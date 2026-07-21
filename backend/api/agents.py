"""Agents API — backward-compatible wrapper over Workspaces API.

Phase 5.3: Internally delegates to WorkspaceRuntimeRegistry.
New code should use /api/workspaces instead.

Endpoints:
    GET  /api/agents            — list all Agent workspaces
    POST /api/agents            — create a new Agent workspace (delegates to registry)
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from api.runtime_context import get_registry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["agents"])


class CreateAgentBody(BaseModel):
    agent_id: str = Field(..., pattern=r"^[a-zA-Z0-9_-]+$", max_length=64)
    name: str = Field(..., max_length=128)
    description: str = ""


# ── GET /api/agents ──────────────────────────────────────────────────

@router.get("")
async def list_agents(request: Request):
    """List all Agent workspaces under .openclaw/.

    Phase 5.3: delegates to registry.list_workspaces() and maps to agent format.
    """
    registry = get_registry(request)
    workspaces = registry.list_workspaces()
    agents = []
    for ws in workspaces:
        agents.append({
            "agent_id": ws["workspace_id"],
            "name": ws["display_name"],
            "workspace_dir": ws["workspace_dir"],
            "has_identity": True,
            "_note": "This endpoint is deprecated. Use GET /api/workspaces instead.",
        })
    return {"agents": agents}


# ── POST /api/agents ─────────────────────────────────────────────────

@router.post("")
async def create_agent(body: CreateAgentBody, request: Request):
    """Create a new Agent workspace.

    Phase 5.3: delegates to registry.create_workspace() for consistent provision.
    """
    registry = get_registry(request)
    try:
        manifest = registry.create_workspace(
            workspace_id=body.agent_id,
            display_name=body.name,
            description=body.description,
        )
    except FileExistsError:
        raise HTTPException(
            status_code=409,
            detail=f"Agent workspace already exists: {body.agent_id}",
        )

    # Also write IDENTITY.md for backward compat
    workspace_dir = registry.resolve_workspace_dir(body.agent_id)
    identity_content = f"# {body.name}\n\n{body.description}\n"
    identity_path = workspace_dir / "IDENTITY.md"
    identity_path.write_text(identity_content, encoding="utf-8")

    logger.info("Created agent workspace (compat): %s", body.agent_id)

    return {
        "agent_id": body.agent_id,
        "name": body.name,
        "workspace_dir": str(workspace_dir),
        "created_at": manifest.get("created_at", ""),
        "_note": "This endpoint is deprecated. Use POST /api/workspaces instead.",
    }
