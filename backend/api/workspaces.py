"""Workspaces API - workspace CRUD plus bootstrap lifecycle."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from api.runtime_context import get_registry
from runtime.bootstrap_runner import BOOTSTRAP_SESSION_ID, BootstrapRunner

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


class CreateWorkspaceBody(BaseModel):
    workspace_id: str = Field(..., pattern=r"^[a-zA-Z0-9_-]+$", max_length=64)
    display_name: str = Field(..., max_length=128)
    description: str = ""


class RenameWorkspaceBody(BaseModel):
    display_name: str = Field(..., max_length=128)
    description: str | None = None


@router.get("")
async def list_workspaces(request: Request):
    registry = get_registry(request)
    return {"workspaces": registry.list_workspaces()}


@router.post("")
async def create_workspace(body: CreateWorkspaceBody, request: Request):
    registry = get_registry(request)
    try:
        manifest = registry.create_workspace(
            workspace_id=body.workspace_id,
            display_name=body.display_name,
            description=body.description,
        )
    except FileExistsError:
        raise HTTPException(409, f"Workspace already exists: {body.workspace_id}")
    return manifest


@router.put("/{workspace_id}")
async def rename_workspace(workspace_id: str, body: RenameWorkspaceBody, request: Request):
    registry = get_registry(request)
    try:
        manifest = registry.rename_workspace(
            workspace_id=workspace_id,
            display_name=body.display_name,
            description=body.description,
        )
    except FileNotFoundError:
        raise HTTPException(404, f"Workspace not found: {workspace_id}")
    return manifest


@router.get("/{workspace_id}/manifest")
async def get_manifest(workspace_id: str, request: Request):
    registry = get_registry(request)
    manifest = registry.load_manifest(workspace_id)
    if not manifest:
        raise HTTPException(404, f"Workspace not found: {workspace_id}")
    return manifest


@router.post("/{workspace_id}/bootstrap/start")
async def start_bootstrap(workspace_id: str, request: Request):
    """Start first-run bootstrap and return the onboarding question."""
    registry = get_registry(request)
    manifest = registry.load_manifest(workspace_id)
    if not manifest:
        raise HTTPException(404, f"Workspace not found: {workspace_id}")

    status = manifest.get("bootstrap_status", "completed")
    if status == "completed":
        raise HTTPException(400, "Workspace bootstrap already completed")
    if status == "running":
        raise HTTPException(409, "Workspace bootstrap already running")
    if status not in ("pending", "failed"):
        raise HTTPException(400, f"Unexpected bootstrap_status: {status}")

    updated = registry.update_bootstrap_status(workspace_id, "running")
    rt = registry.get_runtime(workspace_id)
    runner = BootstrapRunner(workspace_id, rt.workspace_dir)
    start_result = runner.start(rt.session_manager)
    logger.info("Bootstrap started for workspace: %s", workspace_id)
    return {
        "workspace_id": workspace_id,
        "bootstrap_status": "running",
        "session_id": BOOTSTRAP_SESSION_ID,
        "bootstrap_prompt": start_result.prompt,
        "manifest": updated,
    }

