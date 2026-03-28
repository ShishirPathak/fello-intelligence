# Persona inference agent that predicts likely visitor role from browsing behavior.
from __future__ import annotations

import json
import os
import re
from typing import Any

from openai import AsyncOpenAI

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


async def infer_persona(
    pages: list[str],
    dwell_time: int,
    visit_count: int,
) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "likely_role": "Unknown",
            "confidence": 0.0,
            "reasoning": "OPENAI_API_KEY is not configured.",
        }

    client = AsyncOpenAI(api_key=api_key)
    system_prompt = (
        "You are a B2B sales intelligence assistant specializing in real estate and "
        "mortgage technology. Given a list of pages a visitor browsed on a SaaS "
        "platform, infer the most likely job role of the visitor. Consider: pricing "
        "pages suggest budget owners or decision makers, documentation suggests "
        "technical evaluators, case studies suggest business evaluators, blog content "
        "suggests researchers. Return valid JSON only."
    )
    user_prompt = (
        "This visitor browsed these pages on a real estate AI platform: "
        f"{pages}. They spent {dwell_time} seconds on site and visited {visit_count} "
        "times this week. What is their most likely job role? Return JSON with: "
        "likely_role (string), confidence (float 0-1), reasoning (one sentence)."
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
        return {
            "likely_role": "Unknown",
            "confidence": 0.0,
            "reasoning": "Persona inference failed due to an upstream API error.",
        }

    parsed = _extract_json_object(response.output_text or "")
    if not parsed:
        return {
            "likely_role": "Unknown",
            "confidence": 0.0,
            "reasoning": "Persona inference returned invalid JSON.",
        }

    confidence = parsed.get("confidence")
    try:
        normalized_confidence = max(0.0, min(1.0, float(confidence)))
    except (TypeError, ValueError):
        normalized_confidence = 0.0

    return {
        "likely_role": parsed.get("likely_role") or "Unknown",
        "confidence": normalized_confidence,
        "reasoning": parsed.get("reasoning") or "No reasoning provided.",
    }
