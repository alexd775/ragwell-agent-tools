from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from .helpers import PROJECT_ID, platform_environment, settings
from .test_stdio import Peer
from .test_stdio import peer as peer


def qualify_cli(
    fixtures: dict[str, str],
    *,
    require_all: bool = False,
    command: str | None = "/nonexistent-executable",
) -> subprocess.CompletedProcess[str]:
    config = settings()
    env = platform_environment(
        **{
            "RAGWELL_BASE_URL": config.base_url,
            "RAGWELL_PROJECT_ID": str(config.project_id),
            "RAGWELL_API_KEY": config.api_key,
            **fixtures,
        },
    )
    script = Path(__file__).resolve().parents[1] / "scripts" / "qualify_endpoint.py"
    return subprocess.run(
        [
            sys.executable,
            str(script),
            *(["--command", command] if command is not None else []),
            *(["--require-all"] if require_all else []),
        ],
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
    )


def test_require_all_fails_before_starting_any_client() -> None:
    result = qualify_cli({}, require_all=True)
    assert result.returncode == 2
    assert not result.stdout
    assert "Missing required fixture variables" in result.stderr


@pytest.mark.parametrize("foreign", ["not-a-project-uuid", str(PROJECT_ID)])
def test_invalid_foreign_project_is_rejected_before_positive_searches(
    foreign: str,
) -> None:
    result = qualify_cli({"RAGWELL_QA_FOREIGN_PROJECT_ID": foreign})
    assert result.returncode == 2
    assert "qualification_configuration_error" in result.stderr
    assert foreign not in result.stderr


def test_denial_fixture_cannot_charge_the_positive_key() -> None:
    config = settings()
    result = qualify_cli({"RAGWELL_QA_REVOKED_KEY": config.api_key})
    assert result.returncode == 2
    assert "cannot reuse" in result.stderr
    assert config.api_key not in result.stderr


def test_connection_failure_identifies_cause_without_echoing_command() -> None:
    secret = settings().api_key
    result = qualify_cli({}, command=f"/nonexistent-{secret}")
    assert result.returncode == 1
    assert "FileNotFoundError" in result.stderr
    assert secret not in result.stderr
    assert "Traceback" not in result.stderr


def test_real_qualifier_corpus_and_all_denials(peer: Peer) -> None:
    peer.nullable_scores = True
    peer.filenames = {
        "How do I request leave?": "handbook.md",
        "What does the archived 2025 travel policy require?": "travel-policy-2025.md",
        "What does the current 2026 travel policy require?": "travel-policy-2026.md",
        "What are the project decisions about permissions and metered search retries?": "project-decisions.md",
    }
    result = qualify_cli(
        {
            "RAGWELL_BASE_URL": peer.origin,
            "RAGWELL_ALLOW_LOCAL_HTTP": "true",
            "RAGWELL_QA_SCOPE_KEY": "scope-fixture",
            "RAGWELL_QA_EXPIRED_KEY": "expired-fixture",
            "RAGWELL_QA_REVOKED_KEY": "revoked-fixture",
            "RAGWELL_QA_QUOTA_KEY": "quota-fixture",
            "RAGWELL_QA_RATE_KEY": "rate-fixture",
            "RAGWELL_QA_FOREIGN_PROJECT_ID": "00000000-0000-0000-0000-000000000999",
        },
        require_all=True,
        command=None,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.count("PASS ") == 10
    assert not result.stderr
    assert len(peer.requests) == 6
    assert len(peer.discovery_requests) == 11


def test_rejected_positive_search_reports_code_and_is_not_replayed(peer: Peer) -> None:
    result = qualify_cli(
        {
            "RAGWELL_BASE_URL": peer.origin,
            "RAGWELL_ALLOW_LOCAL_HTTP": "true",
            "RAGWELL_API_KEY": "revoked-fixture",
        },
        command=None,
    )
    assert result.returncode == 1
    assert result.stderr == "FAIL leave: authentication_failed\n"
    assert "private-fixture-error" not in result.stderr
    assert "revoked-fixture" not in result.stderr
    assert not peer.requests
    assert len(peer.discovery_requests) == 1
