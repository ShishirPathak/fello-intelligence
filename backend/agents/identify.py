# IP identification agent that resolves a likely company and geo context from ipinfo.io.
from __future__ import annotations

import os
import re
from typing import Any

import httpx

IPINFO_URL_TEMPLATE = "https://ipinfo.io/{ip}/json"
RESIDENTIAL_ISP_KEYWORDS = (
    "comcast",
    "at&t",
    "verizon",
    "t-mobile",
    "charter",
    "cox",
    "spectrum",
    "centurylink",
    "nordvpn",
    "expressvpn",
)
CLOUD_PROVIDER_KEYWORDS = (
    "amazon",
    "amazon.com",
    "aws",
    "google cloud",
    "google llc",
    "microsoft",
    "azure",
    "digitalocean",
    "linode",
    "cloudflare",
    "akamai",
    "oracle cloud",
    "alibaba cloud",
)
AS_PREFIX_PATTERN = re.compile(r"^AS\d+\s+", re.IGNORECASE)


def _clean_org_name(org_value: str | None) -> str | None:
    if not org_value:
        return None

    cleaned = AS_PREFIX_PATTERN.sub("", org_value).strip(" -")
    return cleaned or None


def _is_residential_isp(org_value: str | None) -> bool:
    if not org_value:
        return False

    normalized = org_value.lower()
    return any(keyword in normalized for keyword in RESIDENTIAL_ISP_KEYWORDS)


def _is_cloud_provider(org_value: str | None) -> bool:
    if not org_value:
        return False

    normalized = org_value.lower()
    return any(keyword in normalized for keyword in CLOUD_PROVIDER_KEYWORDS)


def _guess_domain(company_name: str | None) -> str | None:
    if not company_name:
        return None

    normalized = re.sub(r"[^a-z0-9]+", "", company_name.lower())
    if not normalized:
        return None

    return f"{normalized}.com"


async def identify_company_from_ip(ip: str) -> dict[str, Any]:
    token = os.getenv("IPINFO_TOKEN")
    if not token:
        return {
            "resolved": False,
            "confidence": 0.0,
            "reason": "IPINFO_TOKEN is not configured",
            "company_name": None,
            "domain": None,
            "city": None,
            "region": None,
            "country": None,
        }

    url = IPINFO_URL_TEMPLATE.format(ip=ip)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params={"token": token})
            response.raise_for_status()
            payload = response.json()
    except Exception:
        return {
            "resolved": False,
            "confidence": 0.0,
            "reason": "Failed to fetch IP intelligence",
            "company_name": None,
            "domain": None,
            "city": None,
            "region": None,
            "country": None,
        }

    org_value = payload.get("org")
    city = payload.get("city")
    region = payload.get("region")
    country = payload.get("country")

    if _is_residential_isp(org_value):
        return {
            "resolved": False,
            "confidence": 0.1,
            "reason": "Residential ISP detected",
            "company_name": None,
            "domain": None,
            "city": city,
            "region": region,
            "country": country,
        }

    if _is_cloud_provider(org_value):
        return {
            "resolved": False,
            "confidence": 0.15,
            "reason": "Cloud infrastructure IP detected",
            "company_name": None,
            "domain": None,
            "city": city,
            "region": region,
            "country": country,
        }

    company_name = _clean_org_name(org_value)
    if not company_name:
        return {
            "resolved": False,
            "confidence": 0.0,
            "reason": "No company organization found for IP",
            "company_name": None,
            "domain": None,
            "city": city,
            "region": region,
            "country": country,
        }

    return {
        "resolved": True,
        "confidence": 0.75,
        "reason": None,
        "company_name": company_name,
        "domain": _guess_domain(company_name),
        "city": city,
        "region": region,
        "country": country,
    }
