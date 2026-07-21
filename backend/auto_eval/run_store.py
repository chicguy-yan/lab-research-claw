from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from auto_eval.models import RunCheckpoint, ScenarioRuntimeState, SessionRuntimeState


class RunStore:
    def __init__(self, run_root: Path) -> None:
        self.run_root = run_root
        self.reports_dir = run_root / "reports"
        self.scenarios_dir = run_root / "scenarios"
        self.checkpoints_dir = run_root / "checkpoints"
        self.probes_dir = run_root / "probes"
        self.event_log_path = run_root / "events.jsonl"
        self.logs_dir = run_root / "logs"
        self.console_log_path = self.logs_dir / "run.log"
        self.console_lines: list[str] = []

        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.scenarios_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        self.probes_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.console_log_path.write_text("", encoding="utf-8")

    def _normalize(self, value: Any) -> Any:
        if is_dataclass(value):
            return asdict(value)
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, dict):
            return {str(key): self._normalize(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._normalize(item) for item in value]
        if isinstance(value, set):
            return sorted(self._normalize(item) for item in value)
        return value

    def append_event(self, event_type: str, payload: dict[str, Any]) -> None:
        record = {"event_type": event_type, "payload": self._normalize(payload)}
        with self.event_log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    def record_console(self, line: str) -> None:
        self.console_lines.append(line)
        with self.console_log_path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    def write_json(self, relative_path: str, payload: Any) -> Path:
        target = self.run_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self._normalize(payload), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return target

    def write_text(self, relative_path: str, content: str) -> Path:
        target = self.run_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def write_turn_result(self, scenario_id: str, session_id: str, turn_id: int, payload: dict[str, Any]) -> Path:
        safe_session = session_id.replace("/", "_")
        return self.write_json(
            f"scenarios/{scenario_id}/{safe_session}_turn_{turn_id:02d}.json",
            payload,
        )

    def load_checkpoint(self, run_id: str) -> RunCheckpoint:
        checkpoint_path = self.checkpoints_dir / "completed_turns.json"
        if not checkpoint_path.exists():
            return RunCheckpoint(run_id=run_id)

        payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        scenario_states: dict[str, ScenarioRuntimeState] = {}
        for scenario_id, raw_state in payload.get("scenario_states", {}).items():
            session_backend_ids = {
                session_id: SessionRuntimeState(
                    backend_session_id=item["backend_session_id"],
                    trace_count=item.get("trace_count", 0),
                )
                for session_id, item in raw_state.get("session_backend_ids", {}).items()
            }
            scenario_states[scenario_id] = ScenarioRuntimeState(
                workspace_id=raw_state.get("workspace_id"),
                session_backend_ids=session_backend_ids,
            )
        return RunCheckpoint(
            run_id=payload.get("run_id", run_id),
            completed_turns=set(payload.get("completed_turns", [])),
            scenario_states=scenario_states,
        )

    def save_checkpoint(self, checkpoint: RunCheckpoint) -> Path:
        payload = {
            "run_id": checkpoint.run_id,
            "completed_turns": sorted(checkpoint.completed_turns),
            "scenario_states": {
                scenario_id: {
                    "workspace_id": state.workspace_id,
                    "session_backend_ids": {
                        session_id: {
                            "backend_session_id": session_state.backend_session_id,
                            "trace_count": session_state.trace_count,
                        }
                        for session_id, session_state in state.session_backend_ids.items()
                    },
                }
                for scenario_id, state in checkpoint.scenario_states.items()
            },
        }
        return self.write_json("checkpoints/completed_turns.json", payload)

    def load_turn_results(self, scenario_id: str) -> list[dict[str, Any]]:
        target_dir = self.scenarios_dir / scenario_id
        if not target_dir.exists():
            return []
        results = []
        for file_path in sorted(target_dir.glob("*.json")):
            results.append(json.loads(file_path.read_text(encoding="utf-8")))
        return results

    def export_console_replay(self) -> None:
        text = "\n".join(self.console_lines) + ("\n" if self.console_lines else "")
        self.write_text("reports/terminal_replay.txt", text)
        html = "<html><body><pre>{}</pre></body></html>".format(
            text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )
        self.write_text("reports/terminal_replay.html", html)
