"""Opt-in synthetic beta searches and credential-denial cases; never prepare state."""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from collections.abc import Mapping
from dataclasses import replace
from uuid import UUID

from mcp import Client, StdioServerParameters

from ragwell_agent_tools.settings import Settings, SettingsError

CASES = {
    "missing_scope": ("RAGWELL_QA_SCOPE_KEY", {"access_denied"}),
    "expired": ("RAGWELL_QA_EXPIRED_KEY", {"authentication_failed"}),
    "revoked": ("RAGWELL_QA_REVOKED_KEY", {"authentication_failed"}),
    "quota": ("RAGWELL_QA_QUOTA_KEY", {"quota_exceeded"}),
    "rate": ("RAGWELL_QA_RATE_KEY", {"rate_limited"}),
}
QUERIES = (
    ("leave", "How do I request leave?", "handbook.md"),
    (
        "old_policy",
        "What does the archived 2025 travel policy require?",
        "travel-policy-2025.md",
    ),
    (
        "new_policy",
        "What does the current 2026 travel policy require?",
        "travel-policy-2026.md",
    ),
    (
        "decisions",
        "What are the project decisions about permissions and metered search retries?",
        "project-decisions.md",
    ),
)


def parameters(settings: Settings, command: str | None) -> StdioServerParameters:
    return StdioServerParameters(
        command=command or sys.executable,
        args=[] if command else ["-m", "ragwell_agent_tools.stdio"],
        env={
            "RAGWELL_BASE_URL": settings.base_url,
            "RAGWELL_PROJECT_ID": str(settings.project_id),
            "RAGWELL_API_KEY": settings.api_key,
            "RAGWELL_TIMEOUT_SECONDS": str(settings.timeout_seconds),
            "RAGWELL_MAX_SEARCHES": str(settings.max_searches),
        },
    )


async def qualify(
    settings: Settings,
    command: str | None,
    require_all: bool,
    fixtures: Mapping[str, str] | None = None,
) -> int:
    values = os.environ if fixtures is None else fixtures
    required = [variable for variable, _codes in CASES.values()]
    required.append("RAGWELL_QA_FOREIGN_PROJECT_ID")
    missing = [name for name in required if not values.get(name)]
    if require_all and missing:
        print(
            "Missing required fixture variables: " + ", ".join(missing), file=sys.stderr
        )
        return 2
    credentials: dict[str, Settings] = {}
    for label, (variable, _codes) in CASES.items():
        key = values.get(variable)
        if key:
            if key == settings.api_key:
                raise SettingsError(
                    "A denial fixture cannot reuse the allowed search key"
                )
            credentials[label] = replace(settings, api_key=key)
    foreign = values.get("RAGWELL_QA_FOREIGN_PROJECT_ID")
    foreign_config = None
    if foreign:
        try:
            foreign_id = UUID(foreign)
        except ValueError:
            raise SettingsError(
                "RAGWELL_QA_FOREIGN_PROJECT_ID must be a UUID"
            ) from None
        if foreign_id == settings.project_id:
            raise SettingsError(
                "The foreign project fixture must differ from the allowed project"
            )
        foreign_config = replace(settings, project_id=foreign_id)
    async with Client(
        parameters(settings, command), mode="legacy", read_timeout_seconds=30
    ) as client:
        for label, query, filename in QUERIES:
            result = await client.call_tool("ragwell_search", {"query": query})
            data = result.structured_content
            if result.is_error or not isinstance(data, dict):
                print(f"FAIL {label}: search rejected", file=sys.stderr)
                return 1
            matches = data.get("matches", [])
            if not any(
                match.get("source_filename") == filename
                and any(
                    part.get("kind") == "evidence" and part.get("text")
                    for part in match.get("parts", [])
                )
                for match in matches
            ):
                print(
                    f"FAIL {label}: expected source evidence missing", file=sys.stderr
                )
                return 1
            print(f"PASS {label}: source evidence returned")
    for label, (_variable, expected) in CASES.items():
        config = credentials.get(label)
        if config is None:
            print(f"SKIP {label}: fixture credential absent")
            continue
        async with Client(
            parameters(config, command), mode="legacy", read_timeout_seconds=30
        ) as client:
            result = await client.call_tool(
                "ragwell_search", {"query": "integration qualification"}
            )
        data = result.structured_content
        if (
            not result.is_error
            or not isinstance(data, dict)
            or data.get("code") not in expected
        ):
            print(f"FAIL {label}: expected denial missing", file=sys.stderr)
            return 1
        print(f"PASS {label}: expected denial")
    if foreign_config is not None:
        async with Client(
            parameters(foreign_config, command), mode="legacy", read_timeout_seconds=30
        ) as client:
            result = await client.call_tool(
                "ragwell_search", {"query": "integration qualification"}
            )
        data = result.structured_content
        if (
            not result.is_error
            or not isinstance(data, dict)
            or data.get("code") not in {"access_denied", "project_unavailable"}
        ):
            print("FAIL foreign_project: expected denial missing", file=sys.stderr)
            return 1
        print("PASS foreign_project: expected denial")
    else:
        print("SKIP foreign_project: fixture project absent")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run four metered synthetic-corpus searches and opt-in denial cases.",
        epilog="Fixture variables: "
        + ", ".join(variable for variable, _ in CASES.values())
        + ", RAGWELL_QA_FOREIGN_PROJECT_ID. Never put key values in arguments or files.",
    )
    parser.add_argument(
        "--command",
        help="Installed executable path; defaults to this interpreter's package",
    )
    parser.add_argument(
        "--require-all",
        action="store_true",
        help="Fail before searches if any denial fixture is absent",
    )
    args = parser.parse_args()
    try:
        status = asyncio.run(
            qualify(Settings.from_env(), args.command, args.require_all)
        )
    except SettingsError as exc:
        print(f"qualification_configuration_error: {exc}", file=sys.stderr)
        status = 2
    except Exception:
        print(
            "qualification_failed: connection or fixture error; no raw details emitted",
            file=sys.stderr,
        )
        status = 1
    raise SystemExit(status)


if __name__ == "__main__":
    main()
