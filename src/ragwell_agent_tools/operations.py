"""Curated input and operation boundary, independent of the MCP transport."""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field, field_validator
from ragwell.types import SearchResponse


class SearchInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, hide_input_in_errors=True)

    query: str = Field(min_length=1, max_length=2_000)
    k: int = Field(default=5, ge=1, le=5)

    @field_validator("query")
    @classmethod
    def reject_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("query must contain text")
        return value


class SearchOperations(Protocol):
    async def search(self, request: SearchInput) -> SearchResponse:
        """Perform exactly one search under the configured authority."""
        ...
