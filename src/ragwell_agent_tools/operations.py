"""Curated input and operation boundary, independent of the MCP transport."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator
from ragwell.types import (
    DocumentSourcePreview,
    MachineCapabilitiesResponse,
    SearchResponse,
)


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


class FetchSourceInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, hide_input_in_errors=True)

    document_id: UUID
    document_version_id: UUID
    generation_id: UUID
    source_id: UUID
    offset: int = Field(default=0, ge=0, le=2_147_483_646)
    limit: int = Field(default=1_500, ge=1, le=4_000)

    @field_validator(
        "document_id",
        "document_version_id",
        "generation_id",
        "source_id",
        mode="before",
    )
    @classmethod
    def parse_identity(cls, value: object) -> UUID:
        if isinstance(value, UUID):
            return value
        if isinstance(value, str):
            return UUID(value)
        raise ValueError("source identities must be UUIDs")

    def reference(self) -> tuple[UUID, UUID, UUID, UUID]:
        return (
            self.document_id,
            self.document_version_id,
            self.generation_id,
            self.source_id,
        )


class SearchOperations(Protocol):
    async def capabilities(self) -> MachineCapabilitiesResponse:
        """Read the current key's grants without searching or broadening authority."""
        ...

    async def search(self, request: SearchInput) -> SearchResponse:
        """Perform exactly one search under the configured authority."""
        ...

    async def fetch_source(self, request: FetchSourceInput) -> DocumentSourcePreview:
        """Read one bounded source slice under the configured authority."""
        ...
