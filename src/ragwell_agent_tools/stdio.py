"""Local MCP and command-line entry point with sanitized failures."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from typing import Never

from mcp.server.stdio import stdio_server

from . import __version__
from .diagnostics import DebugLog
from .operations import SearchInput
from .settings import Settings, SettingsError
from .tools import SearchRuntime, ToolFailure, build_server

# UTF-8 takes at most four bytes per character. SearchInput also checks length.
MAX_QUERY_STDIN_BYTES = 8_000


async def serve(settings: Settings, diagnostics: DebugLog | None = None) -> None:
    server = build_server(settings, diagnostics=diagnostics)
    async with stdio_server() as (reader, writer):
        await server.run(reader, writer, server.create_initialization_options())


async def check_connection(settings: Settings, diagnostics: DebugLog | None) -> int:
    async with SearchRuntime(settings, diagnostics=diagnostics) as runtime:
        available = await runtime.available_tools()
    if not isinstance(available, frozenset):
        error = ToolFailure.model_validate(available.structured_content)
        print(
            json.dumps(
                {"status": "error", "code": error.code, "message": error.message}
            )
        )
        return 1
    if "ragwell_search" not in available:
        print(
            json.dumps(
                {
                    "status": "error",
                    "code": "access_denied",
                    "message": "Grant retrieval:search to the configured project, or check the project ID.",
                }
            )
        )
        return 1
    print(json.dumps({"status": "ready", "tools": sorted(available), "searches": 0}))
    return 0


async def search_command(
    settings: Settings, request: SearchInput, diagnostics: DebugLog | None
) -> int:
    async with SearchRuntime(settings, diagnostics=diagnostics) as runtime:
        result = await runtime.call("ragwell_search", request.model_dump())
    payload = result.structured_content
    if payload is None:
        raise RuntimeError("Missing structured search result")
    if not result.is_error:
        # Issued references are discarded when this one-shot process exits.
        payload["source_expansion_available"] = False
    print(json.dumps(payload, separators=(",", ":")))
    return 1 if result.is_error else 0


def _print_cli_failure(
    code: str, message: str, *, usage_uncertain: bool = False
) -> None:
    error = ToolFailure(
        code=code, message=message, usage_may_have_been_recorded=usage_uncertain
    )
    print(
        json.dumps(
            error.model_dump(mode="json", exclude_none=True), separators=(",", ":")
        )
    )


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> Never:
        # argparse's default error includes raw argument values.
        _print_cli_failure(
            "invalid_arguments", "Check the command arguments with --help."
        )
        raise SystemExit(2)


def _read_search_input(k: int) -> SearchInput:
    raw = sys.stdin.buffer.read(MAX_QUERY_STDIN_BYTES + 1)
    if len(raw) > MAX_QUERY_STDIN_BYTES:
        raise ValueError("Search input exceeded its byte limit")
    return SearchInput(query=raw.decode("utf-8"), k=k)


def _run_search_command(k: int) -> int:
    diagnostics: DebugLog | None = None
    started = False
    try:
        settings = Settings.from_env()
        try:
            request = _read_search_input(k)
        except (ValueError, OSError):
            _print_cli_failure(
                "invalid_arguments",
                "Supply a nonblank UTF-8 query of at most 2000 characters on stdin.",
            )
            return 2
        if settings.debug_log is not None:
            diagnostics = DebugLog.start(settings.debug_log)
        started = True
        return asyncio.run(search_command(settings, request, diagnostics))
    except SettingsError as exc:
        _print_cli_failure("configuration_error", str(exc))
        return 2
    except KeyboardInterrupt:
        _print_cli_failure(
            "search_interrupted", "The search was interrupted.", usage_uncertain=started
        )
        return 130
    except Exception as exc:
        if diagnostics is not None:
            diagnostics.record("search_failed", exc)
        _print_cli_failure(
            "search_failed",
            "Ragwell could not complete the search.",
            usage_uncertain=started,
        )
        return 1


def main() -> None:
    parser = _ArgumentParser(
        description="Ragwell local evidence search and MCP server", allow_abbrev=False
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check current project grants without a search or an agent task",
    )
    commands = parser.add_subparsers(dest="command")
    commands.add_parser("mcp", help="Start the local MCP stdio server (default)")
    search = commands.add_parser(
        "search", help="Run one search and print JSON", allow_abbrev=False
    )
    search.add_argument(
        "--query-stdin",
        action="store_true",
        required=True,
        help="Read a UTF-8 query from stdin",
    )
    search.add_argument("--k", type=int, choices=range(1, 6), default=5)
    args = parser.parse_args()
    if args.check and args.command is not None:
        parser.error("--check cannot be combined with a command")

    # Framework/transport exception logs can contain source or argument values.
    # The application reports sanitized failures through its result contract
    # and, when RAGWELL_DEBUG_LOG is set, through value-free diagnostics.
    logging.basicConfig(level=logging.CRITICAL, stream=sys.stderr)
    if args.command == "search":
        raise SystemExit(_run_search_command(args.k))
    diagnostics: DebugLog | None = None
    try:
        settings = Settings.from_env()
        if settings.debug_log is not None:
            diagnostics = DebugLog.start(settings.debug_log)
        if args.check:
            raise SystemExit(asyncio.run(check_connection(settings, diagnostics)))
        asyncio.run(serve(settings, diagnostics))
    except SettingsError as exc:
        print(f"ragwell_configuration_error: {exc}", file=sys.stderr)
        raise SystemExit(2) from None
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        if diagnostics is not None:
            diagnostics.record("server_failed", exc)
        print(
            "ragwell_server_failed: restart the connection or contact support",
            file=sys.stderr,
        )
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
