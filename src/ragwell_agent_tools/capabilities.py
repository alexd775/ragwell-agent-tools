"""Bounded projection of current grants onto this connection's curated tools."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator
from ragwell.types import GrantableApiKeyScope, MachineCapabilitiesResponse


class ProjectGrant(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, hide_input_in_errors=True)

    project_id: UUID
    scopes: list[GrantableApiKeyScope] = Field(min_length=1, max_length=13)

    @field_validator("scopes")
    @classmethod
    def unique_scopes(
        cls, value: list[GrantableApiKeyScope]
    ) -> list[GrantableApiKeyScope]:
        if len(set(value)) != len(value):
            raise ValueError("duplicate scopes")
        return value


class GrantSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, hide_input_in_errors=True)

    projects: list[ProjectGrant] = Field(min_length=1, max_length=100)

    @field_validator("projects")
    @classmethod
    def unique_projects(cls, value: list[ProjectGrant]) -> list[ProjectGrant]:
        if len({project.project_id for project in value}) != len(value):
            raise ValueError("duplicate projects")
        return value


def tools_for_project(
    response: MachineCapabilitiesResponse, project_id: UUID
) -> frozenset[str]:
    snapshot = GrantSnapshot.model_validate(
        {
            "projects": [
                {"project_id": p.project_id, "scopes": p.scopes}
                for p in response.projects
            ]
        }
    )
    scopes = next(
        (p.scopes for p in snapshot.projects if p.project_id == project_id), []
    )
    tools: set[str] = set()
    if GrantableApiKeyScope.RETRIEVALSEARCH in scopes:
        tools.add("ragwell_search")
        if GrantableApiKeyScope.DOCUMENTREAD in scopes:
            tools.add("ragwell_fetch_source")
    return frozenset(tools)
