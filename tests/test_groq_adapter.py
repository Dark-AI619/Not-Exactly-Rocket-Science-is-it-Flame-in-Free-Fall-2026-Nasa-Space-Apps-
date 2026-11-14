# Co-authored with ChatGPT
"""Offline Groq boundary tests: no credentials or network requests."""
from types import SimpleNamespace
from unittest.mock import Mock

import groq
import httpx

from backend import GroqAdapter, GroqSettings, ResearchStore, load_groq_settings, retrieve_evidence


MESSAGES = [{"role": "user", "content": "Summarize the cited evidence."}]
REQUEST = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")


def client_with(*responses):
    create = Mock(side_effect=list(responses))
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    factory = Mock(return_value=client)
    return factory, create


def success_response():
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="Cited answer [E1]."))],
        usage=SimpleNamespace(prompt_tokens=120, completion_tokens=18),
    )


def status_error(kind, code, headers=None):
    response = httpx.Response(code, request=REQUEST, headers=headers or {})
    return kind("provider error", response=response, body=None)


def test_settings_read_environment_or_streamlit_secrets_without_exposing_key():
    settings = load_groq_settings(environ={}, secrets={"GROQ_API_KEY": "private-test-value"})
    assert settings.configured and "private-test-value" not in repr(settings)
    assert settings.model == "qwen/qwen3.8-27b"
    override = load_groq_settings(
        environ={"GROQ_API_KEY": "environment-value", "GROQ_MODEL": "qwen/qwen3.8-27b",
                 "GROQ_MAX_OUTPUT_TOKENS": "700", "GROQ_REQUEST_TIMEOUT": "12",
                 "AI_SESSION_REQUEST_LIMIT": "4"},
        secrets={"GROQ_API_KEY": "ignored-secret"},
    )
    assert override.api_key == "environment-value"
    assert (override.max_output_tokens, override.request_timeout, override.session_request_limit) == (700, 12.0, 4)
    invalid = load_groq_settings(environ={"GROQ_MAX_OUTPUT_TOKENS": "1000000",
                                          "GROQ_REQUEST_TIMEOUT": "nan", "GROQ_API_KEY": "placeholder"}, secrets={})
    assert not invalid.configured
    assert (invalid.max_output_tokens, invalid.request_timeout) == (600, 20.0)


def test_missing_key_never_constructs_client_and_retrieval_still_works():
    factory = Mock(side_effect=AssertionError("network client must not be created"))
    result = GroqAdapter(GroqSettings(), client_factory=factory).complete(MESSAGES)
    assert result.mode == "evidence_only" and result.status == "missing_key"
    assert result.attempts == 0 and result.text is None
    factory.assert_not_called()
    with ResearchStore() as store:
        evidence = retrieve_evidence(store, "What is flame extinction in FLEX?")
    assert evidence["supported"] and evidence["items"]


def test_success_reports_latency_usage_and_bounded_settings():
    factory, create = client_with(success_response())
    result = GroqAdapter(GroqSettings(api_key="fake-local-test", max_output_tokens=500),
                         client_factory=factory, clock=Mock(side_effect=[1.0, 1.025])).complete(MESSAGES)
    assert result.mode == "model" and result.status == "ok" and result.text == "Cited answer [E1]."
    assert result.latency_ms == 25.0 and (result.prompt_tokens, result.completion_tokens) == (120, 18)
    factory.assert_called_once_with(api_key="fake-local-test", timeout=20.0, max_retries=0)
    assert create.call_args.kwargs["max_completion_tokens"] == 500


def test_authentication_error_falls_back_without_retry_or_leak():
    factory, create = client_with(status_error(groq.AuthenticationError, 401))
    result = GroqAdapter(GroqSettings(api_key="do-not-print"), client_factory=factory).complete(MESSAGES)
    assert result.status == "authentication_failed" and result.mode == "evidence_only"
    assert result.attempts == 1 and "do-not-print" not in repr(result)
    assert create.call_count == 1


def test_rate_limit_respects_short_retry_after_and_caps_long_wait():
    short = status_error(groq.RateLimitError, 429, {"retry-after": "1.5"})
    factory, create = client_with(short, success_response())
    sleep = Mock()
    result = GroqAdapter(GroqSettings(api_key="fake"), client_factory=factory, sleep=sleep).complete(MESSAGES)
    assert result.status == "ok" and result.attempts == 2
    sleep.assert_called_once_with(1.5)
    assert create.call_count == 2
    long = status_error(groq.RateLimitError, 429, {"retry-after": "60"})
    factory, create = client_with(long)
    result = GroqAdapter(GroqSettings(api_key="fake"), client_factory=factory, sleep=sleep).complete(MESSAGES)
    assert result.status == "rate_limited" and result.attempts == 1
    assert create.call_count == 1


def test_timeouts_and_provider_errors_use_bounded_retries():
    timeout = groq.APITimeoutError(REQUEST)
    factory, create = client_with(timeout, timeout, timeout)
    sleep = Mock()
    result = GroqAdapter(GroqSettings(api_key="fake"), client_factory=factory, sleep=sleep).complete(MESSAGES)
    assert result.status == "provider_unavailable" and result.attempts == 3
    assert [call.args[0] for call in sleep.call_args_list] == [0.25, 0.5]
    assert create.call_count == 3

    factory, create = client_with(status_error(groq.InternalServerError, 503), success_response())
    result = GroqAdapter(GroqSettings(api_key="fake"), client_factory=factory, sleep=Mock()).complete(MESSAGES)
    assert result.status == "ok" and result.attempts == 2

    unavailable = groq.APIConnectionError(request=REQUEST)
    factory, create = client_with(unavailable, unavailable, unavailable)
    result = GroqAdapter(GroqSettings(api_key="fake"), client_factory=factory, sleep=Mock()).complete(MESSAGES)
    assert result.status == "provider_unavailable" and create.call_count == 3


def test_malformed_messages_are_rejected_before_provider_call():
    factory, _ = client_with(success_response())
    adapter = GroqAdapter(GroqSettings(api_key="fake"), client_factory=factory)
    try:
        adapter.complete([{"role": "tool", "content": "unexpected"}])
    except ValueError:
        pass
    else:
        raise AssertionError("unsupported message role was accepted")
    factory.assert_not_called()
