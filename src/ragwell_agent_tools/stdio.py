"""Local stdio entry point; protocol output and credentials stay separate."""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from mcp.server.stdio import stdio_server

from . import __version__
from .diagnostics import DebugLog
from .settings import Settings, SettingsError
from .tools import build_server


async def serve(settings: Settings, diagnostics: DebugLog | None = None) -> None:
    server = build_server(settings, diagnostics=diagnostics)
    async with stdio_server() as (reader, writer):
        await server.run(reader, writer, server.create_initialization_options())


def main() -> None:
    parser = argparse.ArgumentParser(description="Ragwell local MCP evidence search")
    parser.add_argument("--version", action="version", version=__version__)
    parser.parse_args()
    # Framework/transport exception logs can contain source or argument values.
    # The application reports sanitized failures through its result contract
    # and, when RAGWELL_DEBUG_LOG is set, through value-free diagnostics.
    logging.basicConfig(level=logging.CRITICAL, stream=sys.stderr)
    diagnostics: DebugLog | None = None
    try:
        settings = Settings.from_env()
        if settings.debug_log is not None:
            diagnostics = DebugLog.start(settings.debug_log)
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
