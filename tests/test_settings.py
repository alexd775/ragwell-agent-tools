from __future__ import annotations

import math

import pytest

from ragwell_agent_tools.settings import Settings, SettingsError

from .helpers import PROJECT_ID, settings


@pytest.mark.parametrize(
    "origin",
    [
        "http://api.example.com",
        "https://user:credential@example.com",
        "https://example.com?key=credential",
        "https://example.com#credential",
        "https://example.com/v1",
        "file:///tmp/secret",
        "https://example.com:bad",
        "https://example.com/ ",
    ],
)
def test_unsafe_origin_is_rejected_without_echoing_value(origin: str) -> None:
    with pytest.raises(SettingsError) as error:
        settings(base_url=origin)
    assert origin not in str(error.value)


def test_credentials_are_not_represented_and_are_explicit() -> None:
    value = settings()
    assert value.api_key not in repr(value)
    with pytest.raises(SettingsError, match="RAGWELL_BASE_URL"):
        Settings.from_env({})
    with pytest.raises(SettingsError) as error:
        Settings.from_env(
            {
                "RAGWELL_BASE_URL": value.base_url,
                "RAGWELL_PROJECT_ID": "sensitive-value",
                "RAGWELL_API_KEY": value.api_key,
            }
        )
    assert "sensitive-value" not in str(error.value)


@pytest.mark.parametrize("credential", ["", "line\nbreak", "space here", "\x7f"])
def test_invalid_credentials(credential: str) -> None:
    with pytest.raises(SettingsError):
        settings(api_key=credential)


@pytest.mark.parametrize("timeout", [0, -1, math.inf, math.nan, 121])
def test_deadline_is_finite_and_bounded(timeout: float) -> None:
    with pytest.raises(SettingsError):
        settings(timeout_seconds=timeout)


def test_loopback_http_requires_explicit_test_opt_in() -> None:
    with pytest.raises(SettingsError):
        settings(base_url="http://127.0.0.1:9000")
    assert settings(base_url="http://127.0.0.1:9000", allow_local_http=True)
    with pytest.raises(SettingsError):
        settings(base_url="http://api.example.com", allow_local_http=True)


def test_environment_configuration() -> None:
    value = Settings.from_env(
        {
            "RAGWELL_BASE_URL": "https://example.invalid/",
            "RAGWELL_PROJECT_ID": str(PROJECT_ID),
            "RAGWELL_API_KEY": "synthetic-test-credential",
            "RAGWELL_TIMEOUT_SECONDS": "10",
            "RAGWELL_MAX_OUTPUT_BYTES": "4096",
            "RAGWELL_MAX_SEARCHES": "2",
        }
    )
    assert value.base_url == "https://example.invalid"
    assert value.project_id == PROJECT_ID
    assert value.timeout_seconds == 10
    assert value.max_output_bytes == 4096
    assert value.max_searches == 2


@pytest.mark.parametrize(
    "name,value",
    [
        ("RAGWELL_MAX_OUTPUT_BYTES", "2047"),
        ("RAGWELL_MAX_SEARCHES", "0"),
        ("RAGWELL_TIMEOUT_SECONDS", "not-a-number"),
        ("RAGWELL_ALLOW_LOCAL_HTTP", "yes"),
    ],
)
def test_environment_limits_fail_closed(name: str, value: str) -> None:
    values = {
        "RAGWELL_BASE_URL": "https://example.invalid",
        "RAGWELL_PROJECT_ID": str(PROJECT_ID),
        "RAGWELL_API_KEY": "synthetic-test-credential",
        name: value,
    }
    with pytest.raises(SettingsError):
        Settings.from_env(values)
