# FastAPI application that orchestrates identification, enrichment, scoring, caching, and synthesis.
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

if __package__:
    from .agents.enrich import enrich_company
    from .agents.identify import identify_company_from_ip
    from .agents.intent import score_intent
    from .agents.persona import infer_persona
    from .agents.signals import fetch_business_signals
    from .agents.synthesize import synthesize_account_intelligence
    from .cache import get_cached_profile, set_cached_profile
    from .models import AccountIntelligence, CompanyBatchInput, VisitorInput
else:
    from agents.enrich import enrich_company
    from agents.identify import identify_company_from_ip
    from agents.intent import score_intent
    from agents.persona import infer_persona
    from agents.signals import fetch_business_signals
    from agents.synthesize import synthesize_account_intelligence
    from cache import get_cached_profile, set_cached_profile
    from models import AccountIntelligence, CompanyBatchInput, VisitorInput

load_dotenv()

app = FastAPI(title="Fello Intelligence API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_MOCK_VISITOR_FILE = Path(__file__).resolve().parent.parent / "mock_data" / "visitors.json"


def _load_mock_visitors() -> list[dict[str, Any]]:
    try:
        with _MOCK_VISITOR_FILE.open("r", encoding="utf-8") as file:
            payload = json.load(file)
    except Exception:
        return []

    return payload if isinstance(payload, list) else []


def _mock_identify_result(ip: str) -> dict[str, Any] | None:
    for visitor in _load_mock_visitors():
        if visitor.get("ip") != ip:
            continue

        if visitor.get("mock_resolved"):
            company_name = visitor.get("mock_company") or visitor.get("label")
            normalized = "".join(ch for ch in (company_name or "").lower() if ch.isalnum())
            return {
                "resolved": True,
                "confidence": 0.95,
                "reason": "Resolved from demo mock data",
                "company_name": company_name,
                "domain": f"{normalized}.com" if normalized else None,
                "city": None,
                "region": None,
                "country": None,
            }

        return {
            "resolved": False,
            "confidence": 0.1,
            "reason": "Residential ISP detected",
            "company_name": None,
            "domain": None,
            "city": None,
            "region": None,
            "country": None,
        }

    return None


def _combine_confidence(*values: float | None) -> float:
    numeric_values = [float(value) for value in values if value is not None]
    if not numeric_values:
        return 0.0
    return round(sum(numeric_values) / len(numeric_values), 2)


def _headquarters_from_identify(identify_result: dict[str, Any]) -> str | None:
    parts = [
        identify_result.get("city"),
        identify_result.get("region"),
        identify_result.get("country"),
    ]
    resolved_parts = [part for part in parts if part]
    return ", ".join(resolved_parts) if resolved_parts else None


def _profile_payload(
    identify_result: dict[str, Any],
    enrichment_result: dict[str, Any],
    business_signals: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "company_name": enrichment_result.get("company_name")
        or identify_result.get("company_name"),
        "domain": enrichment_result.get("domain") or identify_result.get("domain"),
        "industry": enrichment_result.get("industry"),
        "company_size": enrichment_result.get("company_size"),
        "headquarters": enrichment_result.get("headquarters")
        or _headquarters_from_identify(identify_result),
        "founded_year": enrichment_result.get("founded_year"),
        "website": enrichment_result.get("website"),
        "tech_stack": enrichment_result.get("tech_stack"),
        "business_signals": business_signals if business_signals is not None else None,
        "key_leaders": enrichment_result.get("key_leaders"),
        "enrichment_confidence": enrichment_result.get("confidence", 0.0),
        "description": enrichment_result.get("short_description"),
    }


def _build_account_intelligence(
    profile: dict[str, Any],
    identify_result: dict[str, Any] | None,
    intent_result: dict[str, Any] | None,
    persona_result: dict[str, Any] | None,
    synthesis_result: dict[str, Any] | None,
) -> AccountIntelligence:
    return AccountIntelligence(
        status="resolved",
        confidence=_combine_confidence(
            identify_result.get("confidence") if identify_result else None,
            profile.get("enrichment_confidence"),
            persona_result.get("confidence") if persona_result else None,
        ),
        company_name=profile.get("company_name"),
        domain=profile.get("domain"),
        industry=profile.get("industry"),
        company_size=profile.get("company_size"),
        headquarters=profile.get("headquarters"),
        founded_year=profile.get("founded_year"),
        website=profile.get("website"),
        likely_persona=persona_result.get("likely_role") if persona_result else None,
        persona_confidence=persona_result.get("confidence") if persona_result else None,
        persona_reasoning=persona_result.get("reasoning") if persona_result else None,
        intent_score=intent_result.get("score") if intent_result else None,
        intent_stage=intent_result.get("stage") if intent_result else None,
        intent_signals=intent_result.get("signals", []) if intent_result else [],
        tech_stack=profile.get("tech_stack"),
        business_signals=profile.get("business_signals"),
        key_leaders=profile.get("key_leaders"),
        ai_summary=synthesis_result.get("ai_summary") if synthesis_result else None,
        recommended_actions=(
            synthesis_result.get("recommended_actions", []) if synthesis_result else []
        ),
        unresolved_reason=None,
    )


def _build_unresolved_response(identify_result: dict[str, Any]) -> AccountIntelligence:
    return AccountIntelligence(
        status="unresolved",
        confidence=float(identify_result.get("confidence", 0.0)),
        company_name=None,
        domain=None,
        industry=None,
        company_size=None,
        headquarters=_headquarters_from_identify(identify_result),
        founded_year=None,
        website=None,
        likely_persona=None,
        persona_confidence=None,
        persona_reasoning=None,
        intent_score=None,
        intent_stage=None,
        intent_signals=[],
        tech_stack=None,
        business_signals=None,
        key_leaders=None,
        ai_summary=None,
        recommended_actions=[],
        unresolved_reason=identify_result.get("reason"),
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": "1.0.0"}


@app.post("/analyze", response_model=AccountIntelligence)
async def analyze_visitor(visitor: VisitorInput) -> AccountIntelligence:
    identify_result = _mock_identify_result(visitor.ip)
    if identify_result is None:
        identify_result = await identify_company_from_ip(visitor.ip)
    if not identify_result.get("resolved"):
        return _build_unresolved_response(identify_result)

    domain = identify_result.get("domain")
    cached_profile = await get_cached_profile(domain) if domain else None

    intent_task = asyncio.create_task(
        asyncio.to_thread(
            score_intent,
            visitor.pages,
            visitor.time_on_site_seconds,
            visitor.visits_this_week,
        ),
    )
    persona_task = asyncio.create_task(
        infer_persona(
            visitor.pages,
            visitor.time_on_site_seconds,
            visitor.visits_this_week,
        ),
    )

    if cached_profile:
        intent_result, persona_result = await asyncio.gather(intent_task, persona_task)
        synthesis_result = await synthesize_account_intelligence(
            company_data=cached_profile,
            intent_score=intent_result.get("score"),
            intent_stage=intent_result.get("stage"),
            persona=persona_result,
            signals=intent_result.get("signals", []),
            business_signals=cached_profile.get("business_signals"),
        )
        return _build_account_intelligence(
            profile=cached_profile,
            identify_result=identify_result,
            intent_result=intent_result,
            persona_result=persona_result,
            synthesis_result=synthesis_result,
        )

    enrichment_task = asyncio.create_task(
        enrich_company(
            company_name=identify_result.get("company_name"),
            domain=domain,
        ),
    )
    signals_task = asyncio.create_task(
        fetch_business_signals(identify_result.get("company_name") or ""),
    )

    enrichment_result, business_signals, intent_result, persona_result = await asyncio.gather(
        enrichment_task,
        signals_task,
        intent_task,
        persona_task,
    )
    profile = _profile_payload(identify_result, enrichment_result, business_signals)

    synthesis_result = await synthesize_account_intelligence(
        company_data=profile,
        intent_score=intent_result.get("score"),
        intent_stage=intent_result.get("stage"),
        persona=persona_result,
        signals=intent_result.get("signals", []),
        business_signals=business_signals,
    )

    if profile.get("domain"):
        await set_cached_profile(profile["domain"], profile)

    return _build_account_intelligence(
        profile=profile,
        identify_result=identify_result,
        intent_result=intent_result,
        persona_result=persona_result,
        synthesis_result=synthesis_result,
    )


@app.post("/enrich-batch", response_model=list[AccountIntelligence])
async def enrich_batch(payload: CompanyBatchInput) -> list[AccountIntelligence]:
    results: list[AccountIntelligence] = []

    for company_name in payload.companies:
        enrichment_result = await enrich_company(company_name=company_name)
        business_signals = await fetch_business_signals(company_name)
        profile = _profile_payload({}, enrichment_result, business_signals)
        synthesis_result = await synthesize_account_intelligence(
            company_data=profile,
            intent_score=0.0,
            intent_stage="awareness",
            persona=None,
            signals=[],
            business_signals=business_signals,
        )

        results.append(
            AccountIntelligence(
                status="resolved" if profile.get("company_name") or profile.get("domain") else "unresolved",
                confidence=float(profile.get("enrichment_confidence", 0.0)),
                company_name=profile.get("company_name") or company_name,
                domain=profile.get("domain"),
                industry=profile.get("industry"),
                company_size=profile.get("company_size"),
                headquarters=profile.get("headquarters"),
                founded_year=profile.get("founded_year"),
                website=profile.get("website"),
                likely_persona=None,
                persona_confidence=None,
                persona_reasoning=None,
                intent_score=0.0,
                intent_stage="awareness",
                intent_signals=[],
                tech_stack=profile.get("tech_stack"),
                business_signals=business_signals,
                key_leaders=profile.get("key_leaders"),
                ai_summary=synthesis_result.get("ai_summary"),
                recommended_actions=synthesis_result.get("recommended_actions", []),
                unresolved_reason=(
                    None
                    if profile.get("company_name") or profile.get("domain")
                    else "Unable to enrich company"
                ),
            ),
        )

    return results
