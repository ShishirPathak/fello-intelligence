# Fello Intelligence

Fello Intelligence is an AI account intelligence and enrichment system built for the Fello AI Builder Hackathon. It converts anonymous visitor signals or raw company lists into structured sales intelligence cards for Fello's real estate and mortgage sales team.

It combines IP resolution, company enrichment, persona inference, intent scoring, business signal discovery, and AI synthesis into a single FastAPI backend and React dashboard.

Detailed project documentation is available in [docs/PROJECT_DOCUMENTATION.md](/Users/shishirsmac/Personal/fello-intelligence/docs/PROJECT_DOCUMENTATION.md).

## Architecture

```text
                  +----------------------+
                  |   React Dashboard    |
                  |  Visitor or Company  |
                  +----------+-----------+
                             |
                             v
                    +--------+--------+
                    |  FastAPI API    |
                    | /analyze        |
                    | /enrich-batch   |
                    +--------+--------+
                             |
        +--------------------+--------------------+
        |                    |                    |
        v                    v                    v
+---------------+   +----------------+   +----------------+
| Identify Agent |   | Intent Agent  |   | Persona Agent  |
| ipinfo lookup  |   | rules engine  |   | OpenAI API     |
+-------+-------+   +--------+-------+   +--------+-------+
        |                        |                    |
        +-----------+------------+--------------------+
                    |
                    v
         +----------+-----------+
         | Enrich + Signals     |
         | Apollo / OpenAI      |
         | Serper / OpenAI      |
         +----------+-----------+
                    |
                    v
         +----------+-----------+
         | Synthesize Agent     |
         | OpenAI summary       |
         +----------+-----------+
                    |
                    v
             +------+------+
             | Redis Cache |
             | 24h by domain|
             +-------------+
```

## Setup

1. Move into the project:

```bash
cd fello-intelligence
```

2. Install backend dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Configure environment variables:

```bash
cp .env.example .env
```

Fill in:

- `OPENAI_API_KEY`
- `IPINFO_TOKEN`
- `APOLLO_API_KEY`
- `SERPER_API_KEY`
- `REDIS_URL`

4. Run the backend:

```bash
cd backend
uvicorn main:app --reload
```

5. Run the frontend:

```bash
cd frontend
npm install
npm run dev
```

## API

### `GET /health`

```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

### `POST /analyze`

Request:

```json
{
  "ip": "34.201.12.88",
  "pages": ["/pricing", "/ai-sales-agent", "/case-studies"],
  "time_on_site_seconds": 222,
  "visits_this_week": 3
}
```

Example response:

```json
{
  "status": "resolved",
  "confidence": 0.61,
  "company_name": "Keller Williams Chicago North",
  "domain": "kellerwilliamschicagonorth.com",
  "industry": "Real Estate",
  "company_size": "201-500",
  "headquarters": "Chicago, IL, US",
  "founded_year": "1983",
  "website": "https://kellerwilliamschicagonorth.com",
  "likely_persona": "Regional sales leader",
  "persona_confidence": 0.78,
  "persona_reasoning": "Pricing and product pages suggest a business decision maker.",
  "intent_score": 8.5,
  "intent_stage": "decision",
  "intent_signals": [
    "Visited high-intent page /pricing (+2.5)",
    "Visited mid-intent page /ai-sales-agent (+1.5)"
  ],
  "tech_stack": null,
  "business_signals": [],
  "key_leaders": null,
  "ai_summary": "This account appears to be evaluating Fello for brokerage lead conversion workflows.",
  "recommended_actions": [
    "Send a tailored outbound note.",
    "Offer a workflow demo.",
    "Route to the correct AE."
  ],
  "unresolved_reason": null
}
```

### `POST /enrich-batch`

```json
{
  "companies": ["Keller Williams", "loanDepot", "Compass"]
}
```

Returns a list of `AccountIntelligence` objects.

## Agent Overview

- `identify.py`: resolves the likely company behind an IP using `ipinfo.io` and filters residential or VPN traffic.
- `enrich.py`: enriches a company using Apollo first, then falls back to OpenAI-generated research.
- `intent.py`: scores purchase intent from pages visited, dwell time, and repeat visits.
- `persona.py`: infers the likely visitor role from browsing behavior.
- `signals.py`: finds recent hiring, funding, and growth signals with Serper and normalizes them with OpenAI.
- `synthesize.py`: produces the final account summary and recommended sales actions.
- `cache.py`: caches enrichment payloads by domain for 24 hours with Redis or an in-memory fallback.

## Known Limitations

- IP-to-company identification is inherently imperfect and often fails on residential, mobile, or VPN traffic.
- Apollo and search-based enrichment quality depends on the external APIs returning useful data.
- The frontend currently displays the first batch result when multiple companies are submitted in company mode.
- Some output fields such as `tech_stack` and `key_leaders` remain sparse unless provided by upstream enrichment.

## Future Extensions

- CRM sync for Salesforce or HubSpot account creation and activity logging.
- Real-time visitor monitoring with streaming enrichment rather than request-response polling.
- Vector database storage for historical account memory and similarity-based outreach recommendations.
- Contact-level enrichment and champion mapping across leadership teams.
