"""
becomussy – security utilities.

MVP uses header-based auth (X-User-Id / X-User-Role).
Replace with real OAuth / JWT in production.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Callable

from fastapi import Depends, Header, HTTPException, status


# ── Roles ───────────────────────────────────────────────────────────────
class Role(str, enum.Enum):
    agent_runtime = "agent_runtime"
    steward = "steward"
    reviewer = "reviewer"
    admin = "admin"
    observer = "observer"


# ── Current user representation ─────────────────────────────────────────
@dataclass(frozen=True)
class CurrentUser:
    user_id: str
    role: Role


# ── Dependency: extract current user from headers ───────────────────────
async def get_current_user(
    x_user_id: str = Header(default="anonymous"),
    x_user_role: str = Header(default="observer"),
) -> CurrentUser:
    """Read identity from request headers (MVP – no real auth)."""
    try:
        role = Role(x_user_role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role: {x_user_role}. Must be one of {[r.value for r in Role]}",
        )
    return CurrentUser(user_id=x_user_id, role=role)


# ── Dependency factory: role gate ───────────────────────────────────────
def require_role(*allowed_roles: Role) -> Callable:
    """Return a FastAPI dependency that enforces the caller has one of *allowed_roles*."""

    async def _check(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role.value}' is not authorized. Required: {[r.value for r in allowed_roles]}",
            )
        return user

    return _check
