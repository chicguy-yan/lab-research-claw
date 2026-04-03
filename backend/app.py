"""FastAPI application entrypoint for Experimental-Research-OpenClaw.

Phase 5.3: Startup now initializes WorkspaceRuntimeRegistry instead of
global singleton SessionManager/AgentManager.
"""

from __future__ import annotations

import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config as cfg
from api.agents import router as agents_router
from api.chat import router as chat_router
from api.files import router as files_router
from api.sessions import router as sessions_router

try:
    from runtime.workspace_registry import WorkspaceRuntimeRegistry
except ModuleNotFoundError as exc:
    if exc.name == "langchain_openai":
        raise RuntimeError(
            "Missing dependency 'langchain_openai'. "
            "You are likely running backend/app.py with the wrong Python interpreter. "
            "Activate backend/.venv first, then run 'python app.py'."
        ) from exc
    raise

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8002
BACKEND_URL = f"http://127.0.0.1:{DEFAULT_PORT}"

app = FastAPI(title="Experimental-Research-OpenClaw", version="0.1.0")

# Dev CORS policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": "ok", "service": "experimental-research-openclaw-backend"}


def ensure_default_workspace() -> None:
    """Initialize .openclaw/workspace-default from templates if missing.

    If workspace already exists, migrate missing directories/files from
    the template so that template additions (e.g. assets/uploads/) are
    propagated to older workspaces.

    NOTE: Phase 5.3 — this is now a thin wrapper that delegates to the registry.
    Kept for backward compatibility during transition; will be removed once
    all callers use the registry directly.
    """
    # Handled by registry.ensure_default_workspace() in on_startup
    pass


@app.on_event("startup")
async def on_startup() -> None:
    # 1) Create registry and initialize shared resources (one LLM, one FetchURLTool)
    registry = WorkspaceRuntimeRegistry()
    registry.initialize_shared()

    # 2) Ensure default workspace exists (with manifest + template migration)
    registry.ensure_default_workspace()

    # 3) Pre-warm default workspace runtime
    registry.get_runtime("default")

    # 4) Mount into app state
    app.state.workspace_registry = registry
    app.state.runtime_config = cfg.load_config()

    # Phase 5.3 backward compat: keep these for any code that still reads them
    default_rt = registry.get_runtime("default")
    app.state.session_manager = default_rt.session_manager
    app.state.agent_manager = None  # No longer a single AgentManager

    logger.info("Startup complete: WorkspaceRuntimeRegistry initialized")
    logger.info("Backend URL fixed for frontend: %s", BACKEND_URL)


# Register API routers under /api
from api.assets import router as assets_router
from api.workspaces import router as workspaces_router

app.include_router(chat_router, prefix="/api")
app.include_router(sessions_router, prefix="/api")
app.include_router(files_router, prefix="/api")
app.include_router(agents_router, prefix="/api")
app.include_router(assets_router, prefix="/api")  # Phase 3+4: Assets Upload API
app.include_router(workspaces_router, prefix="/api")  # Phase 5.3: Workspace CRUD + Bootstrap


if __name__ == "__main__":
    try:
        import uvicorn
    except ImportError as exc:
        raise RuntimeError(
            "uvicorn is not installed in the current Python environment. Activate backend/.venv first."
        ) from exc

    if ".venv" not in sys.executable:
        logger.warning(
            "Current Python is %s. This does not look like backend/.venv; dependency errors may follow.",
            sys.executable,
        )

    logger.info("Starting backend via app.py on %s", BACKEND_URL)
    logger.info("Do not switch to 8000/8003; the frontend is pinned to %s.", BACKEND_URL)
    logger.info("Start the backend from this repository's backend/ directory.")
    uvicorn.run("app:app", host=DEFAULT_HOST, port=DEFAULT_PORT, reload=True)
