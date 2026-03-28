# Shared Pydantic models for Fello Intelligence API requests and responses.
from __future__ import annotations

from pydantic import BaseModel, Field


class VisitorInput(BaseModel):
    ip: str
    pages: list[str]
    time_on_site_seconds: int
    visits_this_week: int
    referral_source: str | None = None


class CompanyBatchInput(BaseModel):
    companies: list[str] = Field(default_factory=list)


class AccountIntelligence(BaseModel):
    status: str
    confidence: float
    company_name: str | None = None
    domain: str | None = None
    industry: str | None = None
    company_size: str | None = None
    headquarters: str | None = None
    founded_year: str | None = None
    website: str | None = None
    likely_persona: str | None = None
    persona_confidence: float | None = None
    persona_reasoning: str | None = None
    intent_score: float | None = None
    intent_stage: str | None = None
    intent_signals: list[str] = Field(default_factory=list)
    tech_stack: dict | None = None
    business_signals: list[dict] | None = None
    key_leaders: list[dict] | None = None
    ai_summary: str | None = None
    recommended_actions: list[str] = Field(default_factory=list)
    unresolved_reason: str | None = None
