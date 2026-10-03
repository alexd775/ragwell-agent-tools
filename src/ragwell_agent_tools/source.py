"""Bounded source reads that preserve the returned generation and version."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from mcp.types import CallToolResult
from pydantic import Field
from ragwell.types import DocumentSourcePreview

from .evidence import OutputModel, as_tool_result, known_fields, result_bytes
from .operations import FetchSourceInput


class SourceEvidence(OutputModel):
    status: Literal["ok"] = "ok"
    project_id: UUID
    document_id: UUID
    document_version_id: UUID
    generation_id: UUID
    source_id: UUID
    coordinate_kind: Literal["page", "text"]
    source_ordinal: int = Field(ge=0)
    page_number: int | None = None
    character_count: int = Field(ge=0)
    start_offset: int = Field(ge=0)
    end_offset: int = Field(ge=0)
    content: str
    next_offset: int | None = Field(default=None, ge=0)
    truncated: bool = False
    source_text_is_untrusted: Literal[True] = True


def project_source(
    response: DocumentSourcePreview,
    request: FetchSourceInput,
    *,
    project_id: UUID,
    max_output_bytes: int,
) -> CallToolResult:
    output = SourceEvidence.model_validate(
        {**known_fields(SourceEvidence, response.to_dict()), "project_id": project_id}
    )
    expected_end = min(output.character_count, request.offset + request.limit)
    if (
        (
            output.document_id,
            output.document_version_id,
            output.generation_id,
            output.source_id,
        )
        != request.reference()
        or output.start_offset != request.offset
        or output.end_offset != expected_end
        or output.character_count < request.offset
        or len(output.content) != output.end_offset - output.start_offset
        or output.next_offset
        != (expected_end if expected_end < output.character_count else None)
    ):
        raise ValueError("Source response identity or coordinates did not match")
    while result_bytes(result := as_tool_result(output)) > max_output_bytes:
        if not output.content:
            raise ValueError("Source metadata exceeds the configured output budget")
        output.content = output.content[: len(output.content) // 2]
        output.end_offset = output.start_offset + len(output.content)
        output.next_offset = output.end_offset
        output.truncated = True
    return result
