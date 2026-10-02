"""Bounded evidence projection with original identities and source coordinates."""

from __future__ import annotations

import json
from typing import Any, Literal
from uuid import UUID

from mcp.types import CallToolResult, TextContent
from pydantic import BaseModel, ConfigDict, Field
from ragwell.types import SearchResponse


class OutputModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class SourceSpan(OutputModel):
    source_ordinal: int = Field(ge=0)
    start_offset: int = Field(ge=0)
    end_offset: int = Field(ge=0)
    block_id: str | None = Field(default=None, max_length=512)
    row: int | None = None
    column: int | None = None
    region: list[float] | None = Field(default=None, max_length=4)


class EvidencePart(OutputModel):
    kind: Literal["evidence", "context", "separator"]
    text: str
    original_text_chars: int
    truncated: bool
    source_id: UUID | None = None
    page_number: int | None = None
    start_line: int | None = None
    end_line: int | None = None
    span: SourceSpan | None = None


class Citation(OutputModel):
    kind: Literal["page", "text"]
    start_offset: int = Field(ge=0)
    end_offset: int = Field(ge=0)
    page_number: int | None = None
    start_line: int | None = None
    end_line: int | None = None


class Scores(OutputModel):
    final: float
    text: float | None
    vector: float | None
    hybrid: float | None = None
    rerank: float | None = None
    rerank_confidence: float | None = None


class EvidenceMatch(OutputModel):
    rank: int = Field(ge=1)
    chunk_id: UUID
    document_id: UUID
    document_version_id: UUID
    source_filename: str = Field(max_length=1_024)
    representation_version: str = Field(max_length=128)
    scores: Scores
    citation: Citation | None = None
    parts: list[EvidencePart]
    omitted_parts: int = 0
    truncated: bool = False


class SearchEvidence(OutputModel):
    status: Literal["ok"] = "ok"
    project_id: UUID
    retrieval_id: UUID
    retrieval_version: str = Field(max_length=128)
    matches: list[EvidenceMatch]
    total_matches: int
    omitted_matches: int = 0
    truncated: bool = False
    source_text_is_untrusted: Literal[True] = True
    source_expansion_available: Literal[False] = False


def as_tool_result(payload: BaseModel, *, is_error: bool = False) -> CallToolResult:
    data = payload.model_dump(mode="json", exclude_none=True)
    # A text fallback supports hosts that do not consume structuredContent.
    # The size gate counts both representations; text appears once per payload.
    fallback = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return CallToolResult(
        content=[TextContent(text=fallback)],
        structured_content=data,
        is_error=is_error,
    )


def result_bytes(result: CallToolResult) -> int:
    """Serialized result budget, including structured/text fallback duplication."""
    return len(result.model_dump_json(by_alias=True, exclude_none=True).encode("utf-8"))


def known_fields(model: type[OutputModel], raw: dict[str, Any]) -> dict[str, Any]:
    """Forward only reviewed fields; later SDK releases may add others."""
    return {name: raw[name] for name in model.model_fields if name in raw}


def project_evidence(
    response: SearchResponse, *, project_id: UUID, k: int, max_output_bytes: int
) -> CallToolResult:
    matches: list[EvidenceMatch] = []
    for hit in response.items[:k]:
        parts: list[EvidencePart] = []
        for part in hit.parts[:32]:
            raw_part = part.to_dict()
            fields = known_fields(EvidencePart, raw_part)
            if isinstance(raw_part.get("span"), dict):
                fields["span"] = known_fields(SourceSpan, raw_part["span"])
            original = fields["text"]
            fields.update(
                text=original[:1_500],
                original_text_chars=len(original),
                truncated=len(original) > 1_500,
            )
            parts.append(EvidencePart.model_validate(fields))
        if not hit.parts:
            parts.append(
                EvidencePart(
                    kind="evidence",
                    text=hit.content[:1_500],
                    original_text_chars=len(hit.content),
                    truncated=len(hit.content) > 1_500,
                )
            )
        citation = None
        if hit.citation is not None:
            citation = Citation.model_validate(
                known_fields(Citation, hit.citation.to_dict())
            )
        scores = Scores.model_validate(known_fields(Scores, hit.scores.to_dict()))
        match = EvidenceMatch(
            rank=hit.rank,
            chunk_id=hit.chunk_id,
            document_id=hit.document_id,
            document_version_id=hit.document_version_id,
            source_filename=hit.source_filename,
            representation_version=hit.representation_version,
            scores=scores,
            citation=citation,
            parts=parts,
            omitted_parts=max(0, len(hit.parts) - len(parts)),
            truncated=len(hit.parts) > len(parts) or any(p.truncated for p in parts),
        )
        matches.append(match)
    output = SearchEvidence(
        project_id=project_id,
        retrieval_id=response.retrieval_id,
        retrieval_version=response.retrieval_version,
        matches=matches,
        total_matches=len(response.items),
        omitted_matches=len(response.items) - len(matches),
        truncated=len(response.items) > len(matches)
        or any(m.truncated for m in matches),
    )
    while result_bytes(result := as_tool_result(output)) > max_output_bytes:
        output.truncated = True
        candidates = [(len(p.text), m, p) for m in output.matches for p in m.parts]
        longest = max(candidates, key=lambda item: item[0], default=None)
        if longest is not None and longest[0] > 0:
            length, match, output_part = longest
            output_part.text = output_part.text[: length // 2]
            output_part.truncated = True
            match.truncated = True
        elif output.matches:
            output.matches.pop()
            output.omitted_matches += 1
        else:
            raise ValueError("Evidence metadata exceeds the configured output budget")
    return result
