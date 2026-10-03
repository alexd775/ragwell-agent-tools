from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

import httpx
import pytest
from ragwell.types import SearchResponse

from ragwell_agent_tools import stdio
from ragwell_agent_tools.diagnostics import DebugLog
from ragwell_agent_tools.sdk_operations import SdkOperations
from ragwell_agent_tools.settings import Settings, SettingsError
from ragwell_agent_tools.tools import SearchRuntime

from .helpers import (
    PROJECT_ID,
    FakeOperations,
    capabilities_body,
    result_data,
    search_body,
    settings,
)


def entries(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def test_api_failure_records_identity_without_values(tmp_path: Path) -> None:
    log = tmp_path / "debug.jsonl"

    async def scenario() -> None:
        config = settings()

        def respond(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/v1/machine/capabilities":
                return httpx.Response(200, json=capabilities_body())
            return httpx.Response(
                503,
                json={"error": {"code": "raw-code", "message": "sensitive-provider"}},
                headers={"X-Request-ID": str(PROJECT_ID)},
            )

        async with SdkOperations(
            config, transport=httpx.MockTransport(respond)
        ) as operations:
            async with SearchRuntime(
                config, operations, diagnostics=DebugLog(log)
            ) as runtime:
                result = await runtime.call(
                    "ragwell_search", {"query": "private query"}
                )
        assert result_data(result)["code"] == "api_unavailable"

    asyncio.run(scenario())
    [entry] = entries(log)
    assert entry["event"] == "failure"
    assert entry["code"] == "api_unavailable"
    assert entry["exception"].startswith("ragwell.")
    assert entry["status_code"] == 503
    assert entry["request_id"] == str(PROJECT_ID)
    assert entry["operation_id"].startswith("search_")
    text = log.read_text()
    for value in ("private query", "sensitive-provider", "raw-code", "synthetic-test"):
        assert value not in text


def test_invalid_upstream_shape_records_field_locations_only(tmp_path: Path) -> None:
    log = tmp_path / "debug.jsonl"
    raw = search_body(text="sensitive-source-text")
    raw["items"][0]["parts"][2]["span"]["start_offset"] = -1

    async def scenario() -> None:
        operations = FakeOperations(SearchResponse.from_dict(raw))
        async with SearchRuntime(
            settings(), operations, diagnostics=DebugLog(log)
        ) as runtime:
            await runtime.call("ragwell_search", {"query": "x"})

    asyncio.run(scenario())
    [entry] = entries(log)
    assert entry["code"] == "invalid_response"
    assert entry["exception"] == "pydantic_core._pydantic_core.ValidationError"
    assert entry["validation"] == [
        {"loc": "span.start_offset", "type": "greater_than_equal"}
    ]
    assert "sensitive-source-text" not in log.read_text()


def test_unexpected_error_records_type_and_frames_not_message(tmp_path: Path) -> None:
    log = tmp_path / "debug.jsonl"

    async def scenario() -> None:
        operations = FakeOperations()
        operations.error = TypeError("secret failure value")
        async with SearchRuntime(
            settings(), operations, diagnostics=DebugLog(log)
        ) as runtime:
            await runtime.call("ragwell_search", {"query": "x"})

    asyncio.run(scenario())
    [entry] = entries(log)
    assert entry["code"] == "invalid_response"
    assert entry["exception"] == "builtins.TypeError"
    assert any(frame.startswith("helpers.py:") for frame in entry["frames"])
    assert "secret failure value" not in log.read_text()


def test_rejected_arguments_record_only_the_code(tmp_path: Path) -> None:
    log = tmp_path / "debug.jsonl"

    async def scenario() -> None:
        async with SearchRuntime(
            settings(), FakeOperations(), diagnostics=DebugLog(log)
        ) as runtime:
            await runtime.call(
                "ragwell_search", {"query": "private query", "private-key": "x"}
            )

    asyncio.run(scenario())
    [entry] = entries(log)
    assert entry["code"] == "invalid_arguments"
    assert set(entry) == {"time", "pid", "event", "code"}


def test_debug_log_requires_an_absolute_writable_file(tmp_path: Path) -> None:
    with pytest.raises(SettingsError):
        settings(debug_log=Path("relative.jsonl"))
    with pytest.raises(SettingsError):
        DebugLog.start(tmp_path)
    log = tmp_path / "debug.jsonl"
    DebugLog.start(log)
    [entry] = entries(log)
    assert entry["event"] == "started"
    assert {"version", "ragwell_sdk", "mcp"} <= set(entry)
    if os.name != "nt":
        assert log.stat().st_mode & 0o777 == 0o600


def test_environment_selects_debug_log(tmp_path: Path) -> None:
    value = Settings.from_env(
        {
            "RAGWELL_BASE_URL": "https://example.invalid",
            "RAGWELL_PROJECT_ID": str(PROJECT_ID),
            "RAGWELL_API_KEY": "synthetic-test-credential",
            "RAGWELL_DEBUG_LOG": str(tmp_path / "debug.jsonl"),
        }
    )
    assert value.debug_log == tmp_path / "debug.jsonl"


def test_server_failure_is_recorded_without_message(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    log = tmp_path / "debug.jsonl"

    async def failing_serve(*_args: object) -> None:
        raise RuntimeError("secret startup value")

    monkeypatch.setattr(stdio, "serve", failing_serve)
    monkeypatch.setattr(sys, "argv", ["ragwell-agent-tools"])
    monkeypatch.setenv("RAGWELL_BASE_URL", "https://example.invalid")
    monkeypatch.setenv("RAGWELL_PROJECT_ID", str(PROJECT_ID))
    monkeypatch.setenv("RAGWELL_API_KEY", "synthetic-test-credential")
    monkeypatch.setenv("RAGWELL_DEBUG_LOG", str(log))
    with pytest.raises(SystemExit) as exit_status:
        stdio.main()
    assert exit_status.value.code == 1
    started, failed = entries(log)
    assert started["event"] == "started"
    assert failed["code"] == "server_failed"
    assert failed["exception"] == "builtins.RuntimeError"
    assert "secret startup value" not in log.read_text()
    assert "secret startup value" not in capsys.readouterr().err
