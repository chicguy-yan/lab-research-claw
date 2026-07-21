from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ScenarioPackage:
    scenario_id: str
    scenario_name: str
    package_dir: Path
    question_file: Path
    runbook_file: Path
    document: dict[str, Any]
    runbook_module: Any


@dataclass
class SSEEvent:
    event: str
    data: dict[str, Any]


@dataclass
class AttachmentPayload:
    saved_path: str
    file_type: str
    summary: str
    source_path: str
    reused_from_cache: bool


@dataclass
class EvalConfig:
    backend_url: str
    run_id: str
    run_root: Path
    scenario_paths: list[Path]
    source_root: Path | None = None
    session_limit: int | None = None
    turn_limit: int | None = None
    judge_mode: str = "heuristic"
    mirror_to_workspace: bool = True
    resume: bool = False
    request_timeout_seconds: int = 900
    max_turn_attempts: int = 3
    retry_backoff_seconds: float = 2.0
    verbose: bool = True


@dataclass
class SessionRuntimeState:
    backend_session_id: str
    trace_count: int = 0


@dataclass
class ScenarioRuntimeState:
    workspace_id: str | None = None
    session_backend_ids: dict[str, SessionRuntimeState] = field(default_factory=dict)


@dataclass
class RunCheckpoint:
    run_id: str
    completed_turns: set[str] = field(default_factory=set)
    scenario_states: dict[str, ScenarioRuntimeState] = field(default_factory=dict)


def turn_key(scenario_id: str, session_id: str, turn_id: int) -> str:
    return f"{scenario_id}/{session_id}/turn_{turn_id}"
