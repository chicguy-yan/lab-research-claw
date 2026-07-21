"""WorkspaceRuntimeRegistry 鈥?workspace lifecycle, manifest, and runtime management.

Phase 5.3: Replaces the global singleton SessionManager/AgentManager pattern.
Each workspace gets its own SessionManager + workspace-scoped tools,
while LLM and stateless tools are shared across all workspaces.
"""

from __future__ import annotations

import json
import logging
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from langchain_openai import ChatOpenAI

import config as cfg
from graph.session_manager import SessionManager
from tools.fetch_url_tool import FetchURLTool
from tools.python_repl_tool import PythonREPLTool
from tools.read_file_tool import ReadFileTool
from tools.terminal_tool import TerminalTool
from tools.write_file_tool import WriteFileTool
from runtime.bootstrap_runner import sync_bootstrap_file

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _bootstrap_template_path() -> Path:
    return cfg.WORKSPACE_TEMPLATES_DIR / "BOOTSTRAP.md"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class SharedAgentResources:
    """Resources shared across all workspaces (one instance per process)."""
    llm: ChatOpenAI | None = None
    fetch_url_tool: FetchURLTool | None = None
    config_error: str = ""


@dataclass
class WorkspaceRuntime:
    """Per-workspace isolated runtime."""
    workspace_id: str
    workspace_dir: Path
    session_manager: SessionManager = field(repr=False)
    workspace_tools: list = field(default_factory=list, repr=False)


# ---------------------------------------------------------------------------
# Manifest helpers
# ---------------------------------------------------------------------------

VALID_BOOTSTRAP_STATUSES = {"pending", "running", "completed", "failed"}


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


# ---------------------------------------------------------------------------
# Skill registry normalization (moved from app.py)
# ---------------------------------------------------------------------------

def _normalize_skill_entry(raw_skill: dict) -> dict | None:
    skill_id = str(raw_skill.get("id", "")).strip()
    name = str(raw_skill.get("name", "")).strip()
    if not skill_id or not name:
        return None
    normalized = dict(raw_skill)
    normalized["id"] = skill_id
    normalized["name"] = name
    normalized["entry"] = str(raw_skill.get("entry", "")).strip() or f"skills/{skill_id}/SKILL.md"
    normalized["category"] = str(raw_skill.get("category", "misc")).strip() or "misc"
    triggers = raw_skill.get("triggers", [])
    normalized["triggers"] = [str(t).strip() for t in triggers if str(t).strip()]
    use_cases = str(raw_skill.get("use_cases", "")).strip() or str(raw_skill.get("description", "")).strip()
    if use_cases:
        normalized["use_cases"] = use_cases
    else:
        normalized.pop("use_cases", None)
    preferred_routes = raw_skill.get("preferred_routes", [])
    normalized["preferred_routes"] = [str(t).strip() for t in preferred_routes if str(t).strip()]
    return normalized


def _normalize_workspace_skills(template_dir: Path, workspace_dir: Path) -> None:
    """Refresh workspace skill registry from template + legacy entries."""
    template_registry_path = template_dir / "skills" / "registry.json"
    workspace_registry_path = workspace_dir / "skills" / "registry.json"

    template_registry = _load_json(template_registry_path)
    workspace_registry = _load_json(workspace_registry_path)

    normalized_skills: list[dict] = []
    index_by_id: dict[str, int] = {}

    for raw_skill in workspace_registry.get("skills", []):
        normalized = _normalize_skill_entry(raw_skill)
        if not normalized:
            continue
        index_by_id[normalized["id"]] = len(normalized_skills)
        normalized_skills.append(normalized)

    for raw_skill in template_registry.get("skills", []):
        normalized = _normalize_skill_entry(raw_skill)
        if not normalized:
            continue
        existing_index = index_by_id.get(normalized["id"])
        if existing_index is None:
            index_by_id[normalized["id"]] = len(normalized_skills)
            normalized_skills.append(normalized)
            continue
        merged = dict(normalized_skills[existing_index])
        merged.update(normalized)
        for key, value in normalized_skills[existing_index].items():
            if key not in merged:
                merged[key] = value
        normalized_skills[existing_index] = merged

    normalized_registry = {
        "version": (
            str(template_registry.get("version", "")).strip()
            or str(workspace_registry.get("version", "")).strip()
            or "0.1"
        ),
        "skills": normalized_skills,
    }
    if "last_updated" in workspace_registry:
        normalized_registry["last_updated"] = workspace_registry["last_updated"]
    elif "last_updated" in template_registry:
        normalized_registry["last_updated"] = template_registry["last_updated"]

    serialized = json.dumps(normalized_registry, indent=2, ensure_ascii=False) + "\n"
    current_serialized = ""
    if workspace_registry_path.exists():
        try:
            current_serialized = workspace_registry_path.read_text(encoding="utf-8")
        except OSError:
            current_serialized = ""

    if serialized != current_serialized:
        workspace_registry_path.parent.mkdir(parents=True, exist_ok=True)
        workspace_registry_path.write_text(serialized, encoding="utf-8")
        logger.info("Normalized workspace skill registry: %s", workspace_registry_path)


def _migrate_workspace(template_dir: Path, workspace_dir: Path) -> None:
    """Copy missing directories and files from template into an existing workspace."""
    for src in template_dir.rglob("*"):
        rel = src.relative_to(template_dir)
        if rel.as_posix() == "BOOTSTRAP.md":
            continue
        dst = workspace_dir / rel
        if dst.exists():
            continue
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
            logger.info("Migrated missing directory: %s", rel)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            logger.info("Migrated missing file: %s", rel)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class WorkspaceRuntimeRegistry:
    """Central registry: workspace lifecycle + runtime management.

    Shared resources (LLM, FetchURLTool) are created once.
    Per-workspace resources (SessionManager, file/exec tools) are lazily created.
    """

    def __init__(self) -> None:
        self._shared = SharedAgentResources()
        self._runtimes: dict[str, WorkspaceRuntime] = {}

    # 鈹€鈹€ shared resources 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

    def initialize_shared(self) -> None:
        """Initialize shared LLM + stateless tools. Called once at startup."""
        self._shared.config_error = cfg.openai_api_key_error()
        if self._shared.config_error:
            logger.warning("%s", self._shared.config_error)
            self._shared.llm = None
        else:
            self._shared.llm = ChatOpenAI(
                api_key=cfg.OPENAI_API_KEY,
                base_url=cfg.OPENAI_BASE_URL,
                model=cfg.OPENAI_MODEL,
                streaming=True,
            )
        self._shared.fetch_url_tool = FetchURLTool()
        logger.info(
            "Shared resources initialized 鈥?model=%s base_url=%s",
            cfg.OPENAI_MODEL, cfg.OPENAI_BASE_URL,
        )

    def get_shared(self) -> SharedAgentResources:
        return self._shared

    # 鈹€鈹€ workspace directory resolution 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

    @staticmethod
    def resolve_workspace_dir(workspace_id: str) -> Path:
        return cfg.OPENCLAW_DIR / f"workspace-{workspace_id}"

    @staticmethod
    def manifest_path(workspace_dir: Path) -> Path:
        return workspace_dir / "workspace_manifest.json"

    # 鈹€鈹€ manifest CRUD 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

    def load_manifest(self, workspace_id: str) -> dict:
        wdir = self.resolve_workspace_dir(workspace_id)
        return _load_json(self.manifest_path(wdir))

    def save_manifest(self, workspace_id: str, manifest: dict) -> None:
        wdir = self.resolve_workspace_dir(workspace_id)
        manifest["updated_at"] = _now_iso()
        _save_json(self.manifest_path(wdir), manifest)

    def update_bootstrap_status(
        self, workspace_id: str, status: str, error: str = ""
    ) -> dict:
        """Update bootstrap_status in manifest. Returns updated manifest."""
        if status not in VALID_BOOTSTRAP_STATUSES:
            raise ValueError(f"Invalid bootstrap status: {status}")
        manifest = self.load_manifest(workspace_id)
        manifest["bootstrap_status"] = status
        if error:
            manifest["last_bootstrap_error"] = error
        elif status == "completed":
            manifest["last_bootstrap_error"] = ""
        self.save_manifest(workspace_id, manifest)
        return manifest

    # 鈹€鈹€ workspace listing 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

    def list_workspaces(self) -> list[dict]:
        workspaces = []
        if not cfg.OPENCLAW_DIR.exists():
            return workspaces
        for child in sorted(cfg.OPENCLAW_DIR.iterdir()):
            if not child.is_dir() or not child.name.startswith("workspace-"):
                continue
            wid = child.name[len("workspace-"):]
            manifest = _load_json(self.manifest_path(child))
            sm = self._get_or_create_session_manager(wid, child)
            workspaces.append({
                "workspace_id": wid,
                "display_name": manifest.get("display_name", wid),
                "description": manifest.get("description", ""),
                "bootstrap_status": manifest.get("bootstrap_status", "completed"),
                "workspace_dir": str(child),
                "session_count": len(sm.list_sessions()),
            })
        return workspaces

    # 鈹€鈹€ workspace creation (provision) 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

    def create_workspace(
        self,
        workspace_id: str,
        display_name: str,
        description: str = "",
    ) -> dict:
        """Provision a new workspace: copy template, write manifest, set pending."""
        workspace_dir = self.resolve_workspace_dir(workspace_id)
        if workspace_dir.exists():
            raise FileExistsError(f"Workspace already exists: {workspace_id}")

        cfg.OPENCLAW_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            cfg.WORKSPACE_TEMPLATES_DIR,
            workspace_dir,
            ignore=shutil.ignore_patterns("BOOTSTRAP.md"),
        )

        now = _now_iso()
        manifest = {
            "workspace_id": workspace_id,
            "display_name": display_name,
            "description": description,
            "bootstrap_status": "pending",
            "created_at": now,
            "updated_at": now,
        }
        _save_json(self.manifest_path(workspace_dir), manifest)
        sync_bootstrap_file(workspace_dir, _bootstrap_template_path(), manifest["bootstrap_status"])

        _normalize_workspace_skills(cfg.WORKSPACE_TEMPLATES_DIR, workspace_dir)

        logger.info("Provisioned workspace: %s at %s", workspace_id, workspace_dir)
        return manifest

    def rename_workspace(self, workspace_id: str, display_name: str, description: str | None = None) -> dict:
        manifest = self.load_manifest(workspace_id)
        if not manifest:
            raise FileNotFoundError(f"Workspace not found: {workspace_id}")
        manifest["display_name"] = display_name
        if description is not None:
            manifest["description"] = description
        self.save_manifest(workspace_id, manifest)
        return manifest

    # 鈹€鈹€ ensure default workspace 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

    def ensure_default_workspace(self) -> None:
        """Ensure workspace-default exists. Migrate template additions if needed."""
        cfg.OPENCLAW_DIR.mkdir(parents=True, exist_ok=True)
        default_dir = cfg.DEFAULT_WORKSPACE_DIR
        if not default_dir.exists():
            shutil.copytree(
                cfg.WORKSPACE_TEMPLATES_DIR,
                default_dir,
                ignore=shutil.ignore_patterns("BOOTSTRAP.md"),
            )
            now = _now_iso()
            manifest = {
                "workspace_id": "default",
                "display_name": "Default Workspace",
                "description": "",
                "bootstrap_status": "completed",
                "created_at": now,
                "updated_at": now,
            }
            _save_json(self.manifest_path(default_dir), manifest)
            logger.info("Initialized default workspace at %s", default_dir)
        else:
            _migrate_workspace(cfg.WORKSPACE_TEMPLATES_DIR, default_dir)
            # Ensure manifest exists for legacy default workspace
            mp = self.manifest_path(default_dir)
            if not mp.exists():
                now = _now_iso()
                manifest = {
                    "workspace_id": "default",
                    "display_name": "Default Workspace",
                    "description": "",
                    "bootstrap_status": "completed",
                    "created_at": now,
                    "updated_at": now,
                }
                _save_json(mp, manifest)
        default_manifest = _load_json(self.manifest_path(default_dir))
        sync_bootstrap_file(default_dir, _bootstrap_template_path(), default_manifest.get("bootstrap_status", "completed"))
        _normalize_workspace_skills(cfg.WORKSPACE_TEMPLATES_DIR, default_dir)

    # 鈹€鈹€ runtime (lazy init) 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

    def _get_or_create_session_manager(self, workspace_id: str, workspace_dir: Path) -> SessionManager:
        if workspace_id in self._runtimes:
            return self._runtimes[workspace_id].session_manager
        return SessionManager(workspace_dir)

    def _build_workspace_tools(self, workspace_dir: Path) -> list:
        return [
            TerminalTool(workspace_dir=workspace_dir),
            PythonREPLTool(workspace_dir=workspace_dir),
            ReadFileTool(workspace_dir=workspace_dir),
            WriteFileTool(workspace_dir=workspace_dir),
        ]

    def get_runtime(self, workspace_id: str) -> WorkspaceRuntime:
        """Get or lazily create a WorkspaceRuntime for the given workspace_id."""
        if workspace_id in self._runtimes:
            return self._runtimes[workspace_id]

        workspace_dir = self.resolve_workspace_dir(workspace_id)
        if not workspace_dir.exists():
            raise FileNotFoundError(f"Workspace directory not found: {workspace_id}")

        # Migrate template additions
        _migrate_workspace(cfg.WORKSPACE_TEMPLATES_DIR, workspace_dir)
        manifest = self.load_manifest(workspace_id)
        sync_bootstrap_file(workspace_dir, _bootstrap_template_path(), manifest.get("bootstrap_status", "completed"))
        _normalize_workspace_skills(cfg.WORKSPACE_TEMPLATES_DIR, workspace_dir)

        sm = SessionManager(workspace_dir)
        tools = self._build_workspace_tools(workspace_dir)

        runtime = WorkspaceRuntime(
            workspace_id=workspace_id,
            workspace_dir=workspace_dir,
            session_manager=sm,
            workspace_tools=tools,
        )
        self._runtimes[workspace_id] = runtime
        logger.info("Created runtime for workspace: %s", workspace_id)
        return runtime

    def get_all_tools(self, workspace_id: str) -> list:
        """Return shared tools + workspace-scoped tools combined."""
        runtime = self.get_runtime(workspace_id)
        all_tools = list(runtime.workspace_tools)
        if self._shared.fetch_url_tool:
            all_tools.append(self._shared.fetch_url_tool)
        return all_tools


