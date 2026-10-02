"""Opt-in local failure diagnostics without queries, source text or credentials."""

from __future__ import annotations

import json
import os
import traceback
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from uuid import UUID

from pydantic import ValidationError as ModelValidationError
from ragwell import ApiError, RagwellError

from . import __version__
from .settings import SettingsError


def qualified_name(value: BaseException) -> str:
    kind = type(value)
    return f"{kind.__module__}.{kind.__qualname__}"


def describe(error: BaseException) -> dict[str, object]:
    """Exception identity and code locations only.

    Messages, arguments and frame values are never read: SDK, protocol and
    validation messages can contain queries, source text or response values.
    """
    frames = traceback.StackSummary.extract(
        traceback.walk_tb(error.__traceback__), lookup_lines=False
    )
    details: dict[str, object] = {
        "exception": qualified_name(error),
        "frames": [
            f"{Path(frame.filename).name}:{frame.lineno} {frame.name}"
            for frame in frames
        ][-8:],
    }
    if error.__cause__ is not None:
        details["cause"] = qualified_name(error.__cause__)
    if isinstance(error, BaseExceptionGroup):
        details["grouped"] = [qualified_name(item) for item in error.exceptions][:8]
    if isinstance(error, RagwellError):
        if error.operation_id:
            details["operation_id"] = error.operation_id
        try:
            if error.request_id:
                details["request_id"] = str(UUID(error.request_id))
        except ValueError:
            pass
    if isinstance(error, ApiError):
        details["status_code"] = error.status_code
    if isinstance(error, ModelValidationError):
        # Locations name output-model fields; input values are excluded.
        details["validation"] = [
            {"loc": ".".join(str(item) for item in entry["loc"]), "type": entry["type"]}
            for entry in error.errors(
                include_url=False, include_context=False, include_input=False
            )
        ][:10]
    return details


class DebugLog:
    """Appends JSON lines to a user-selected local file for support diagnosis."""

    def __init__(self, path: Path) -> None:
        self._path = path

    @classmethod
    def start(cls, path: Path) -> DebugLog:
        log = cls(path)
        started = log._write(
            {
                "event": "started",
                "version": __version__,
                "ragwell_sdk": version("ragwell"),
                "mcp": version("mcp"),
            }
        )
        if not started:
            raise SettingsError("RAGWELL_DEBUG_LOG must be a writable file path")
        return log

    def record(self, code: str, error: BaseException | None = None) -> None:
        entry: dict[str, object] = {"event": "failure", "code": code}
        if error is not None:
            entry.update(describe(error))
        # Diagnostics are best effort after startup; they never change a result.
        self._write(entry)

    def _write(self, entry: dict[str, object]) -> bool:
        line = json.dumps(
            {
                "time": datetime.now(UTC).isoformat(timespec="milliseconds"),
                "pid": os.getpid(),
                **entry,
            },
            separators=(",", ":"),
        )
        try:
            descriptor = os.open(
                self._path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600
            )
            with os.fdopen(descriptor, "a", encoding="utf-8") as stream:
                stream.write(line + "\n")
        except OSError:
            return False
        return True
