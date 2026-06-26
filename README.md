# Deck Analyzer

> Public engineering showcase of a private production codebase. The product, prompts and domain logic are intentionally left undescribed here — this repository exists only to demonstrate engineering practice, through one sanitized code sample. No secrets, no data.

## Stack

| Layer            | Tools                                                                              |
| ---------------- | --------------------------------------------------------------------------------- |
| Frontend         | Streamlit (Python), custom CSS/JS                                                  |
| Backend          | Python                                                                             |
| AI               | Anthropic Claude (Opus / Sonnet / Haiku) with prompt caching · per-task model router · OpenAI Whisper |
| Infra            | Render (Infrastructure-as-Code, EU) · Cloudflare (WAF) · Sentry                    |
| Security / Auth  | bcrypt · PII-redacting logger                                                      |
| CI/CD            | GitHub Actions — pytest · ruff · Playwright                                        |

## Code sample

[`code-sample/model_router.py`](code-sample/model_router.py) — per-task LLM model routing with cache-aware cost accounting, including the prompt-caching price buckets Anthropic bills separately. Task keys and pricing are illustrative.
