# Fello Intelligence Project Documentation

## 1. Purpose

Fello Intelligence is an AI-assisted account intelligence system created for the Fello AI Builder Hackathon. Its purpose is to help Fello's sales team convert anonymous or semi-anonymous website traffic into actionable sales intelligence.

The system accepts either:

- visitor signals such as IP address, visited pages, time on site, and visit frequency
- a batch of company names for direct enrichment

It returns a structured account intelligence object that can power a sales dashboard and guide outbound follow-up.

## 2. Business Use Case

Fello sells AI solutions for real estate and mortgage businesses. The sales problem is that website traffic by itself is noisy:

- many visitors are anonymous
- IP ownership is often unreliable
- even when a company can be identified, the sales team still needs context
- sellers need to know who visited, why they likely visited, how serious they are, and what to do next

This project turns that messy signal into:

- likely company identity
- firmographic enrichment
- inferred buyer persona
- intent score and stage
- current business signals
- probable tech stack
- AI-written summary
- concrete sales actions

## 3. Primary User Flows

### 3.1 Visitor Signal Flow

This is the main use case for the demo.

1. A user enters visitor details in the dashboard.
2. The frontend sends the payload to `POST /analyze`.
3. The backend identifies the company from IP.
4. If the visitor is unresolved, the pipeline exits cleanly with an unresolved response.
5. If resolved, the backend enriches the company profile, scores intent, infers persona, searches business signals, and synthesizes a final summary.
6. The frontend renders the result as an account intelligence card.

### 3.2 Company List Flow

This is a direct enrichment mode.

1. A user enters one company name per line.
2. The frontend sends the names to `POST /enrich-batch`.
3. The backend enriches each company sequentially.
4. The frontend currently shows the first returned result.

## 4. High-Level Architecture

```text
Frontend (React + Tailwind)
        |
        v
FastAPI Backend
        |
        +--> Identify Agent      -> ipinfo
        +--> Enrich Agent        -> Apollo + OpenAI fallback + Serper/OpenAI tech stack
        +--> Intent Agent        -> local rule engine
        +--> Persona Agent       -> OpenAI
        +--> Signals Agent       -> Serper + OpenAI
        +--> Synthesis Agent     -> OpenAI
        |
        +--> Cache Layer         -> Redis or in-memory fallback
```

## 5. Repository Structure

```text
fello-intelligence/
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── cache.py
│   └── agents/
│       ├── __init__.py
│       ├── identify.py
│       ├── enrich.py
│       ├── intent.py
│       ├── persona.py
│       ├── synthesize.py
│       └── signals.py
├── frontend/
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.js
│   ├── postcss.config.js
│   ├── index.html
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       ├── styles.css
│       └── components/
│           ├── InputPanel.jsx
│           ├── AccountCard.jsx
│           ├── IntentBadge.jsx
│           ├── PersonaCard.jsx
│           ├── ActionsCard.jsx
│           ├── TechStack.jsx
│           ├── BusinessSignals.jsx
│           └── UnresolvedCard.jsx
├── mock_data/
│   └── visitors.json
├── docs/
│   └── PROJECT_DOCUMENTATION.md
├── .env.example
├── requirements.txt
└── README.md
```

## 6. Backend Flow: From Request to Response

### 6.1 Entry Point

The backend entry point is [`backend/main.py`](../backend/main.py).

Key responsibilities:

- load environment variables with `python-dotenv`
- create the FastAPI app
- enable CORS for local frontend origins
- expose `/health`, `/analyze`, and `/enrich-batch`
- orchestrate the agents

### 6.2 Analyze Flow

When `POST /analyze` is called:

1. The request body is validated against `VisitorInput`.
2. The backend checks whether the IP matches a demo record from `mock_data/visitors.json`.
3. If a mock match exists, the system resolves using mock company data.
4. If no mock match exists, the backend calls the identify agent.
5. If the visitor is unresolved, the backend returns an unresolved `AccountIntelligence`.
6. If resolved, the backend checks the cache using the company domain.
7. On a cache hit:
   - the backend skips company enrichment
   - intent and persona are still recomputed because they depend on current visitor behavior
   - synthesis is regenerated
8. On a cache miss:
   - enrichment runs
   - business signal search runs
   - intent scoring runs
   - persona inference runs
   - synthesis runs last
9. The profile is cached by domain.
10. The response is returned as `AccountIntelligence`.

### 6.3 Batch Enrichment Flow

When `POST /enrich-batch` is called:

1. The payload is validated against `CompanyBatchInput`.
2. The backend loops through each company name.
3. Each company is enriched individually.
4. Business signals are fetched.
5. Synthesis is generated.
6. The endpoint returns a list of `AccountIntelligence` objects.

## 7. Data Model Layer

The shared request and response models are in [`backend/models.py`](../backend/models.py).

### 7.1 Input Model

`VisitorInput` represents raw website activity:

- `ip`
- `pages`
- `time_on_site_seconds`
- `visits_this_week`
- optional `referral_source`

### 7.2 Output Model

`AccountIntelligence` is the central response object and contains:

- resolution status
- confidence
- company identity
- firmographics
- persona
- intent
- business signals
- tech stack
- leaders
- AI summary
- recommended actions
- unresolved reason

This shape is intentionally broad so the frontend can render one result card regardless of how much upstream data was available.

## 8. Agent-by-Agent Implementation

### 8.1 Identify Agent

File: [`backend/agents/identify.py`](../backend/agents/identify.py)

Responsibilities:

- call `ipinfo.io`
- inspect the `org` field
- reject residential ISP traffic
- reject cloud-infrastructure traffic such as AWS and similar providers
- extract geo context
- produce a probable company and domain guess

Why this matters:

IP ownership is often misleading. Residential traffic and cloud-provider IPs should not become fake target accounts. This is why the agent explicitly rejects those categories.

### 8.2 Enrich Agent

File: [`backend/agents/enrich.py`](../backend/agents/enrich.py)

Responsibilities:

- call Apollo organization enrichment by domain
- normalize the Apollo response
- fall back to OpenAI-based company research if Apollo is unavailable or empty
- infer probable `tech_stack` using Serper snippets plus OpenAI extraction

This agent is the main source of:

- company identity refinement
- industry
- company size
- headquarters
- founded year
- website
- short description
- tech stack

### 8.3 Intent Agent

File: [`backend/agents/intent.py`](../backend/agents/intent.py)

This is a pure rules engine.

Inputs:

- visited pages
- dwell time
- visits this week

Outputs:

- `score`
- `stage`
- `signals`

Stages:

- `awareness`
- `evaluation`
- `decision`

This is deliberately deterministic so intent remains explainable in a demo.

### 8.4 Persona Agent

File: [`backend/agents/persona.py`](../backend/agents/persona.py)

Responsibilities:

- use OpenAI to infer the likely role behind the browsing behavior
- return JSON with role, confidence, and reasoning

The role is not claimed as ground truth. It is a high-confidence hypothesis for sales use.

### 8.5 Signals Agent

File: [`backend/agents/signals.py`](../backend/agents/signals.py)

Responsibilities:

- search recent public signals with Serper
- search themes:
  - hiring
  - funding
  - expansion/growth
- normalize snippets into concise signal objects with OpenAI

This gives the sales team recent external context beyond the company profile alone.

### 8.6 Synthesis Agent

File: [`backend/agents/synthesize.py`](../backend/agents/synthesize.py)

Responsibilities:

- combine company profile, persona, intent, and signals
- produce:
  - `ai_summary`
  - `recommended_actions`

The summary is meant to answer:

- why did this account likely visit
- why is it relevant to Fello
- what should sales do next

### 8.7 Cache Layer

File: [`backend/cache.py`](../backend/cache.py)

Responsibilities:

- cache company-level enrichment by domain for 24 hours
- use Redis when `REDIS_URL` is configured
- fall back to in-memory cache when Redis is absent

This reduces repeat calls to Apollo and other enrichment logic for the same domain.

## 9. Frontend Flow

### 9.1 Entry Point

Files:

- [`frontend/src/main.jsx`](../frontend/src/main.jsx)
- [`frontend/src/App.jsx`](../frontend/src/App.jsx)

The frontend:

- mounts the React app
- loads Tailwind styles
- stores current input state
- calls backend endpoints
- manages UI states:
  - empty
  - loading
  - result
  - unresolved

### 9.2 Input Panel

File: [`frontend/src/components/InputPanel.jsx`](../frontend/src/components/InputPanel.jsx)

Responsibilities:

- choose between visitor mode and company mode
- collect input
- trigger analysis
- reset state
- present mock recent visitors for quick demo clicks

### 9.3 Result Rendering

Main result components:

- [`frontend/src/components/AccountCard.jsx`](../frontend/src/components/AccountCard.jsx)
- [`frontend/src/components/PersonaCard.jsx`](../frontend/src/components/PersonaCard.jsx)
- [`frontend/src/components/ActionsCard.jsx`](../frontend/src/components/ActionsCard.jsx)
- [`frontend/src/components/BusinessSignals.jsx`](../frontend/src/components/BusinessSignals.jsx)
- [`frontend/src/components/TechStack.jsx`](../frontend/src/components/TechStack.jsx)
- [`frontend/src/components/UnresolvedCard.jsx`](../frontend/src/components/UnresolvedCard.jsx)

The frontend does not generate business logic. It renders backend decisions.

## 10. Mock Data Strategy

File: [`mock_data/visitors.json`](../mock_data/visitors.json)

Purpose:

- make the demo stable even when IP intelligence is noisy
- avoid AWS/public cloud IPs becoming fake companies
- provide reliable visitor examples for the frontend queue

Backend behavior:

- if the incoming IP matches a mock visitor
- and `mock_resolved` is true
- the backend resolves the visitor using `mock_company`

This makes the demo much more predictable than raw live IP lookup.

## 11. External Services and What They Contribute

### OpenAI

Used for:

- company research fallback
- persona inference
- signal normalization
- final synthesis
- tech-stack inference

### ipinfo

Used for:

- IP to organization lookup
- geo context

### Apollo

Used for:

- structured company enrichment by domain

### Serper

Used for:

- public search snippets
- business signals retrieval
- tech-stack evidence gathering

### Redis / Upstash

Used for:

- company profile caching

## 12. Why Some Fields May Be Empty

### `tech_stack`

May be empty when:

- Serper returns weak evidence
- OpenAI cannot confidently infer tools
- the cached profile was created before stronger inference existed

### `business_signals`

May be empty when:

- no useful recent public search evidence exists
- OpenAI extraction rejects weak snippets

### `key_leaders`

This field exists in the response model but is not fully implemented in the current backend enrichment flow, so it may remain null.

## 13. Error Handling Philosophy

This system is designed to degrade gracefully.

Principles:

- never crash the whole pipeline because one agent failed
- return partial data whenever possible
- use confidence scores to show uncertainty
- keep unresolved visitors as a first-class state, not an error

Examples:

- if OpenAI fails, deterministic intent scoring still works
- if Apollo fails, OpenAI company research can still provide fallback enrichment
- if Redis is unavailable, in-memory cache is used
- if IP identification fails, the unresolved response is returned cleanly

## 14. Demo Walkthrough

Recommended flow:

1. Open the dashboard.
2. Click a mock visitor from the recent visitors queue.
3. Let the system show loading.
4. Show the resolved account card.
5. Explain:
   - how the company was identified
   - why the buyer looks high or medium intent
   - what persona the model inferred
   - what signals support outreach
   - what actions sales should take

Then click the unresolved visitor to demonstrate graceful fallback for anonymous residential traffic.

## 15. Current Limitations

- IP intelligence is inherently noisy.
- Search-based inference is only as good as public web evidence.
- Tech stack and leaders are still the weakest fields.
- Batch mode currently only shows the first result in the UI.
- The frontend is demo-oriented, not production-hardened.

## 16. Recommended Next Improvements

Short-term:

- add explicit `key_leaders` enrichment
- refresh cache automatically when sparse profiles are detected
- improve tech-stack evidence retrieval queries
- show all batch results in the frontend

Medium-term:

- CRM sync
- real-time visitor monitoring
- account history timeline
- contact enrichment
- vector memory for account research

## 17. Summary

The system is built as a layered intelligence pipeline:

1. identify the account
2. enrich the company
3. score intent
4. infer persona
5. gather external signals
6. synthesize a sales-ready summary

The implementation is intentionally hackathon-pragmatic:

- deterministic where explainability matters
- AI where synthesis and inference help most
- cached where external calls are expensive
- demo-safe where live IP data is unreliable
