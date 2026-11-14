# Co-authored with ChatGPT
"""Single optional Groq boundary; the research corpus remains authoritative."""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Callable, Mapping

import groq


DEFAULT_MODEL = "qwen/qwen3.8-27b"  # Verify account availability again before live use.


@dataclass(frozen=True)
class GroqSettings:
    api_key: str = field(default="", repr=False)
    model: str = DEFAULT_MODEL
    max_output_tokens: int = 600
    request_timeout: float = 20.0
    session_request_limit: int = 8

    @property
    def configured(self) -> bool:
        return bool(self.api_key.strip())


@dataclass(frozen=True)
class GroqResult:
    mode: str  # "model" or "evidence_only"
    text: str | None
    status: str
    model: str | None
    latency_ms: float
    attempts: int
    prompt_tokens: int | None = None
    completion_tokens: int | None = None


def _bounded_number(value: object, default: int | float, minimum: int | float,
                    maximum: int | float, kind: type[int] | type[float]) -> int | float:
    try:
        number = kind(value)
    except (TypeError, ValueError):
        return default
    return number if minimum <= number <= maximum else default


def load_groq_settings(*, environ: Mapping[str, str] | None = None,
                       secrets: Mapping[str, object] | None = None) -> GroqSettings:
    """Read environment first, then optional Streamlit secrets; never log values."""
    environment = os.environ if environ is None else environ
    if secrets is None:
        try:
            import streamlit as st
            secrets = st.secrets
        except ImportError:
            secrets = {}

    def read(name: str, default: str = "") -> str:
        value = environment.get(name)
        if value is None or not str(value).strip():
            try:
                value = secrets.get(name) if secrets is not None else None
            except Exception:  # Streamlit raises if no secrets file exists.
                value = None
        return str(value).strip() if value is not None and str(value).strip() else default

    key = read("GROQ_API_KEY")
    if key.lower() in {"replace-me", "your-key-here", "placeholder"}:
        key = ""
    return GroqSettings(
        api_key=key,
        model=read("GROQ_MODEL", DEFAULT_MODEL),
        max_output_tokens=int(_bounded_number(read("GROQ_MAX_OUTPUT_TOKENS"), 600, 64, 2048, int)),
        request_timeout=float(_bounded_number(read("GROQ_REQUEST_TIMEOUT"), 20.0, 1.0, 60.0, float)),
        session_request_limit=int(_bounded_number(read("AI_SESSION_REQUEST_LIMIT"), 8, 1, 50, int)),
    )


class GroqAdapter:
    """Invoke the official SDK only with a configured key; return safe fallback states."""

    def __init__(self, settings: GroqSettings, *, client_factory: Callable | None = None,
                 sleep: Callable[[float], None] = time.sleep,
                 clock: Callable[[], float] = time.perf_counter):
        self.settings = settings
        self._factory = client_factory or groq.Groq
        self._client = None
        self._sleep = sleep
        self._clock = clock

    def complete(self, messages: list[dict[str, str]]) -> GroqResult:
        if not self.settings.configured:
            return GroqResult("evidence_only", None, "missing_key", None, 0.0, 0)
        if not messages or len(messages) > 12 or any(
            item.get("role") not in {"system", "user", "assistant"}
            or not isinstance(item.get("content"), str)
            or len(item["content"]) > 12_000 for item in messages
        ):
            raise ValueError("messages must be 1–12 bounded text messages")
        start = self._clock()
        attempts = 0

        def fallback(status: str) -> GroqResult:
            return GroqResult("evidence_only", None, status, self.settings.model,
                              round((self._clock() - start) * 1000, 1), attempts)

        try:
            if self._client is None:
                self._client = self._factory(api_key=self.settings.api_key,
                                             timeout=self.settings.request_timeout, max_retries=0)
            for retry in range(3):
                attempts += 1
                try:
                    response = self._client.chat.completions.create(
                        model=self.settings.model, messages=messages,
                        max_completion_tokens=self.settings.max_output_tokens,
                    )
                    content = response.choices[0].message.content
                    if not isinstance(content, str) or not content.strip():
                        return fallback("empty_response")
                    usage = getattr(response, "usage", None)
                    return GroqResult(
                        "model", content.strip(), "ok", self.settings.model,
                        round((self._clock() - start) * 1000, 1), attempts,
                        getattr(usage, "prompt_tokens", None),
                        getattr(usage, "completion_tokens", None),
                    )
                except (groq.AuthenticationError, groq.PermissionDeniedError):
                    return fallback("authentication_failed")
                except groq.RateLimitError as exc:
                    wait = 0.25 * 2 ** retry
                    header = exc.response.headers.get("retry-after")
                    if header is not None:
                        try:
                            wait = float(header)
                        except ValueError:
                            pass
                    if retry == 2 or wait > 2.0:
                        return fallback("rate_limited")
                    self._sleep(max(0.0, wait))
                except (groq.APITimeoutError, groq.APIConnectionError, groq.InternalServerError):
                    if retry == 2:
                        return fallback("provider_unavailable")
                    self._sleep(0.25 * 2 ** retry)
                except groq.APIStatusError as exc:
                    if exc.status_code in (408, 409) and retry < 2:
                        self._sleep(0.25 * 2 ** retry)
                        continue
                    return fallback("provider_unavailable")
        except (groq.APIError, OSError, ValueError, TypeError, IndexError, AttributeError):
            return fallback("provider_unavailable")
        return fallback("provider_unavailable")
