# Company enrichment agent that uses Apollo first and falls back to OpenAI-based research.
from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx
from openai import AsyncOpenAI

APOLLO_ENRICH_URL = "https://api.apollo.io/v1/organizations/enrich"
SERPER_SEARCH_URL = "https://google.serper.dev/search"
OPENAI_MODEL = "gpt-4.1-mini"


def _extract_json_object(text: str) -> dict[str, Any] | None:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None

    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None

    return parsed if isinstance(parsed, dict) else None


def _normalize_employee_count(employee_count: Any) -> str | None:
    if employee_count in (None, ""):
        return None
    return str(employee_count)


def _normalize_headquarters(city: Any) -> str | None:
    if city in (None, ""):
        return None
    return str(city)


def _domain_from_website(website_url: str | None) -> str | None:
    if not website_url:
        return None

    cleaned = re.sub(r"^https?://", "", website_url, flags=re.IGNORECASE)
    cleaned = cleaned.split("/")[0].strip().lower()
    return cleaned or None


async def _search_tech_stack(company_name: str, domain: str | None) -> list[dict[str, Any]]:
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key or not company_name:
        return []

    query = (
        f'"{company_name}" tech stack CRM marketing analytics'
        if not domain
        else f'"{company_name}" "{domain}" tech stack CRM marketing analytics'
    )

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                SERPER_SEARCH_URL,
                headers={
                    "X-API-KEY": api_key,
                    "Content-Type": "application/json",
                },
                json={"q": query},
            )
            response.raise_for_status()
            payload = response.json()
    except Exception:
        return []

    organic_results = payload.get("organic") or []
    return organic_results[:5] if isinstance(organic_results, list) else []


async def _infer_tech_stack(company_name: str, domain: str | None) -> dict[str, str] | None:
    search_results = await _search_tech_stack(company_name, domain)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not search_results:
        return None

    client = AsyncOpenAI(api_key=api_key)
    snippets = "\n\n".join(
        (
            f"Title: {result.get('title')}\n"
            f"Snippet: {result.get('snippet')}\n"
            f"Link: {result.get('link')}"
        )
        for result in search_results
    )
    system_prompt = (
        "You extract probable B2B software tools from web search snippets. "
        "Return valid JSON only with keys: crm, marketing, analytics. "
        "Use a short vendor/product name when reasonably supported by the snippets. "
        "If uncertain, return null for that field."
    )
    user_prompt = (
        f"Company: {company_name}\n"
        f"Domain: {domain}\n"
        f"Search evidence:\n{snippets}"
    )

    try:
        response = await client.responses.create(
            model=OPENAI_MODEL,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
    except Exception:
        return None

    parsed = _extract_json_object(response.output_text or "")
    if not parsed:
        return None

    tech_stack = {
        "crm": parsed.get("crm"),
        "marketing": parsed.get("marketing"),
        "analytics": parsed.get("analytics"),
    }
    return tech_stack if any(tech_stack.values()) else None


async def _enrich_with_apollo(domain: str) -> dict[str, Any] | None:
    api_key = os.getenv("APOLLO_API_KEY")
    if not api_key or not domain:
        return None

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                APOLLO_ENRICH_URL,
                headers={"x-api-key": api_key, "Content-Type": "application/json"},
                json={"domain": domain},
            )
            response.raise_for_status()
            payload = response.json()
    except Exception:
        return None

    organization = payload.get("organization") or payload.get("account") or payload
    if not isinstance(organization, dict):
        return None

    name = organization.get("name")
    website_url = organization.get("website_url") or organization.get("website")
    result = {
        "company_name": name,
        "domain": _domain_from_website(website_url) or domain,
        "industry": organization.get("industry"),
        "company_size": _normalize_employee_count(
            organization.get("estimated_num_employees"),
        ),
        "headquarters": _normalize_headquarters(organization.get("city")),
        "founded_year": (
            str(organization.get("founded_year"))
            if organization.get("founded_year")
            else None
        ),
        "website": website_url,
        "linkedin_url": organization.get("linkedin_url"),
        "short_description": organization.get("short_description"),
        "confidence": 0.6,
        "source": "apollo",
    }

    if not any(result.get(field) for field in ("company_name", "industry", "website")):
        return None

    return result


async def _enrich_with_openai(company_name: str) -> dict[str, Any] | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not company_name:
        return None

    client = AsyncOpenAI(api_key=api_key)
    system_prompt = (
        "You are a company research assistant. Given a company name, return structured "
        "JSON with: name, industry, estimated_employee_count, headquarters_city, "
        "founded_year, website_domain, one_line_description. Return ONLY valid JSON, "
        "no markdown, no extra text."
    )

    try:
        response = await client.responses.create(
            model=OPENAI_MODEL,
            input=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Research this company: {company_name}",
                },
            ],
        )
    except Exception:
        return None

    parsed = _extract_json_object(response.output_text or "")
    if not parsed:
        return None

    return {
        "company_name": parsed.get("name") or company_name,
        "domain": parsed.get("website_domain"),
        "industry": parsed.get("industry"),
        "company_size": _normalize_employee_count(parsed.get("estimated_employee_count")),
        "headquarters": _normalize_headquarters(parsed.get("headquarters_city")),
        "founded_year": (
            str(parsed.get("founded_year")) if parsed.get("founded_year") else None
        ),
        "website": (
            f"https://{parsed.get('website_domain')}"
            if parsed.get("website_domain")
            else None
        ),
        "linkedin_url": None,
        "short_description": parsed.get("one_line_description"),
        "confidence": 0.45,
        "source": "openai_research",
    }


async def enrich_company(
    company_name: str | None = None,
    domain: str | None = None,
) -> dict[str, Any]:
    normalized_domain = (domain or "").strip().lower() or None
    normalized_name = (company_name or "").strip() or None

    apollo_result = await _enrich_with_apollo(normalized_domain or "")
    if apollo_result:
        if not apollo_result.get("company_name") and normalized_name:
            apollo_result["company_name"] = normalized_name
        apollo_result["tech_stack"] = await _infer_tech_stack(
            apollo_result.get("company_name") or normalized_name or "",
            apollo_result.get("domain") or normalized_domain,
        )
        return apollo_result

    openai_result = await _enrich_with_openai(normalized_name or "")
    if openai_result:
        if not openai_result.get("domain") and normalized_domain:
            openai_result["domain"] = normalized_domain
        openai_result["tech_stack"] = await _infer_tech_stack(
            openai_result.get("company_name") or normalized_name or "",
            openai_result.get("domain") or normalized_domain,
        )
        return openai_result

    return {
        "company_name": normalized_name,
        "domain": normalized_domain,
        "industry": None,
        "company_size": None,
        "headquarters": None,
        "founded_year": None,
        "website": f"https://{normalized_domain}" if normalized_domain else None,
        "linkedin_url": None,
        "short_description": None,
        "tech_stack": None,
        "confidence": 0.0,
        "source": "unavailable",
    }
