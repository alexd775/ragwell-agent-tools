"""Opt-in synthetic beta searches and credential-denial cases; never prepare state."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
from collections.abc import Mapping
from dataclasses import replace
from uuid import UUID

from mcp import Client, StdioServerParameters

from ragwell_agent_tools.diagnostics import describe
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
FAILURE_CODES = frozenset(
    {
        "unknown_tool",
        "invalid_arguments",
        "busy",
        "local_budget_exhausted",
        "not_ready",
        "authentication_failed",
        "access_denied",
        "project_unavailable",
        "quota_exceeded",
        "rate_limited",
        "request_rejected",
        "search_timeout",
        "connection_failed",
        "invalid_response",
        "api_unavailable",
        "search_failed",
        "discovery_timeout",
        "discovery_unavailable",
    }
)


def failure_code(data: object) -> str:
    """Only known adapter codes may leave an untrusted tool response."""
    code = data.get("code") if isinstance(data, dict) else None
    return (
        code
        if isinstance(code, str) and code in FAILURE_CODES
        else "invalid_tool_response"
    )


def exception_details(error: BaseException, depth: int = 0) -> dict[str, object]:
    """Expose nested protocol failures without messages, arguments or values."""
    details = describe(error)
    if depth < 3:
        if isinstance(error, BaseExceptionGroup):
            details["exceptions"] = [
                exception_details(item, depth + 1) for item in error.exceptions[:4]
            ]
        elif error.__cause__ is not None:
            details["caused_by"] = exception_details(error.__cause__, depth + 1)
    return details


def parameters(settings: Settings, command: str | None) -> StdioServerParameters:
    env = {
        "RAGWELL_BASE_URL": settings.base_url,
        "RAGWELL_PROJECT_ID": str(settings.project_id),
        "RAGWELL_API_KEY": settings.api_key,
        "RAGWELL_TIMEOUT_SECONDS": str(settings.timeout_seconds),
        "RAGWELL_MAX_OUTPUT_BYTES": str(settings.max_output_bytes),
        "RAGWELL_MAX_SEARCHES": str(settings.max_searches),
        "RAGWELL_ALLOW_LOCAL_HTTP": str(settings.allow_local_http).lower(),
    }
    if settings.debug_log is not None:
        env["RAGWELL_DEBUG_LOG"] = str(settings.debug_log)
    return StdioServerParameters(
        command=command or sys.executable,
        args=[] if command else ["-m", "ragwell_agent_tools.stdio"],
        env=env,
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
    read_timeout = max(30.0, settings.timeout_seconds + 5)
    async with Client(
        parameters(settings, command), mode="legacy", read_timeout_seconds=read_timeout
    ) as client:
        for label, query, filename in QUERIES:
            result = await client.call_tool("ragwell_search", {"query": query})
            data = result.structured_content
            if result.is_error or not isinstance(data, dict):
                print(f"FAIL {label}: {failure_code(data)}", file=sys.stderr)
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
            parameters(config, command),
            mode="legacy",
            read_timeout_seconds=read_timeout,
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
            print(
                f"FAIL {label}: expected denial missing ({failure_code(data)})",
                file=sys.stderr,
            )
            return 1
        print(f"PASS {label}: expected denial")
    if foreign_config is not None:
        async with Client(
            parameters(foreign_config, command),
            mode="legacy",
            read_timeout_seconds=read_timeout,
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
            print(
                f"FAIL foreign_project: expected denial missing ({failure_code(data)})",
                file=sys.stderr,
            )
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
        + ", RAGWELL_QA_FOREIGN_PROJECT_ID. For a local .env, run "
        "uv run --locked --no-sync --env-file .env python scripts/qualify_endpoint.py. "
        "Never put key values in arguments or committed files.",
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
    # MCP validation/transport logs may contain response data or arguments.
    logging.basicConfig(level=logging.CRITICAL, stream=sys.stderr)
    try:
        status = asyncio.run(
            qualify(Settings.from_env(), args.command, args.require_all)
        )
    except SettingsError as exc:
        print(f"qualification_configuration_error: {exc}", file=sys.stderr)
        status = 2
    except Exception as exc:
        print(
            "qualification_failed: MCP connection, protocol or fixture error",
            file=sys.stderr,
        )
        print(
            json.dumps(exception_details(exc), separators=(",", ":")), file=sys.stderr
        )
        status = 1
    raise SystemExit(status)


if __name__ == "__main__":
    main()
