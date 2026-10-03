"""Real subprocess stdio and SDK HTTP with a synthetic loopback peer."""

from __future__ import annotations

import asyncio
import json
import subprocess
import sys
import threading
from collections.abc import Iterator
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import pytest
from mcp import Client, StdioServerParameters

from ragwell_agent_tools import __version__

from .helpers import (
    PROJECT_ID,
    capabilities_body,
    platform_environment,
    result_data,
    search_body,
    source_arguments,
    source_body,
)


@dataclass
class Peer:
    origin: str = ""
    requests: list[dict[str, Any]] = field(default_factory=list)
    filenames: dict[str, str] = field(default_factory=dict)
    nullable_scores: bool = False
    discovery_requests: list[str] = field(default_factory=list)


@pytest.fixture
def peer() -> Iterator[Peer]:
    value = Peer()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:
            pass

        def do_GET(self) -> None:
            if self.path == "/v1/machine/capabilities":
                value.discovery_requests.append(self.path)
                authority = self.headers.get("Authorization", "")
                status = 200
                payload = capabilities_body()
                if authority in {"Bearer revoked-fixture", "Bearer expired-fixture"}:
                    status = 401
                    payload = {
                        "error": {
                            "code": "fixture_rejected",
                            "message": "private-fixture-error",
                        }
                    }
                elif authority == "Bearer scope-fixture":
                    payload = capabilities_body(scopes=["project:read"])
                elif authority == "Bearer foreign-fixture":
                    payload = capabilities_body(project_id=PROJECT_ID.__class__(int=99))
                encoded = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)
                return
            value.requests.append({"path": self.path, "body": None})
            encoded = json.dumps(source_body()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def do_POST(self) -> None:
            request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            authority = self.headers.get("Authorization", "")
            value.requests.append({"path": self.path, "body": request})
            status = 200
            payload = search_body()
            payload["items"][0]["source_filename"] = value.filenames.get(
                request["query"], "travel-policy.md"
            )
            if value.nullable_scores:
                payload["items"][0]["scores"] = {
                    "final": 0.7,
                    "text": None,
                    "vector": None,
                }
            if authority in {"Bearer revoked-fixture", "Bearer expired-fixture"}:
                status = 401
            elif (
                authority in {"Bearer scope-fixture", "Bearer foreign-fixture"}
                or self.path != f"/v1/projects/{PROJECT_ID}/search"
            ):
                status = 403
            elif authority in {"Bearer quota-fixture", "Bearer rate-fixture"}:
                status = 429
            if status != 200:
                code = (
                    "plan_limit_searches"
                    if authority == "Bearer quota-fixture"
                    else "fixture_rejected"
                )
                payload = {"error": {"code": code, "message": "private-fixture-error"}}
            encoded = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("X-Request-ID", str(PROJECT_ID))
            self.end_headers()
            self.wfile.write(encoded)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    value.origin = f"http://127.0.0.1:{server.server_port}"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield value
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        assert not thread.is_alive()


def parameters(
    origin: str, cwd: Path, key: str = "success-fixture", **extra: str
) -> StdioServerParameters:
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "ragwell_agent_tools.stdio"],
        cwd=cwd,
        env={
            "RAGWELL_BASE_URL": origin,
            "RAGWELL_PROJECT_ID": str(PROJECT_ID),
            "RAGWELL_API_KEY": key,
            "RAGWELL_ALLOW_LOCAL_HTTP": "true",
            **extra,
        },
    )


@pytest.mark.parametrize("mode", ["legacy", "auto"])
def test_real_stdio_handshake_search_and_clean_shutdown(
    peer: Peer, tmp_path: Path, mode: str, capfd: pytest.CaptureFixture[str]
) -> None:
    async def scenario() -> None:
        async with Client(
            parameters(peer.origin, tmp_path), mode=mode, read_timeout_seconds=5
        ) as client:
            assert client.protocol_version == (
                "2025-11-25" if mode == "legacy" else "2026-07-28"
            )
            listed = await client.list_tools()
            assert [t.name for t in listed.tools] == [
                "ragwell_search",
                "ragwell_fetch_source",
            ]
            result = await client.call_tool(
                "ragwell_search", {"query": "How do I request travel?", "k": 1}
            )
            assert not result.is_error
            assert (
                result_data(result)["matches"][0]["source_filename"]
                == "travel-policy.md"
            )
            source = await client.call_tool("ragwell_fetch_source", source_arguments())
            assert not source.is_error
            assert result_data(source)["content"] == source_body()["content"]
            invalid = await client.call_tool(
                "ragwell_search",
                {"query": "private-invalid-query", "project_id": "foreign"},
            )
            assert invalid.is_error

    asyncio.run(scenario())
    assert len(peer.requests) == 2
    assert len(peer.discovery_requests) == 3
    assert peer.requests[0]["body"] == {"query": "How do I request travel?", "k": 1}
    captured = capfd.readouterr()
    assert captured.out == ""
    assert captured.err == ""


@pytest.mark.parametrize("mode", ["legacy", "auto"])
def test_stdio_accepts_absent_component_scores(
    peer: Peer, tmp_path: Path, mode: str
) -> None:
    peer.nullable_scores = True

    async def scenario() -> None:
        async with Client(parameters(peer.origin, tmp_path), mode=mode) as client:
            result = await client.call_tool(
                "ragwell_search", {"query": "synthetic query"}
            )
            assert not result.is_error
            assert result_data(result)["matches"][0]["scores"] == {"final": 0.7}

    asyncio.run(scenario())
    assert len(peer.requests) == 1


@pytest.mark.parametrize(
    "key,expected",
    [
        ("revoked-fixture", "authentication_failed"),
        ("expired-fixture", "authentication_failed"),
        ("scope-fixture", "access_denied"),
        ("foreign-fixture", "access_denied"),
        ("quota-fixture", "quota_exceeded"),
        ("rate-fixture", "rate_limited"),
    ],
)
def test_stdio_denials_do_not_retry_or_disclose_peer_messages(
    peer: Peer,
    tmp_path: Path,
    key: str,
    expected: str,
    capfd: pytest.CaptureFixture[str],
) -> None:
    async def scenario() -> None:
        async with Client(
            parameters(peer.origin, tmp_path, key),
            mode="legacy",
            read_timeout_seconds=5,
        ) as client:
            result = await client.call_tool(
                "ragwell_search", {"query": "private-denied-query"}
            )
            assert result.is_error
            assert result_data(result)["code"] == expected
            assert "private-fixture-error" not in result.model_dump_json()
            assert "private-denied-query" not in result.model_dump_json()
            assert key not in result.model_dump_json()

    asyncio.run(scenario())
    assert len(peer.requests) == (
        0
        if key
        in {"revoked-fixture", "expired-fixture", "scope-fixture", "foreign-fixture"}
        else 1
    )
    assert len(peer.discovery_requests) == 1
    captured = capfd.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_stdio_debug_log_records_sanitized_failures(
    peer: Peer, tmp_path: Path, capfd: pytest.CaptureFixture[str]
) -> None:
    log = tmp_path / "debug.jsonl"

    async def scenario() -> None:
        async with Client(
            parameters(
                peer.origin, tmp_path, "rate-fixture", RAGWELL_DEBUG_LOG=str(log)
            ),
            mode="legacy",
            read_timeout_seconds=5,
        ) as client:
            result = await client.call_tool(
                "ragwell_search", {"query": "private-logged-query"}
            )
            assert result_data(result)["code"] == "rate_limited"

    asyncio.run(scenario())
    started, failed = [json.loads(line) for line in log.read_text().splitlines()]
    assert started["event"] == "started"
    assert failed["code"] == "rate_limited"
    assert failed["status_code"] == 429
    assert failed["request_id"] == str(PROJECT_ID)
    for value in ("private-logged-query", "private-fixture-error", "rate-fixture"):
        assert value not in log.read_text()
    captured = capfd.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_cli_requires_configuration_without_stdout_or_traceback(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ragwell_agent_tools.stdio"],
        env=platform_environment(),
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 2
    assert result.stdout == ""
    assert (
        result.stderr
        == "ragwell_configuration_error: Set RAGWELL_BASE_URL before starting Ragwell tools\n"
    )


def test_version_command_needs_no_key(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ragwell_agent_tools.stdio", "--version"],
        env=platform_environment(),
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == __version__
    assert not result.stderr


@pytest.mark.parametrize(
    "key,expected",
    [("success-fixture", 0), ("scope-fixture", 1), ("revoked-fixture", 1)],
)
def test_unmetered_connection_check(
    peer: Peer, tmp_path: Path, key: str, expected: int
) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ragwell_agent_tools.stdio", "--check"],
        env=platform_environment(
            RAGWELL_BASE_URL=peer.origin,
            RAGWELL_PROJECT_ID=str(PROJECT_ID),
            RAGWELL_API_KEY=key,
            RAGWELL_ALLOW_LOCAL_HTTP="true",
        ),
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == expected
    assert not result.stderr
    data = json.loads(result.stdout)
    if expected == 0:
        assert data == {
            "status": "ready",
            "tools": ["ragwell_fetch_source", "ragwell_search"],
            "searches": 0,
        }
    else:
        assert data["code"] in {"access_denied", "authentication_failed"}
    assert not peer.requests
    assert len(peer.discovery_requests) == 1
    assert key not in result.stdout
