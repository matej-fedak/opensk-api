"""Rate-limit middleware tests.

Deterministic: the limiter clock is replaced with a fake; no real sleeping.
The shared singleton limiter in `services.rate_limit` is reset between tests.
"""

from __future__ import annotations

import json

import pytest
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

import services.rate_limit as rate_limit_module
from main import app as production_app
from services.rate_limit import (
    REQUEST_LIMIT,
    RateLimitMiddleware,
    _parse_ip,
    rate_limit_enabled,
    rate_limiter,
)

LIMIT = REQUEST_LIMIT
WINDOW = 60


@pytest.fixture
def clock(monkeypatch):
    value = [1_760_000_000]  # arbitrary fixed epoch
    monkeypatch.setattr(rate_limiter, "_clock", lambda: value[0])
    return value


@pytest.fixture
def env(monkeypatch):
    monkeypatch.delenv("RENDER", raising=False)
    monkeypatch.delenv("OPENSK_RATE_LIMIT_ENABLED", raising=False)
    return monkeypatch


@pytest.fixture(autouse=True)
def _reset_limiter():
    rate_limiter.reset()
    yield
    rate_limiter.reset()


@pytest.fixture
def client():
    return TestClient(production_app)


def _limited_app(limit: int, clock) -> TestClient:
    small = rate_limit_module.FixedWindowRateLimiter(clock=lambda: clock[0], limit=limit, window_seconds=WINDOW)
    app = FastAPI()

    @app.get("/v1/ping")
    def ping():
        return {"ok": True}

    app.add_middleware(RateLimitMiddleware, limiter=small)
    return TestClient(app), small


# --- enablement -------------------------------------------------------------


def test_disabled_outside_render_by_default(client, env):
    response = client.get("/v1/banks")
    assert response.status_code == 200
    assert "X-RateLimit-Limit" not in response.headers


def test_enabled_under_render_env(client, env):
    env.setenv("RENDER", "true")
    response = client.get("/v1/banks")
    assert response.headers["X-RateLimit-Limit"] == str(LIMIT)


def test_explicit_enable_override_local(client, env):
    env.setenv("OPENSK_RATE_LIMIT_ENABLED", "true")
    response = client.get("/v1/banks")
    assert "X-RateLimit-Limit" in response.headers


def test_explicit_disable_override_render(client, env):
    env.setenv("RENDER", "true")
    env.setenv("OPENSK_RATE_LIMIT_ENABLED", "false")
    response = client.get("/v1/banks")
    assert "X-RateLimit-Limit" not in response.headers


def test_unknown_setting_falls_back_to_auto(monkeypatch):
    assert rate_limit_enabled(lambda key: {"OPENSK_RATE_LIMIT_ENABLED": "bogus"}.get(key)) is False
    assert rate_limit_enabled(lambda key: {"OPENSK_RATE_LIMIT_ENABLED": " true ", "RENDER": ""}.get(key)) is True


# --- identity ---------------------------------------------------------------


def test_identity_off_render_ignores_xff(client, env, clock):
    env.setenv("OPENSK_RATE_LIMIT_ENABLED", "true")
    client.get("/", headers={"X-Forwarded-For": "1.1.1.1"})
    client.get("/", headers={"X-Forwarded-For": "9.9.9.9"})
    # Both requests land in the same peer bucket (TestClient peer), not the spoofed ones.
    assert set(rate_limiter._counts.keys()) == {"testclient"}
    assert rate_limiter._counts["testclient"] == 2


def test_identity_render_uses_rightmost_non_cloudflare(client, env, clock):
    env.setenv("RENDER", "true")
    client.get("/", headers={"X-Forwarded-For": "203.0.113.10"})
    client.get("/", headers={"X-Forwarded-For": "9.9.9.9, 203.0.113.11"})
    client.get("/", headers={"X-Forwarded-For": "198.51.100.5, 172.64.0.9"})  # right-most is Cloudflare egress
    assert rate_limiter._counts == {
        "203.0.113.10": 1,
        "203.0.113.11": 1,
        "198.51.100.5": 1,
    }


def test_identity_render_spoof_left_entries_share_bucket(client, env, clock):
    env.setenv("OPENSK_RATE_LIMIT_ENABLED", "true")
    env.setenv("RENDER", "true")
    for fake in ["1.1.1.1", "2.2.2.2", "3.3.3.3"]:
        client.get("/", headers={"X-Forwarded-For": f"{fake}, 203.0.113.99"})
    assert rate_limiter._counts == {"203.0.113.99": 3}


def test_identity_render_ipv4_ipv6_and_malformed(client, env, clock):
    env.setenv("RENDER", "true")
    client.get("/", headers={"X-Forwarded-For": "2001:db8::1"})
    client.get("/", headers={"X-Forwarded-For": "garbage, 10.20.30.40"})
    client.get("/", headers={"X-Forwarded-For": "[2001:db8::2]:443"})
    assert rate_limiter._counts == {
        "2001:db8::1": 1,
        "10.20.30.40": 1,
        "2001:db8::2": 1,
    }


def test_identity_render_missing_or_invalid_fails_closed(client, env, clock):
    env.setenv("RENDER", "true")
    response = client.get("/")  # no X-Forwarded-For at all
    assert response.status_code == 200
    client.get("/", headers={"X-Forwarded-For": "not-an-ip"})
    assert rate_limiter._counts == {"unknown": 2}


def test_parse_ip_forms():
    assert str(_parse_ip(" 192.0.2.1 ")) == "192.0.2.1"
    assert str(_parse_ip("192.0.2.1:8080")) == "192.0.2.1"
    assert str(_parse_ip("[2001:db8::5]:443")) == "2001:db8::5"
    assert _parse_ip("nonsense") is None
    assert _parse_ip("") is None


# --- limit semantics (small deterministic limit) ----------------------------


def test_limit_threshold_and_independent_buckets(env, clock):
    env.setenv("RENDER", "true")
    small_client, _small = _limited_app(3, clock)
    headers = {"X-Forwarded-For": "203.0.113.1"}
    assert small_client.get("/v1/ping", headers=headers).status_code == 200
    assert small_client.get("/v1/ping", headers=headers).status_code == 200
    assert small_client.get("/v1/ping", headers=headers).status_code == 200
    rejected = small_client.get("/v1/ping", headers=headers)
    assert rejected.status_code == 429
    assert rejected.headers["X-RateLimit-Remaining"] == "0"

    other = small_client.get("/v1/ping", headers={"X-Forwarded-For": "203.0.113.2"})
    assert other.status_code == 200


def test_window_reset_restores_quota_and_clears_state(env, clock):
    env.setenv("RENDER", "true")
    small_client, small = _limited_app(2, clock)
    headers = {"X-Forwarded-For": "203.0.113.1"}
    assert small_client.get("/v1/ping", headers=headers).status_code == 200
    assert small_client.get("/v1/ping", headers=headers).status_code == 200
    assert small_client.get("/v1/ping", headers=headers).status_code == 429

    clock[0] += WINDOW
    allowed = small_client.get("/v1/ping", headers=headers)
    assert allowed.status_code == 200
    assert allowed.headers["X-RateLimit-Remaining"] == "1"
    assert list(small._counts.keys()) == ["203.0.113.1"]


def test_headers_limit_remaining_reset_and_retry_after(env, clock):
    env.setenv("RENDER", "true")
    small_client, small = _limited_app(3, clock)
    headers = {"X-Forwarded-For": "203.0.113.1"}
    first = small_client.get("/v1/ping", headers=headers)
    expected_reset = (clock[0] // WINDOW + 1) * WINDOW
    assert first.headers["X-RateLimit-Limit"] == "3"
    assert first.headers["X-RateLimit-Remaining"] == "2"
    assert first.headers["X-RateLimit-Reset"] == str(expected_reset)

    small_client.get("/v1/ping", headers=headers)
    small_client.get("/v1/ping", headers=headers)
    rejected = small_client.get("/v1/ping", headers=headers)
    assert rejected.status_code == 429
    assert rejected.headers["Retry-After"] == str(expected_reset - clock[0])
    assert rejected.headers["X-RateLimit-Reset"] == str(expected_reset)
    assert rejected.headers["Cache-Control"] == "no-store"

    clock[0] += WINDOW - 1  # boundary: same remaining logic never goes negative
    allowed = small_client.get("/v1/ping", headers=headers)
    assert int(allowed.headers["X-RateLimit-Remaining"]) >= 0


# --- health exemption -------------------------------------------------------


def test_health_never_limited_and_consumes_no_quota(client, env, clock):
    env.setenv("RENDER", "true")
    for _ in range(LIMIT + 50):
        response = client.get("/v1/health")
        assert response.status_code == 200
        assert "X-RateLimit-Limit" not in response.headers

    response = client.get("/")
    assert response.headers["X-RateLimit-Remaining"] == str(LIMIT - 1)


# --- HTTP / middleware interaction ------------------------------------------


def test_200_has_rate_and_existing_cache_headers(client, env, clock):
    env.setenv("RENDER", "true")
    response = client.get("/v1/banks")
    assert response.status_code == 200
    assert "X-RateLimit-Limit" in response.headers
    assert response.headers["etag"].startswith('"')
    assert "last-modified" in response.headers


def test_conditional_304_consumes_quota_and_carries_headers(client, env, clock):
    env.setenv("RENDER", "true")
    first = client.get("/v1/banks")
    etag = first.headers["etag"]
    second = client.get("/v1/banks", headers={"If-None-Match": etag})
    assert second.status_code == 304
    assert second.headers["X-RateLimit-Limit"] == str(LIMIT)
    assert second.headers["X-RateLimit-Remaining"] == str(LIMIT - 2)

    third = client.get("/v1/holidays/2026", headers={"If-Modified-Since": "Wed, 01 Jan 3030 00:00:00 GMT"})
    assert third.status_code == 304
    assert third.headers["X-RateLimit-Remaining"] == str(LIMIT - 3)


def test_error_responses_still_consume_quota(client, env, clock):
    env.setenv("RENDER", "true")
    missing = client.get("/v1/exchange-rates/2026-10-10")
    assert missing.status_code == 404
    assert missing.headers["X-RateLimit-Remaining"] == str(LIMIT - 1)
    invalid = client.get("/v1/exchange-rates/latest", params={"currency": "nope"})
    assert invalid.status_code == 400
    assert invalid.headers["X-RateLimit-Remaining"] == str(LIMIT - 2)


def test_429_has_no_etag_or_last_modified(client, env, clock):
    env.setenv("RENDER", "true")
    for _ in range(LIMIT):
        assert client.get("/v1/banks").status_code == 200
    rejected = client.get("/v1/banks")
    assert rejected.status_code == 429
    assert "etag" not in rejected.headers
    assert "last-modified" not in rejected.headers
    assert rejected.headers["Cache-Control"] == "no-store"


def test_cors_exposes_rate_headers_and_429_is_wrapped(client, env, clock):
    env.setenv("RENDER", "true")
    origin = {"Origin": "https://example.com"}
    response = client.get("/v1/banks", headers=origin)
    assert response.headers["access-control-allow-origin"] == "*"
    exposed = response.headers["access-control-expose-headers"].lower()
    for header in ("x-ratelimit-limit", "x-ratelimit-remaining", "x-ratelimit-reset", "retry-after"):
        assert header in exposed

    for _ in range(LIMIT - 1):
        client.get("/v1/banks", headers=origin)
    rejected = client.get("/v1/banks", headers=origin)
    assert rejected.status_code == 429
    assert rejected.headers["access-control-allow-origin"] == "*"


def test_options_preflight_not_counted(client, env, clock):
    env.setenv("RENDER", "true")
    preflight = client.options(
        "/v1/banks",
        headers={"Origin": "https://example.com", "Access-Control-Request-Method": "GET"},
    )
    assert preflight.status_code == 200
    assert "X-RateLimit-Limit" not in preflight.headers
    assert rate_limiter._counts == {}


# --- envelope ---------------------------------------------------------------


def test_429_uses_standard_error_envelope(client, env, clock):
    env.setenv("RENDER", "true")
    for _ in range(LIMIT):
        client.get("/v1/banks")
    rejected = client.get("/v1/banks")
    assert rejected.status_code == 429
    body = json.loads(rejected.content)
    assert body == {
        "data": None,
        "metadata": {"source": "OpenSK API", "lastUpdated": None, "version": "v1"},
        "error": {
            "code": "RATE_LIMITED",
            "message": "Rate limit exceeded. Retry after the number of seconds in Retry-After.",
            "messageSk": "Prekročený limit požiadaviek. Skúste znova po počte sekúnd v Retry-After.",
        },
    }
    assert body["metadata"]["lastUpdated"] is None
    assert body["metadata"]["version"] == "v1"


def test_non_get_requests_bypass_limiter(client, env, clock):
    env.setenv("RENDER", "true")
    response = client.post("/v1/banks")
    assert response.status_code == 405
    assert "X-RateLimit-Limit" not in response.headers
