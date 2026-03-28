# Synthesis agent that turns account intelligence inputs into a summary and recommended next actions.
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


def _fallback_actions(company_name: str | None, intent_stage: str | None) -> list[str]:
    account_name = company_name or "this account"
    stage = intent_stage or "awareness"
    return [
        f"Research {account_name} and confirm current real estate or mortgage motion.",
        f"Send a tailored outbound message aligned to the {stage} stage.",
        f"Attempt to identify the buyer group and route to the right AE.",
    ]


async def synthesize_account_intelligence(
    company_data: dict[str, Any],
    intent_score: float | None,
    intent_stage: str | None,
    persona: dict[str, Any] | None,
    signals: list[str],
    business_signals: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    company_name = company_data.get("company_name") or company_data.get("name")

    if not api_key:
        return {
            "ai_summary": (
                f"{company_name or 'This account'} shows {intent_stage or 'early'} buyer "
                "interest based on recent site behavior, but AI synthesis is unavailable "
                "because OPENAI_API_KEY is not configured."
            ),
            "recommended_actions": _fallback_actions(company_name, intent_stage),
        }

    client = AsyncOpenAI(api_key=api_key)
    system_prompt = (
        "You are a senior sales intelligence analyst for Fello, a real estate and "
        "mortgage AI platform. Your job is to generate concise, actionable account "
        "summaries for the sales team. Be specific, professional, and focus on why this "
        "company is a good fit for Fello's AI sales automation tools. Always tailor "
        "recommendations to the real estate and mortgage industry context. Return valid "
        "JSON only."
    )
    user_prompt = (
        "Generate a sales intelligence summary for this account:\n\n"
        f"Company: {company_data}\n"
        f"Visitor intent score: {intent_score}/10\n"
        f"Intent stage: {intent_stage}\n"
        f"Likely visitor persona: {persona}\n"
        f"Key signals: {signals}\n"
        f"Business signals: {business_signals}\n\n"
        "Return JSON with:\n"
        "- ai_summary: 2-3 sentence paragraph about the company and why they visited\n"
        "- recommended_actions: array of exactly 3 specific, actionable strings for the sales team"
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
            "ai_summary": (
                f"{company_name or 'This account'} appears to be in the "
                f"{intent_stage or 'awareness'} stage based on observed visitor behavior. "
                "The account warrants follow-up, but AI synthesis was unavailable."
            ),
            "recommended_actions": _fallback_actions(company_name, intent_stage),
        }

    parsed = _extract_json_object(response.output_text or "")
    if not parsed:
        return {
            "ai_summary": (
                f"{company_name or 'This account'} has usable enrichment and intent data, "
                "but the synthesis output could not be parsed into structured JSON."
            ),
            "recommended_actions": _fallback_actions(company_name, intent_stage),
        }

    recommended_actions = parsed.get("recommended_actions")
    if not isinstance(recommended_actions, list):
        recommended_actions = _fallback_actions(company_name, intent_stage)

    normalized_actions = [
        str(action).strip() for action in recommended_actions if str(action).strip()
    ][:3]
    while len(normalized_actions) < 3:
        normalized_actions.append(
            _fallback_actions(company_name, intent_stage)[len(normalized_actions)],
        )

    return {
        "ai_summary": parsed.get("ai_summary")
        or f"{company_name or 'This account'} shows measurable sales interest.",
        "recommended_actions": normalized_actions,
    }
