# Intent scoring agent that converts visitor behavior into a score, stage, and supporting signals.
from __future__ import annotations

from typing import Any

HIGH_INTENT_PAGES = {
    "/pricing",
    "/plans",
    "/buy",
    "/demo",
    "/get-started",
}
MID_INTENT_PAGES = {
    "/case-studies",
    "/features",
    "/ai-sales-agent",
    "/product",
}
LOW_INTENT_PAGES = {
    "/blog",
    "/about",
    "/careers",
    "/team",
}


def _normalize_page(page: str) -> str:
    return page.strip().lower()


def score_intent(
    pages: list[str],
    time_on_site_seconds: int,
    visits_this_week: int,
) -> dict[str, Any]:
    score = 0.0
    signals: list[str] = []

    for raw_page in pages:
        page = _normalize_page(raw_page)
        if page in HIGH_INTENT_PAGES:
            score += 2.5
            signals.append(f"Visited high-intent page {page} (+2.5)")
        elif page in MID_INTENT_PAGES:
            score += 1.5
            signals.append(f"Visited mid-intent page {page} (+1.5)")
        elif page in LOW_INTENT_PAGES:
            score += 0.5
            signals.append(f"Visited low-intent page {page} (+0.5)")

    if time_on_site_seconds > 300:
        score += 2.0
        signals.append("Spent over 300 seconds on site (+2.0)")
    elif 120 <= time_on_site_seconds <= 300:
        score += 1.5
        signals.append("Spent 120 to 300 seconds on site (+1.5)")
    elif 60 <= time_on_site_seconds < 120:
        score += 0.5
        signals.append("Spent 60 to 119 seconds on site (+0.5)")

    if visits_this_week >= 4:
        score += 2.5
        signals.append("Visited 4 or more times this week (+2.5)")
    elif visits_this_week == 3:
        score += 2.0
        signals.append("Visited 3 times this week (+2.0)")
    elif visits_this_week == 2:
        score += 1.0
        signals.append("Visited 2 times this week (+1.0)")

    final_score = min(round(score, 1), 10.0)
    if final_score >= 7.0:
        stage = "decision"
    elif final_score >= 4.0:
        stage = "evaluation"
    else:
        stage = "awareness"

    if not signals:
        signals.append("Limited behavioral signals available")

    return {
        "score": final_score,
        "stage": stage,
        "signals": signals,
    }
