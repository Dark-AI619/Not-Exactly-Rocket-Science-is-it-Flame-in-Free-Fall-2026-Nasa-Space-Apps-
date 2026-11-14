# Phase 4A — secure Groq boundary

Checked 2026-11-15. This checkpoint adds one optional Groq SDK adapter to the existing Phase 3 retrieval backend. No generative request is connected to the Streamlit pages, no real key is present, and no live Groq request was made.

## Audit and integration point

The baseline development branch was `phase3-integration` at Phase 3F commit `3c3308b7fca2b2a9419a9583b1fee415355a3806`. The clean baseline passed 30 tests. `data/flame_research.db.gz` contains 273 validated FLEX tests, 2,457 measurement cells, 329 PDF passages and 23 sources; Phase 4A does not modify it. `backend.retrieval.retrieve_evidence` remains the authoritative source of bounded evidence packets. The new adapter accepts bounded chat messages only; Phase 4B will compose verified packets into those messages and validate generated claims.

## Configuration and behavior

The official `groq` Python SDK is the only new runtime dependency. `load_groq_settings` reads environment variables first and optionally Streamlit secrets. It never logs the key, and `GroqSettings` hides it from its representation. A missing or placeholder key returns `evidence_only` without constructing a client or making a network call. `.env`, `.env.*`, `.streamlit/secrets.toml`, secret backups and logs are Git-ignored; `.env.example` contains no credential.

The configurable model defaults to `qwen/qwen3.8-27b`, shown in Groq's [supported model documentation](https://console.groq.com/docs/model/qwen/qwen3.8-27b) and [free-tier rate-limit table](https://console.groq.com/docs/rate-limits) on this date. Account availability must be checked again before live use; model IDs and quotas can change. The default output cap is 600 tokens (allowed 64–2048), timeout 20 seconds (allowed 1–60), and future per-session request limit eight (allowed 1–50). The adapter disables hidden SDK retries and makes at most three attempts with short bounded backoff. A long `retry-after` yields evidence-only fallback instead of waiting or retrying aggressively. Authentication, rate-limit, timeout and provider-unavailable states are reported with fixed codes, not raw credential-bearing exceptions. Successful mocked calls report latency and prompt/completion token counts.

## Verification

The full local test suite passed **37 tests**. New offline tests cover environment and Streamlit-secret loading, missing-key fallback, deterministic retrieval without a key, mocked success with usage and latency, authentication failure, short and long rate limits, timeout, server and connection errors, and message bounds. Python compilation and `git diff --check` passed. With `GROQ_API_KEY` explicitly unset, a local Streamlit launch on port 8507 displayed the Assistant, retrieved four cited FLEX evidence items, and showed no Streamlit exception. No live Groq model access, free-tier account entitlement or generated scientific answer was tested in 4A.

## Next checkpoint

Phase 4B may use the existing evidence packet as the only factual context for one Groq request and must validate citations and numerical claims before showing generated text. The public Streamlit app and `main` remain unchanged. Wait for explicit approval before implementing 4B.
