"""Runtime context helper — resolve workspace from request.

Phase 5.3: Unified entry point for all APIs to get WorkspaceRuntime.
Priority: body workspace_id > X-Workspace-Id header > default fallback.
"""

from __future__ import annotations

from fastapi import HTTPException, Request

from runtime.workspace_registry import WorkspaceRuntime, WorkspaceRuntimeRegistry


def get_registry(request: Request) -> WorkspaceRuntimeRegistry:
    """Get the WorkspaceRuntimeRegistry from app state."""
    return request.app.state.workspace_registry


def resolve_workspace_id(request: Request, body_workspace_id: str | None = None) -> str:
    """Resolve workspace_id from body, header, or default."""
    if body_workspace_id and body_workspace_id.strip():
        return body_workspace_id.strip()
    header_val = request.headers.get("X-Workspace-Id", "").strip()
    if header_val:
        return header_val
    return "default"


def get_runtime(request: Request, body_workspace_id: str | None = None) -> WorkspaceRuntime:
    """Resolve workspace and return its runtime. Raises 404 if not found."""
    registry = get_registry(request)
    wid = resolve_workspace_id(request, body_workspace_id)
    try:
        return registry.get_runtime(wid)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Workspace not found: {wid}")
