"""Explicit process configuration; credentials never appear in representations."""

from __future__ import annotations

import math
import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit
from uuid import UUID


class SettingsError(ValueError):
    """A sanitized configuration failure."""


@dataclass(frozen=True, slots=True)
class Settings:
    base_url: str
    project_id: UUID
    api_key: str = field(repr=False)
    timeout_seconds: float = 20.0
    max_output_bytes: int = 24_000
    max_searches: int = 50
    allow_local_http: bool = False
    debug_log: Path | None = None

    def __post_init__(self) -> None:
        try:
            url = urlsplit(self.base_url)
            _ = url.port
        except ValueError:
            raise SettingsError("RAGWELL_BASE_URL must be a valid API origin") from None
        local_http = (
            self.allow_local_http
            and url.scheme == "http"
            and url.hostname in {"localhost", "127.0.0.1", "::1"}
        )
        if (
            not url.hostname
            or (url.scheme != "https" and not local_http)
            or url.username is not None
            or url.password is not None
            or url.path not in {"", "/"}
            or url.query
            or url.fragment
            or any(char.isspace() for char in self.base_url)
        ):
            raise SettingsError("RAGWELL_BASE_URL must be an HTTPS API origin")
        if not isinstance(self.project_id, UUID):
            raise SettingsError("RAGWELL_PROJECT_ID must be a UUID")
        if (
            not self.api_key
            or len(self.api_key) > 512
            or any(not 33 <= ord(char) <= 126 for char in self.api_key)
        ):
            raise SettingsError("RAGWELL_API_KEY must be a nonempty credential")
        if not math.isfinite(self.timeout_seconds) or not (
            0 < self.timeout_seconds <= 120
        ):
            raise SettingsError("RAGWELL_TIMEOUT_SECONDS must be between 0 and 120")
        if not 2_048 <= self.max_output_bytes <= 65_536:
            raise SettingsError("RAGWELL_MAX_OUTPUT_BYTES must be 2048 through 65536")
        if not 1 <= self.max_searches <= 10_000:
            raise SettingsError("RAGWELL_MAX_SEARCHES must be 1 through 10000")
        if self.debug_log is not None and not self.debug_log.is_absolute():
            raise SettingsError("RAGWELL_DEBUG_LOG must be an absolute file path")

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> Settings:
        values = os.environ if environ is None else environ
        required = ("RAGWELL_BASE_URL", "RAGWELL_PROJECT_ID", "RAGWELL_API_KEY")
        for name in required:
            if not values.get(name):
                raise SettingsError(f"Set {name} before starting Ragwell tools")
        try:
            project_id = UUID(values["RAGWELL_PROJECT_ID"])
        except ValueError:
            raise SettingsError("RAGWELL_PROJECT_ID must be a UUID") from None
        try:
            timeout = float(values.get("RAGWELL_TIMEOUT_SECONDS", "20"))
            output = int(values.get("RAGWELL_MAX_OUTPUT_BYTES", "24000"))
            searches = int(values.get("RAGWELL_MAX_SEARCHES", "50"))
        except ValueError:
            raise SettingsError("Ragwell limit settings must be numeric") from None
        allow_http = values.get("RAGWELL_ALLOW_LOCAL_HTTP", "false")
        if allow_http not in {"true", "false"}:
            raise SettingsError("RAGWELL_ALLOW_LOCAL_HTTP must be true or false")
        debug_log = values.get("RAGWELL_DEBUG_LOG")
        return cls(
            base_url=values["RAGWELL_BASE_URL"].rstrip("/"),
            project_id=project_id,
            api_key=values["RAGWELL_API_KEY"],
            timeout_seconds=timeout,
            max_output_bytes=output,
            max_searches=searches,
            allow_local_http=allow_http == "true",
            debug_log=Path(debug_log) if debug_log else None,
        )
