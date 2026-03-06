"""
becomussy – shared Pydantic schemas & enumerations.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

# ── Enumerations ────────────────────────────────────────────────────────


class StatusEnum(str, enum.Enum):
    active = "active"
    archived = "archived"
    deprecated = "deprecated"
    deleted_soft = "deleted_soft"


class ApprovalStateEnum(str, enum.Enum):
    not_required = "not_required"
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    deferred = "deferred"


class ConfidenceLevelEnum(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class MemoryTypeEnum(str, enum.Enum):
    episodic = "episodic"
    semantic = "semantic"
    autobiographical = "autobiographical"
    working = "working"
    relational = "relational"


class RevisionStageEnum(str, enum.Enum):
    observation = "observation"
    interpretation = "interpretation"
    candidate_revision = "candidate_revision"
    evidence_collection = "evidence_collection"
    simulation_review = "simulation_review"
    approval = "approval"
    adoption = "adoption"
    monitoring = "monitoring"
    closed = "closed"


class RiskClassEnum(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class VisibilityEnum(str, enum.Enum):
    private_runtime = "private_runtime"
    steward_visible = "steward_visible"
    shared = "shared"
    restricted = "restricted"


class UserRoleEnum(str, enum.Enum):
    agent_runtime = "agent_runtime"
    steward = "steward"
    reviewer = "reviewer"
    admin = "admin"
    observer = "observer"


# ── Shared value-objects ────────────────────────────────────────────────


class ProvenanceSchema(BaseModel):
    """Lightweight provenance information attached to many entities."""

    model_config = ConfigDict(extra="forbid")

    source_kind: str
    source_ref: str
    extra: dict[str, Any] | None = None


# ── Pagination wrapper ──────────────────────────────────────────────────

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Envelope for paginated list responses."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    items: list[T]
    total: int
    limit: int
    offset: int


# ── Audit event schemas ────────────────────────────────────────────────


class AuditEventCreate(BaseModel):
    """Schema for creating a new audit event."""

    model_config = ConfigDict(extra="forbid")

    event_type: str
    entity_type: str
    entity_id: uuid.UUID | None = None
    actor: str
    actor_type: str
    before_json: dict[str, Any] | None = None
    after_json: dict[str, Any] | None = None
    rationale: str | None = None
    provenance_json: dict[str, Any] = Field(default_factory=dict)
    approval_state: ApprovalStateEnum | None = None


class AuditEventRead(BaseModel):
    """Schema returned when reading an audit event."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    occurred_at: datetime
    actor: str
    actor_type: str
    event_type: str
    entity_type: str
    entity_id: uuid.UUID | None = None
    before_json: dict[str, Any] | None = None
    after_json: dict[str, Any] | None = None
    rationale: str | None = None
    provenance_json: dict[str, Any]
    approval_state: str | None = None
    immutable: bool
