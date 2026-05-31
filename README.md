# Deck Analyzer

An AI decision-support tool that turns a pitch deck and founder-call notes into a structured investment verdict. Built for angel networks and funds — each tenant gets its own thesis, scoring weights, and thresholds.

> Multi-tenant SaaS (Streamlit + Claude), deployed in the EU. This repository is a **public engineering showcase** — the proprietary prompts, scoring doctrine, and client data live in a private repo and are intentionally excluded.

## Key features

- **Screening verdict** — from a PDF and pasted call notes, a 3-zone decision (skip / look / proceed) on a transparent /20 grid.
- **One product, many theses** — each network plugs in its own scoring weights, sector exclusions, and thresholds without code changes.
- **Cost-aware** — per-task model routing and prompt caching, tracked per tenant.
- **Privacy-first** — decks, audio, and notes are processed in memory and purged on logout; logs keep metadata, not content.
- **Two modes** — upstream screening, and full post-call analysis with 4-axis scoring.

## Architecture

```mermaid
flowchart TD
    User([Investor / sourcer])
    User -->|HTTPS| CF[Cloudflare edge<br/>WAF · rate limit · TLS · security headers]
    CF --> Render

    subgraph Render["Render — EU region · IaC blueprint · always-on"]
        Entry[entry.py<br/>ASGI header injection] --> Router[app.py router ~200 LOC]
        Router --> Auth[Multi-tenant auth<br/>bcrypt · timing-safe]
        Auth --> Pages[Pages: screening · memo · batch · compare]
        Pages --> Svc[LLM orchestration]

        Svc --> Safety[Prompt-injection defense<br/>XML envelope · audit log]
        Safety --> Cache[Prompt cache<br/>ephemeral 5-min TTL]
        Cache --> RouterLLM{Model router<br/>by task}
    end

    RouterLLM -->|dense memos| Opus[Claude Opus]
    RouterLLM -->|fast screening| Sonnet[Claude Sonnet]
    RouterLLM -->|OCR / extraction| Haiku[Claude Haiku]
    Pages -->|audio notes| Whisper[OpenAI Whisper]

    Opus --> Track[Budget tracker<br/>atomic, per-tenant]
    Sonnet --> Track
    Haiku --> Track
    Track --> Logs[(Safe logger<br/>PII redaction)]
    Logs --> Sentry[Sentry telemetry]
    Track --> Admin[Admin dashboard]

    classDef ext fill:#eef,stroke:#557;
    class Opus,Sonnet,Haiku,Whisper,Sentry,CF ext;
```

Tenant data is isolated per client and per member via namespaced session keys (`client::member::key`).

## Tech stack

| Layer | Tools |
|---|---|
| **Frontend** | Streamlit (Python), custom CSS/JS |
| **Backend** | Python |
| **AI** | Anthropic Claude (Opus / Sonnet / Haiku) with prompt caching · OpenAI Whisper · per-task model router |
| **Infra** | Render (Infrastructure-as-Code, EU region) · Cloudflare (WAF + edge security headers) · Sentry |
| **Security / Auth** | bcrypt · prompt-injection envelope · PII-redacting logger |
| **CI/CD** | GitHub Actions — pytest · ruff · Playwright |
| **Other** | reportlab (PDF export) |

## Highlights

- **Multi-tenant isolation** — every business-data session key is namespaced `client::member::key`, so one tenant's data isn't reachable from another's namespace.
- **Per-task LLM routing + caching** — Opus / Sonnet / Haiku chosen per task, with cache-aware cost accounting. See [`code-sample/model_router.py`](code-sample/model_router.py).
- **Prompt-injection handling** — user input is wrapped in whitelisted XML envelopes with tag-escaping, and a defense preamble leads each system prompt.
- **Privacy by design** — no raw decks/audio/notes written to disk; PII redaction in logs; EU hosting.

## Contact

[hippolyte.dupac@gmail.com](mailto:hippolyte.dupac@gmail.com)

## License

The showcased product is proprietary. This repository exists to demonstrate engineering practices; the single code sample is a sanitized excerpt published for that purpose.
