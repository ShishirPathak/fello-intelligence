# Business signals agent that finds recent company signals via Serper and normalizes them with OpenAI.
from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx
from openai import AsyncOpenAI

SERPER_SEARCH_URL = "https://google.serper.dev/search"
OPENAI_MODEL = "gpt-4.1-mini"
SEARCH_QUERIES = (
    ("hiring", "{company_name} hiring 2024 2025"),
    ("funding", "{company_name} funding news announcement"),
    ("growth", "{company_name} expansion growth"),
)


def _extract_json_object(text: str) -> dict[str, Any] | None:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None

    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None

    return parsed if isinstance(parsed, dict) else None


async def _search_serper(company_name: str) -> list[dict[str, Any]]:
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key or not company_name:
        return []

    results: list[dict[str, Any]] = []
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            for signal_type, template in SEARCH_QUERIES:
                response = await client.post(
                    SERPER_SEARCH_URL,
                    headers={
                        "X-API-KEY": api_key,
                        "Content-Type": "application/json",
                    },
                    json={"q": template.format(company_name=company_name)},
                )
                response.raise_for_status()
                payload = response.json()
                organic_results = payload.get("organic") or []
                if organic_results:
                    top_result = organic_results[0]
                    results.append(
                        {
                            "requested_type": signal_type,
                            "title": top_result.get("title"),
                            "snippet": top_result.get("snippet"),
                            "link": top_result.get("link"),
                        }
                    )
    except Exception:
        return []

    return results


async def _extract_signal(result: dict[str, Any]) -> dict[str, Any] | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    client = AsyncOpenAI(api_key=api_key)
    prompt = (
        "From this search result snippet, extract a business signal in under 10 words. "
        "Return JSON: {type: 'hiring'|'funding'|'news'|'growth', label: string, "
        "description: string}. Return only valid JSON."
    )
    user_input = (
        f"Title: {result.get('title')}\n"
        f"Snippet: {result.get('snippet')}\n"
        f"Preferred type: {result.get('requested_type')}"
    )

    try:
        response = await client.responses.create(
            model=OPENAI_MODEL,
            input=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input},
            ],
        )
    except Exception:
        return None

    parsed = _extract_json_object(response.output_text or "")
    if not parsed:
        return None

    signal_type = parsed.get("type") or result.get("requested_type") or "news"
    if signal_type not in {"hiring", "funding", "news", "growth"}:
        signal_type = result.get("requested_type") or "news"

    return {
        "type": signal_type,
        "label": parsed.get("label") or "Recent business activity",
        "description": parsed.get("description") or (result.get("snippet") or ""),
        "source_url": result.get("link"),
    }


async def fetch_business_signals(company_name: str) -> list[dict[str, Any]]:
    search_results = await _search_serper(company_name)
    if not search_results:
        return []

    extracted_signals: list[dict[str, Any]] = []
    for result in search_results:
        signal = await _extract_signal(result)
        if signal:
            extracted_signals.append(signal)

    return extracted_signals[:3]
