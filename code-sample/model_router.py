"""Per-task LLM model routing + cache-aware cost accounting.

A small, dependency-free module that picks the right Claude tier for each
task and prices every call — including the prompt-caching buckets Anthropic
bills separately. This is the cost/latency control point of the product.

Routing rationale
-----------------
- High-volume screening (fast pre-filter, latency-critical) -> Sonnet:
  ~3x faster and ~5x cheaper than Opus. Low latency matters because a long
  model call blocks the request thread and degrades the UX (frozen spinner).
- Dense deliverables (memos, final decision write-ups) -> Opus for quality.
- Mechanical tasks (OCR, PDF text extraction) -> Haiku for cost (~80-95%
  cheaper on work that carries no strategic judgment).
- Sonnet also acts as the fallback when Opus is overloaded.

NOTE: This is a sanitized excerpt from a private, production multi-tenant
codebase, published as a code sample. Task keys and pricing are illustrative;
no proprietary prompts, scoring logic, or client data are included.
"""

from __future__ import annotations


MODEL_OPUS: str = "claude-opus-4-7"
MODEL_SONNET: str = "claude-sonnet-4-6"
MODEL_HAIKU: str = "claude-haiku-4-5-20251001"


# Single source of truth: task -> model. Adding a task is a one-line change,
# and `unknown task -> Opus` fails safe toward maximum quality rather than
# silently downgrading.
_TASK_TABLE: dict[str, str] = {
    "deck_screening": MODEL_SONNET,    # high volume, latency-critical
    "investment_memo": MODEL_OPUS,     # dense deliverable, quality-first
    "memo_enrichment": MODEL_OPUS,
    "regeneration": MODEL_OPUS,
    "comparison": MODEL_OPUS,
    "ocr_notes": MODEL_HAIKU,          # mechanical, cost-optimized
    "pdf_extraction": MODEL_HAIKU,
}


# (input USD / Mtok, output USD / Mtok) — public Anthropic list pricing.
_PRICE_USD_PER_MTOK: dict[str, tuple[float, float]] = {
    MODEL_OPUS: (15.0, 75.0),
    MODEL_SONNET: (3.0, 15.0),
    MODEL_HAIKU: (1.0, 5.0),
}


def model_for_task(task: str) -> str:
    """Return the model to use for a given task.

    Unknown task -> Opus (fail-safe toward maximum quality).
    """
    return _TASK_TABLE.get(task, MODEL_OPUS)


def estimated_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimated USD cost for a single call.

    Negative arguments are clamped to zero. An unknown model falls back to
    Opus pricing (the most expensive) so we never *under*-estimate spend.
    """
    input_tokens = max(0, input_tokens)
    output_tokens = max(0, output_tokens)
    price_in, price_out = _PRICE_USD_PER_MTOK.get(model, _PRICE_USD_PER_MTOK[MODEL_OPUS])
    return (input_tokens / 1_000_000.0) * price_in + (output_tokens / 1_000_000.0) * price_out


def estimated_cost_with_cache(
    model: str,
    input_tokens: int,
    output_tokens: int,
    cache_read_tokens: int = 0,
    cache_creation_tokens: int = 0,
) -> float:
    """Cost accounting for prompt caching.

    Anthropic bills three input buckets at different rates:
    - cache creation : 1.25x the normal input price
    - cache read     : 0.10x the normal input price
    - normal input   : full price

    The caller passes the three buckets straight from ``message.usage``,
    so the dashboard reports real spend, not a flat-rate approximation.
    Getting this right is what makes a ~90% cache-hit burst actually show
    up as ~90% savings in the budget tracker.
    """
    price_in, price_out = _PRICE_USD_PER_MTOK.get(model, _PRICE_USD_PER_MTOK[MODEL_OPUS])
    cost = 0.0
    cost += max(0, input_tokens) / 1_000_000.0 * price_in
    cost += max(0, output_tokens) / 1_000_000.0 * price_out
    cost += max(0, cache_creation_tokens) / 1_000_000.0 * price_in * 1.25
    cost += max(0, cache_read_tokens) / 1_000_000.0 * price_in * 0.10
    return cost


def available_models() -> list[str]:
    """Known models (handy for external validation / tests)."""
    return [MODEL_OPUS, MODEL_SONNET, MODEL_HAIKU]


def known_tasks() -> list[str]:
    """Known task keys (handy for external validation / tests)."""
    return list(_TASK_TABLE.keys())
