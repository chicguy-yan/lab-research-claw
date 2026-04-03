"""Files API — 4 endpoints for workspace file operations.

Endpoints:
    GET  /api/files?path=...                  — read file content
    POST /api/files                           — save file {path, content}
    GET  /api/files/tree?path=...&max_depth=3 — directory tree
    GET  /api/files/preview?path=...&max_chars=500 — file preview (truncated)

All paths are relative to the current workspace root.
Path security enforced via resolve_safe_path (PRD §6.9).

Phase 5.3: workspace-aware via X-Workspace-Id header.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from api.runtime_context import get_runtime
from graph.path_utils import PathSecurityError, resolve_safe_path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/files", tags=["files"])


class SaveFileBody(BaseModel):
    path: str
    content: str


def _get_workspace(request: Request):
    """Get the current workspace directory from runtime context."""
    rt = get_runtime(request)
    return rt.workspace_dir


# ── GET /api/files?path=... ──────────────────────────────────────────

@router.get("")
async def read_file(request: Request, path: str = Query(..., description="Relative path")):
    """Read a file from the workspace."""
    workspace = _get_workspace(request)
    try:
        resolved = resolve_safe_path(workspace, path)
    except PathSecurityError as e:
        raise HTTPException(status_code=403, detail=str(e))

    if not resolved.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    if resolved.is_dir():
        raise HTTPException(status_code=400, detail=f"Path is a directory: {path}")

    try:
        content = resolved.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail=f"File is not UTF-8 text: {path}")

    return {"path": path, "content": content}


# ── POST /api/files ──────────────────────────────────────────────────

@router.post("")
async def save_file(body: SaveFileBody, request: Request):
    """Save (create or overwrite) a file in the workspace."""
    workspace = _get_workspace(request)
    try:
        resolved = resolve_safe_path(workspace, body.path, require_writable=True)
    except PathSecurityError as e:
        raise HTTPException(status_code=403, detail=str(e))

    # Ensure parent directory exists
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(body.content, encoding="utf-8")
    logger.info("Saved file: %s", body.path)
    return {"path": body.path, "saved": True}


# ── GET /api/files/tree?path=...&max_depth=3 ─────────────────────────

@router.get("/tree")
async def file_tree(
    request: Request,
    path: str = Query("", description="Relative subdirectory (empty = root)"),
    max_depth: int = Query(3, ge=1, le=10),
):
    """Return a recursive directory tree as nested dicts."""
    workspace = _get_workspace(request)
    root_path = path or "."
    try:
        resolved = resolve_safe_path(workspace, root_path)
    except PathSecurityError as e:
        raise HTTPException(status_code=403, detail=str(e))

    if not resolved.exists():
        raise HTTPException(status_code=404, detail=f"Path not found: {path}")
    if not resolved.is_dir():
        raise HTTPException(status_code=400, detail=f"Path is not a directory: {path}")

    tree = _build_tree(resolved, workspace, max_depth, current_depth=0)
    return {"path": path or "/", "tree": tree}


def _build_tree(directory, workspace, max_depth: int, current_depth: int) -> list[dict]:
    """Recursively build a directory tree structure."""
    entries = []
    try:
        children = sorted(directory.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except PermissionError:
        return entries

    for child in children:
        rel = child.relative_to(workspace.resolve()).as_posix()
        # Keep system skills visible in the frontend, while still hiding
        # unrelated internal template files that start with "_".
        if child.name.startswith("."):
            continue
        if child.name.startswith("_") and rel != "skills/_system" and not rel.startswith("skills/_system/"):
            continue

        entry = {"name": child.name, "path": rel, "type": "dir" if child.is_dir() else "file"}

        if child.is_dir() and current_depth < max_depth - 1:
            entry["children"] = _build_tree(child, workspace, max_depth, current_depth + 1)

        entries.append(entry)
    return entries


# ── GET /api/files/preview?path=...&max_chars=500 ────────────────────

@router.get("/preview")
async def file_preview(
    request: Request,
    path: str = Query(..., description="Relative path"),
    max_chars: int = Query(500, ge=100, le=10000),
):
    """Return a truncated preview of a text file."""
    workspace = _get_workspace(request)
    try:
        resolved = resolve_safe_path(workspace, path)
    except PathSecurityError as e:
        raise HTTPException(status_code=403, detail=str(e))

    if not resolved.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    if resolved.is_dir():
        raise HTTPException(status_code=400, detail=f"Path is a directory: {path}")

    try:
        content = resolved.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail=f"File is not UTF-8 text: {path}")

    truncated = len(content) > max_chars
    return {
        "path": path,
        "preview": content[:max_chars],
        "truncated": truncated,
        "total_chars": len(content),
    }
