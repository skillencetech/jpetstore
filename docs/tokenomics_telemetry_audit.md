# JPetStore Modernization: Tokenomics & AI Usage Audit

**Document Version:** 2.0.0  
**Target Reference:** docs/ASSESSMENT.pdf (Evaluation Area: *Tokenomics*)  
**System:** JPetStore AI-Native Python Platform

---

## 1. Scope

This audit covers two separate things, and keeps them apart:

* **Part A: AI usage while building the application.** Measured as far as the tooling allows.
* **Part B: Cost design of the AI features inside the application.** A design analysis, not a benchmark.

Anything not measured is labeled as such.

---

## 2. Part A: AI Resource Use During the Build (Measured)

### 2.1 What the tooling exposes

The Antigravity IDE reports quota as a **percentage of each model pool**, not as token counts. Gemini models share one pool, and Claude and GPT models share another. Token counts per prompt, cache hits and cost were not available, so none are reported. Percentages are not converted to tokens or cost.

### 2.2 Pool readings

| Reading | Gemini weekly remaining | Gemini five-hour remaining | Claude and GPT weekly remaining |
| :-- | :-: | :-: | :-: |
| 28 Oct, 9:28 AM | 89% | 100% | 0% |
| 28 Oct, 12:34 PM | 80% | 71% | 0% |
| Change | 9 points | 29 points | none (already exhausted) |

The Claude and GPT pool was already exhausted at both readings, so the work in this window ran on Gemini models. The pools are account-wide and may include other work.

### 2.3 Prompts by milestone

The full list of 66 prompts across two working sessions is in the Prompt Log, tagged by milestone.

| Milestone | Prompts |
| :-- | :-: |
| M0 Discovery and decomposition | 3 |
| M1 Strategy, decisions and ADRs | 9 |
| M2 Foundation and dependency resolution | 4 |
| M3 Catalog and UI rendering | 1 |
| M4 Cart, preferences and visual parity | 3 |
| M5 Account, security and localization | 8 |
| M6 Orders and checkout | 3 |
| M7 AI-native layer | 7 |
| M8 Verification, documentation and deployment | 20 |
| M9 Submission and handover | 8 |
| **Total** | **66** |

Of these, 15 prompts reported a defect or a parity gap (build errors, runtime errors, layout and feature gaps). These are the iteration evidence: they show where generated output needed correction.

### 2.4 Practices applied to limit consumption

* **Decisions before code.** Nine prompts went to strategy and ADRs before generation began, which reduced rework on structure.
* **Reuse of the existing front end.** Porting JSPs to Jinja2 avoided generating and validating a separate SPA (ADR-002). The saving was not measured.
* **Bounded scope per request.** Work was requested domain by domain (catalog, cart, account, orders, AI layer).
* **Verification gates.** Linting, type checking, security scanning and regression tests run after generation (see the Guardrails report).
* **Fixes driven by evidence.** Defect prompts quote the error text or attach a screenshot rather than describing symptoms loosely.

### 2.5 Limits of the measurement

* Percentages cannot be attributed to a single milestone or model.
* Only two readings were taken, so consumption is not split by milestone.
* The model used per prompt was not recorded.
* No claim of efficiency relative to a baseline is made, because no baseline was run.

---

## 3. Part B: Runtime Cost Design of the AI Features (Design Analysis)

### 3.1 Design

Semantic search and the Pet Advisor use in-process, rule-based scoring over catalog data (`app/services/ai_service.py`). They make **no calls to an external LLM or embedding service**. Consequences that follow directly from that design:

* No per-request token cost.
* No dependency on an external AI service's availability or rate limits.
* Catalog data stays in-process.
* Behavior is deterministic and testable with `pytest`.

### 3.2 Agent tool endpoints

The `/api/v1/tools` endpoints use compact Pydantic v2 schemas with concise field descriptions. An external agent that loads these definitions pays tokens for them on each invocation, so schema size matters. The size has **not been measured**. It can be measured by passing the generated `/openapi.json` for the tool routes to a tokenizer and reporting the count with the tokenizer name.

### 3.3 Bounded advisor input

The advisor receives active category IDs and item IDs from the cart and profile preferences, and draws recommendations from catalog records. It does not send order history or rendered HTML to any model.

### 3.4 Trade-off

Local scoring is free, private and deterministic, but it matches on weighted keywords and category concepts rather than learned meaning. Queries phrased outside those rules will return weaker results than an embedding or LLM approach. The scorer sits behind a service interface, so a model-backed implementation can replace it at the cost of tokens, latency and an external dependency. If that were done, the controls in the Guardrails report (input screening, output validation, token limits) become required.

### 3.5 Illustrative comparison (not measured)

If every search sent the full catalog (16 products, 28 items) to an external model, input tokens per query would scale with catalog size and prompt design, and cost would scale with the provider's pricing. This is a qualitative comparison. No dollar or latency figures are claimed, because none were measured.

---

## 4. What Would Be Done With More Time

1. Log usage per call through an API key or proxy to obtain input, output and cache-read tokens.
2. Report cost per milestone and cost per passing test.
3. Run one slice (for example, catalog search) with and without bounded context, and report the difference against a measured baseline.
4. Benchmark search and advisor latency (median and 95th percentile over at least 100 requests), recording the machine used.
5. Count the token size of the tool schemas with a named tokenizer.
