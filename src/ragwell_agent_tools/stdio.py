"""Local stdio entry point; protocol output and credentials stay separate."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys

from mcp.server.stdio import stdio_server

from . import __version__
from .diagnostics import DebugLog
from .settings import Settings, SettingsError
from .tools import SearchRuntime, ToolFailure, build_server


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


def main() -> None:
    parser = argparse.ArgumentParser(description="Ragwell local MCP evidence search")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check current project grants without a search or an agent task",
    )
    args = parser.parse_args()
    # Framework/transport exception logs can contain source or argument values.
    # The application reports sanitized failures through its result contract
    # and, when RAGWELL_DEBUG_LOG is set, through value-free diagnostics.
    logging.basicConfig(level=logging.CRITICAL, stream=sys.stderr)
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
