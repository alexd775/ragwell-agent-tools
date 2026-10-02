from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from .helpers import PROJECT_ID, platform_environment, settings


def qualify_cli(
    fixtures: dict[str, str], *, require_all: bool = False
) -> subprocess.CompletedProcess[str]:
    config = settings()
    env = platform_environment(
        RAGWELL_BASE_URL=config.base_url,
        RAGWELL_PROJECT_ID=str(config.project_id),
        RAGWELL_API_KEY=config.api_key,
        **fixtures,
    )
    script = Path(__file__).resolve().parents[1] / "scripts" / "qualify_endpoint.py"
    return subprocess.run(
        [
            sys.executable,
            str(script),
            "--command",
            "/nonexistent-executable",
            *(["--require-all"] if require_all else []),
        ],
        env=env,
        capture_output=True,
        text=True,
        timeout=5,
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
