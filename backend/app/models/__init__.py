"""
becomussy – Model registry.

All ORM models are imported here so Alembic autogenerate and
init_db can discover them via Base.metadata.
"""

from app.models.audit import AuditEvent  # noqa: F401
from app.models.memory import MemoryItem, MemoryLink  # noqa: F401
from app.models.thread import Thread  # noqa: F401
from app.models.project import Project, Commitment  # noqa: F401
from app.models.journal import JournalEntry  # noqa: F401
from app.models.self_model import SelfModelVersion  # noqa: F401
from app.models.revision import RevisionProposal  # noqa: F401
from app.models.governance import ApprovalDecision  # noqa: F401
