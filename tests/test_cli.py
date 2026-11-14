"""One-shot search through the command entry point and shared execution runtime."""

from __future__ import annotations

import io
import json
import sys

import pytest

from ragwell_agent_tools import stdio
from ragwell_agent_tools.diagnostics import DebugLog
from ragwell_agent_tools.settings import Settings
from ragwell_agent_tools.tools import SearchRuntime

from .helpers import PROJECT_ID, FakeOperations


@pytest.fixture
def configured_connection(monkeypatch: pytest.MonkeyPatch) -> FakeOperations:
    monkeypatch.setenv("RAGWELL_BASE_URL", "https://api.ragwell.dev")
    monkeypatch.setenv("RAGWELL_PROJECT_ID", str(PROJECT_ID))
    monkeypatch.setenv("RAGWELL_API_KEY", "synthetic-cli-fixture")
    operations = FakeOperations()

    def new_runtime(
        settings: Settings, *, diagnostics: DebugLog | None = None
    ) -> SearchRuntime:
        return SearchRuntime(settings, operations, diagnostics=diagnostics)

    monkeypatch.setattr(stdio, "SearchRuntime", new_runtime)
    return operations


def run_command(monkeypatch: pytest.MonkeyPatch, stdin: bytes, *args: str) -> int:
    monkeypatch.setattr(sys, "argv", ["ragwell-agent-tools", "search", *args])
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(stdin)))
    with pytest.raises(SystemExit) as caught:
        stdio.main()
    assert isinstance(caught.value.code, int)
    return caught.value.code


def test_cli_search_preserves_evidence_and_disables_source_expansion(
    configured_connection: FakeOperations,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    query = "How do I book a trip to København?"
    assert run_command(monkeypatch, query.encode(), "--query-stdin", "--k", "2") == 0
    capture = capsys.readouterr()
    assert not capture.err
    assert capture.out.count("\n") == 1
    evidence = json.loads(capture.out)
    assert evidence["status"] == "ok"
    assert evidence["source_expansion_available"] is False
    assert evidence["source_text_is_untrusted"] is True
    match = evidence["matches"][0]
    assert match["source_filename"] == "travel-policy.md"
    assert match["parts"][2]["start_line"] == 3
    assert match["parts"][2]["span"]["start_offset"] == 18
    [request] = configured_connection.requests
    assert request.query == query
    assert request.k == 2
    assert configured_connection.capability_calls == 1
    assert configured_connection.source_requests == []


def test_cli_search_does_not_replay_or_disclose_timed_out_search(
    configured_connection: FakeOperations,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    configured_connection.error = TimeoutError("private-fixture-error")
    assert run_command(monkeypatch, b"private-fixture-query", "--query-stdin") == 1
    capture = capsys.readouterr()
    assert not capture.err
    assert "private-fixture" not in capture.out
    failure = json.loads(capture.out)
    assert failure["status"] == "error"
    assert failure["code"] == "search_timeout"
    assert failure["usage_may_have_been_recorded"] is True
    assert failure["automatic_retry"] is False
    [request] = configured_connection.requests
    assert request.k == 5


@pytest.mark.parametrize(
    "stdin,args",
    [
        (b"query", ()),
        (b"query", ("--query-stdin", "--k", "private-fixture-argument")),
        (b" \n", ("--query-stdin",)),
        (b"\xff", ("--query-stdin",)),
        (b"x" * 2_001, ("--query-stdin",)),
        (b"x" * 8_001, ("--query-stdin",)),
    ],
)
def test_cli_rejects_bad_input_before_discovery(
    stdin: bytes,
    args: tuple[str, ...],
    configured_connection: FakeOperations,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert run_command(monkeypatch, stdin, *args) == 2
    capture = capsys.readouterr()
    assert not capture.err
    assert "private-fixture-argument" not in capture.out
    assert json.loads(capture.out)["code"] == "invalid_arguments"
    assert configured_connection.capability_calls == 0
    assert configured_connection.requests == []
