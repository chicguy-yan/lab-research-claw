"""Sessions API — 5 endpoints for session CRUD + history.

Phase 5.3: All endpoints are now workspace-aware via X-Workspace-Id header.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from api.runtime_context import get_runtime

router = APIRouter(prefix="/sessions", tags=["sessions"])


class CreateSessionBody(BaseModel):
    title: str = "未命名会话"


class RenameSessionBody(BaseModel):
    title: str


@router.get("")
async def list_sessions(request: Request):
    """GET /api/sessions — list sessions sorted by updated_at desc."""
    rt = get_runtime(request)
    return {"sessions": rt.session_manager.list_sessions()}


@router.post("")
async def create_session(body: CreateSessionBody, request: Request):
    """POST /api/sessions — create a new session."""
    rt = get_runtime(request)
    meta = rt.session_manager.create_session(title=body.title)
    return meta


@router.put("/{session_id}")
async def rename_session(session_id: str, body: RenameSessionBody, request: Request):
    """PUT /api/sessions/{session_id} — rename a session."""
    rt = get_runtime(request)
    result = rt.session_manager.rename_session(session_id, body.title)
    if result is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return result


@router.delete("/{session_id}")
async def delete_session(session_id: str, request: Request):
    """DELETE /api/sessions/{session_id} — delete a session."""
    rt = get_runtime(request)
    deleted = rt.session_manager.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"deleted": True}


@router.get("/{session_id}/history")
async def get_history(session_id: str, request: Request):
    """GET /api/sessions/{session_id}/history — get message history."""
    rt = get_runtime(request)
    messages = rt.session_manager.load_session(session_id)
    return {"session_id": session_id, "messages": messages}
