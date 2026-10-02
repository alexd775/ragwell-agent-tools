from __future__ import annotations

import copy
import json
from typing import Any

import pytest
from mcp.types import TextContent
from ragwell.types import ChunkPart, SearchResponse

from ragwell_agent_tools.evidence import project_evidence, result_bytes

from .helpers import PROJECT_ID, result_data, search_body


def test_multipart_evidence_is_not_duplicated_or_relabelled() -> None:
    response = SearchResponse.from_dict(search_body())
    output = project_evidence(
        response, project_id=PROJECT_ID, k=5, max_output_bytes=24000
    )
    data = result_data(output)
    hit = data["matches"][0]
    assert "content" not in hit
    assert "generation_id" not in hit
    assert "url" not in hit
    assert [p["kind"] for p in hit["parts"]] == ["context", "separator", "evidence"]
    assert hit["parts"][2]["start_line"] == 3
    assert hit["parts"][2]["span"]["start_offset"] == 18
    assert hit["document_version_id"] == str(response.items[0].document_version_id)
    assert data["source_expansion_available"] is False
    assert data["truncated"] is False
    assert isinstance(output.content[0], TextContent)
    assert json.loads(output.content[0].text) == data


@pytest.mark.parametrize("budget", [2048, 4096, 24000])
def test_full_serialized_result_is_bounded_with_original_coordinates(
    budget: int,
) -> None:
    raw = search_body(text='😀\n"\\' * 5000)
    raw["items"] = [copy.deepcopy(raw["items"][0]) for _ in range(5)]
    response = SearchResponse.from_dict(raw)
    result = project_evidence(
        response, project_id=PROJECT_ID, k=5, max_output_bytes=budget
    )
    data = result_data(result)
    assert result_bytes(result) <= budget
    assert data["truncated"] is True
    assert data["total_matches"] == 5
    assert data["omitted_matches"] + len(data["matches"]) == 5
    for hit in data["matches"]:
        part = hit["parts"][2]
        assert part["span"] == {
            "source_ordinal": 0,
            "start_offset": 18,
            "end_offset": 73,
        }
        assert part["original_text_chars"] == len(raw["items"][0]["parts"][2]["text"])
        assert part["truncated"] is True
        assert raw["items"][0]["parts"][2]["text"].startswith(part["text"])
    assert response.items[0].parts[2].text == raw["items"][0]["parts"][2]["text"]


def test_empty_results_are_successful_and_not_missing_permissions() -> None:
    raw = search_body()
    raw["items"] = []
    result = project_evidence(
        SearchResponse.from_dict(raw),
        project_id=PROJECT_ID,
        k=5,
        max_output_bytes=24000,
    )
    data = result_data(result)
    assert not result.is_error
    assert data["matches"] == []
    assert not data["truncated"]


def test_single_citation_fallback_preserves_source_coordinates() -> None:
    raw = search_body()
    raw["items"][0]["parts"] = []
    raw["items"][0]["citation"] = {
        "kind": "text",
        "source_filename": "travel-policy.md",
        "start_line": 3,
        "end_line": 3,
        "start_offset": 18,
        "end_offset": 73,
    }
    result = project_evidence(
        SearchResponse.from_dict(raw),
        project_id=PROJECT_ID,
        k=5,
        max_output_bytes=24000,
    )
    hit = result_data(result)["matches"][0]
    assert hit["parts"][0]["text"] == raw["items"][0]["content"]
    assert hit["citation"]["start_offset"] == 18


def test_fields_added_by_a_later_sdk_are_dropped_not_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    released = ChunkPart.to_dict

    def later_sdk_to_dict(self: ChunkPart) -> dict[str, Any]:
        fields = released(self)
        if isinstance(fields.get("span"), dict):
            fields["span"] = {**fields["span"], "future_field": "span"}
        return {**fields, "future_field": "part"}

    monkeypatch.setattr(ChunkPart, "to_dict", later_sdk_to_dict)
    raw = search_body()
    raw["items"][0]["citation"] = {
        "kind": "text",
        "source_filename": "travel-policy.md",
        "start_line": 3,
        "end_line": 3,
        "start_offset": 18,
        "end_offset": 73,
        "future_field": "citation",
    }
    result = project_evidence(
        SearchResponse.from_dict(raw),
        project_id=PROJECT_ID,
        k=5,
        max_output_bytes=24000,
    )
    assert not result.is_error
    assert "future_field" not in result.model_dump_json()
    hit = result_data(result)["matches"][0]
    assert hit["parts"][2]["span"]["start_offset"] == 18
    assert hit["citation"]["start_offset"] == 18


def test_omitted_source_parts_are_disclosed() -> None:
    raw = search_body()
    raw["items"][0]["parts"] *= 20
    result = project_evidence(
        SearchResponse.from_dict(raw),
        project_id=PROJECT_ID,
        k=5,
        max_output_bytes=65536,
    )
    hit = result_data(result)["matches"][0]
    assert hit["omitted_parts"] == 28
    assert hit["truncated"]
