from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

import requests

from auto_eval.http_backend import HttpBackendClient
from auto_eval.judge import HeuristicJudge
from auto_eval.markdown_reporter import build_overall_report_markdown, build_scenario_summary_markdown
from auto_eval.models import (
    AttachmentPayload,
    EvalConfig,
    RunCheckpoint,
    ScenarioRuntimeState,
    SessionRuntimeState,
    turn_key,
)
from auto_eval.run_store import RunStore
from auto_eval.scenario_loader import load_scenario_package


class EvalRunner:
    def __init__(self, config: EvalConfig) -> None:
        self.config = config
        self.client = HttpBackendClient(config.backend_url, timeout_seconds=config.request_timeout_seconds)
        self.store = RunStore(config.run_root)
        self.judge = HeuristicJudge(mode=config.judge_mode)
        self.asset_cache: dict[tuple[str, str], AttachmentPayload] = {}
        self._last_token_preview = ""

    def _single_line(self, value: str, limit: int = 120) -> str:
        compact = re.sub(r"\s+", " ", value).strip()
        if len(compact) > limit:
            return compact[: limit - 3] + "..."
        return compact

    def _summarize_value(self, value: Any) -> str:
        if value is None:
            return "none"
        if isinstance(value, dict):
            if value.get("path"):
                return f"path={value['path']}"
            if value.get("saved_path"):
                return f"saved_path={value['saved_path']}"
            scalar_keys = [key for key, item in value.items() if isinstance(item, (str, int, float, bool))]
            if scalar_keys:
                parts = []
                for key in scalar_keys[:3]:
                    item = value[key]
                    if isinstance(item, str):
                        item = self._single_line(item, limit=48)
                    parts.append(f"{key}={item}")
                return ", ".join(parts)
            return f"keys={','.join(sorted(value.keys())[:5])}"
        if isinstance(value, list):
            return f"list[{len(value)}]"
        if isinstance(value, str):
            compact = self._single_line(value, limit=80)
            if len(compact) <= 24 and " " not in compact:
                return compact
            return f"text_len={len(value)}"
        return str(value)

    def _log(self, message: str) -> None:
        stamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{stamp}] {self._single_line(message, limit=240)}"
        encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
        safe_line = line.encode(encoding, errors="replace").decode(encoding, errors="replace")
        print(safe_line, flush=True)
        self.store.record_console(safe_line)

    def _scenario_state(self, checkpoint: RunCheckpoint, scenario_id: str) -> ScenarioRuntimeState:
        if scenario_id not in checkpoint.scenario_states:
            checkpoint.scenario_states[scenario_id] = ScenarioRuntimeState()
        return checkpoint.scenario_states[scenario_id]

    def _session_state(
        self,
        scenario_state: ScenarioRuntimeState,
        session_id: str,
        backend_session_id: str,
    ) -> SessionRuntimeState:
        if session_id not in scenario_state.session_backend_ids:
            scenario_state.session_backend_ids[session_id] = SessionRuntimeState(
                backend_session_id=backend_session_id
            )
        return scenario_state.session_backend_ids[session_id]

    def _workspace_date_token(self) -> str:
        date_matches = re.findall(r"20\d{6}", self.config.run_id)
        time_matches = re.findall(r"(?<!\d)(\d{6})(?!\d)", self.config.run_id)

        if date_matches:
            date_part = date_matches[-1][2:]
        else:
            date_part = datetime.now().strftime("%y%m%d")

        hhmm = datetime.now().strftime("%H%M")
        if time_matches:
            for candidate in reversed(time_matches):
                if not candidate.startswith("20"):
                    hhmm = candidate[:4]
                    break

        return f"{date_part}_{hhmm}"

    def _build_workspace_id(self, scenario_id: str) -> str:
        return f"eval-{scenario_id.lower()}-{self._workspace_date_token()}"

    def _resolve_upload_path(self, scenario_dir: Path, declared_path: str) -> Path:
        candidate = Path(declared_path)
        if candidate.is_absolute() and candidate.exists():
            return candidate
        local_candidate = scenario_dir / declared_path
        if local_candidate.exists():
            return local_candidate.resolve()
        if self.config.source_root:
            rooted = self.config.source_root / declared_path
            if rooted.exists():
                return rooted.resolve()
        raise FileNotFoundError(f"Upload source not found: {declared_path}")

    def _materialize_attachments(
        self,
        scenario_dir: Path,
        workspace_id: str,
        turn: dict[str, Any],
    ) -> list[AttachmentPayload]:
        attachments: list[AttachmentPayload] = []
        for declared_path in turn.get("user_upload", []):
            source_path = self._resolve_upload_path(scenario_dir, declared_path)
            cache_key = (workspace_id, str(source_path))
            cached = self.asset_cache.get(cache_key)
            if cached:
                attachments.append(
                    AttachmentPayload(
                        saved_path=cached.saved_path,
                        file_type=cached.file_type,
                        summary=cached.summary,
                        source_path=cached.source_path,
                        reused_from_cache=True,
                    )
                )
                self._log(f"[UPLOAD][CACHE] {declared_path} -> {cached.saved_path}")
                continue

            self._log(f"[UPLOAD][START] {declared_path}")
            uploaded = self.client.upload_asset(workspace_id, source_path)
            payload = AttachmentPayload(
                saved_path=uploaded["saved_path"],
                file_type=uploaded.get("file_type", ""),
                summary=uploaded.get("quick_summary", ""),
                source_path=str(source_path),
                reused_from_cache=False,
            )
            self.asset_cache[cache_key] = payload
            attachments.append(payload)
            summary_chars = len(payload.summary or "")
            self._log(
                f"[UPLOAD][DONE] {declared_path} -> {payload.saved_path} "
                f"(type={payload.file_type or 'unknown'}, summary_chars={summary_chars})"
            )
        return attachments

    def _fetch_trace_delta(
        self,
        workspace_id: str,
        backend_session_id: str,
        session_state: SessionRuntimeState,
    ) -> list[dict[str, Any]]:
        raw_content = self.client.read_text_file(workspace_id, f"context_trace/{backend_session_id}.json")
        envelope = json.loads(raw_content)
        traces = envelope.get("traces", [])
        delta = traces[session_state.trace_count :]
        session_state.trace_count = len(traces)
        return delta

    def _last_assistant_text(self, history: dict[str, Any]) -> str:
        messages = history.get("messages", [])
        assistants = [item.get("content", "") for item in messages if item.get("role") == "assistant"]
        return assistants[-1] if assistants else ""

    def _extract_created_paths(self, trace_events: list[dict[str, Any]]) -> list[str]:
        paths: list[str] = []
        for event in trace_events:
            args = event.get("args") or {}
            if event.get("tool") == "write_file" and isinstance(args, dict) and args.get("path"):
                paths.append(args["path"])
        return paths

    def _flatten_tree_files(self, entries: list[dict[str, Any]]) -> list[str]:
        files: list[str] = []
        for entry in entries:
            if entry.get("type") == "file" and entry.get("path"):
                files.append(entry["path"])
            files.extend(self._flatten_tree_files(entry.get("children", [])))
        return files

    def _write_probe_json(self, target: Path, payload: Any) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def _capture_temporary_dir_probe(
        self,
        probe_root: Path,
        workspace_id: str,
        backend_session_id: str,
    ) -> tuple[dict[str, Any], dict[str, str]]:
        session_root = f"temporary_dir/{backend_session_id}"
        snapshot: dict[str, Any] = {
            "path": session_root,
            "exists": False,
            "file_count": 0,
            "files": [],
            "session_relative_files": [],
            "tree": [],
            "copied_text_files": [],
            "preview_samples": {},
        }
        text_files: dict[str, str] = {}

        try:
            payload = self.client.get_file_tree(workspace_id, session_root, max_depth=6)
        except Exception as exc:
            snapshot["error"] = str(exc)
            self._write_probe_json(probe_root / "temporary_dir_snapshot.json", snapshot)
            return snapshot, text_files

        tree = payload.get("tree", [])
        files = self._flatten_tree_files(tree)
        prefix = session_root.rstrip("/") + "/"
        session_relative_files = [item[len(prefix):] if item.startswith(prefix) else item for item in files]
        snapshot.update(
            {
                "exists": True,
                "file_count": len(files),
                "files": files,
                "session_relative_files": session_relative_files,
                "tree": tree,
            }
        )

        preview_samples: dict[str, str] = {}
        copied_text_files: list[dict[str, Any]] = []
        for full_path, relative_path in zip(files, session_relative_files):
            try:
                content = self.client.read_text_file(workspace_id, full_path)
            except Exception as exc:
                copied_text_files.append({"path": full_path, "copied": False, "error": str(exc)})
                continue

            target = probe_root / full_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            text_files[relative_path] = content
            copied_text_files.append({"path": full_path, "copied": True, "chars": len(content)})
            if len(preview_samples) < 8:
                preview_samples[relative_path] = content[:200]

        snapshot["copied_text_files"] = copied_text_files
        snapshot["preview_samples"] = preview_samples
        self._write_probe_json(probe_root / "temporary_dir_snapshot.json", snapshot)
        return snapshot, text_files

    def _evaluate_temporary_expectations(
        self,
        turn: dict[str, Any],
        temporary_snapshot: dict[str, Any],
        temporary_text_files: dict[str, str],
    ) -> dict[str, Any] | None:
        expectations = turn.get("temporary_expectations")
        if not expectations:
            return None

        session_relative_files = list(temporary_snapshot.get("session_relative_files", []))
        file_count = int(temporary_snapshot.get("file_count", 0))
        score = 100.0
        reasons: list[str] = []

        min_file_count = expectations.get("min_file_count")
        if min_file_count is not None and file_count < int(min_file_count):
            score -= 25.0
            reasons.append(f"temporary_dir file_count={file_count} < {min_file_count}")

        max_file_count = expectations.get("max_file_count")
        if max_file_count is not None and file_count > int(max_file_count):
            score -= 15.0
            reasons.append(f"temporary_dir file_count={file_count} > {max_file_count}")

        for required_file in expectations.get("required_files", []):
            if required_file not in session_relative_files:
                score -= 20.0
                reasons.append(f"missing temporary file: {required_file}")

        for pattern in expectations.get("required_globs", []):
            if not any(fnmatch(item, pattern) for item in session_relative_files):
                score -= 15.0
                reasons.append(f"missing temporary glob match: {pattern}")

        for relative_path, required_terms in expectations.get("required_terms_by_file", {}).items():
            content = temporary_text_files.get(relative_path, "")
            if not content:
                score -= 15.0
                reasons.append(f"temporary file unreadable or missing: {relative_path}")
                continue
            for term in required_terms:
                if term not in content:
                    score -= 8.0
                    reasons.append(f"temporary file missing term `{term}` in {relative_path}")

        score = max(0.0, round(score, 2))
        verdict = "pass" if score >= 80 else "partial" if score >= 60 else "fail"
        return {
            "criterion_id": expectations.get("criterion_id", f"{turn['turn_id']}-TEMP"),
            "score": score,
            "verdict": verdict,
            "reasons": reasons,
            "evidence": {
                "file_count": file_count,
                "session_relative_files": session_relative_files,
                "preview_samples": temporary_snapshot.get("preview_samples", {}),
            },
        }

    def _prepare_probe_workspace(
        self,
        scenario_id: str,
        session_id: str,
        turn_id: int,
        workspace_id: str,
        turn: dict[str, Any],
    ) -> Path:
        probe_root = self.store.probes_dir / scenario_id / session_id / f"turn_{turn_id:02d}"
        probe_root.mkdir(parents=True, exist_ok=True)
        for expected in turn.get("expected_artifacts", []):
            path = expected["path"]
            target = probe_root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                content = self.client.read_text_file(workspace_id, path)
            except Exception:
                continue
            target.write_text(content, encoding="utf-8")
        return probe_root

    def _scenario_summary_payload(
        self,
        scenario: dict[str, Any],
        runbook_summary: dict[str, Any],
        turn_results: list[dict[str, Any]],
    ) -> dict[str, Any]:
        average = sum(item["final_turn_score"] for item in turn_results) / max(1, len(turn_results))
        pass_count = sum(1 for item in turn_results if item["final_turn_score"] >= 80)
        temporary_turns = sum(
            1 for item in turn_results if item.get("temporary_dir_snapshot", {}).get("file_count", 0) > 0
        )
        return {
            "scenario_id": scenario["scenario_id"],
            "scenario_name": scenario.get("scenario_name", scenario["scenario_id"]),
            "average_score": round(average, 2),
            "pass_rate": pass_count / max(1, len(turn_results)),
            "turn_count": len(turn_results),
            "temporary_turn_count": temporary_turns,
            "hallucination_summary": runbook_summary.get("hallucination_summary", {}),
            "runtime_blueprint": runbook_summary.get("runtime_blueprint", {}),
        }

    def _planned_turn_keys(self, scenario_packages: list[Any]) -> list[str]:
        planned: list[str] = []
        for scenario_package in scenario_packages:
            sessions = scenario_package.document["sessions"]
            if self.config.session_limit is not None:
                sessions = sessions[: self.config.session_limit]
            for session in sessions:
                turns = session["dialogue"]
                if self.config.turn_limit is not None:
                    turns = turns[: self.config.turn_limit]
                for turn in turns:
                    planned.append(turn_key(scenario_package.scenario_id, session["session_id"], turn["turn_id"]))
        return planned

    def _render_progress_bar(self, completed: int, total: int, width: int = 24) -> str:
        if total <= 0:
            return "[------------------------]   0.00% (0/0)"
        ratio = min(1.0, max(0.0, completed / total))
        filled = int(round(ratio * width))
        bar = "#" * filled + "-" * (width - filled)
        return f"[{bar}] {ratio * 100:6.2f}% ({completed}/{total})"

    def _log_progress(self, completed: int, total: int, prefix: str = "[PROGRESS]") -> None:
        self._log(f"{prefix} {self._render_progress_bar(completed, total)}")

    def _write_workspace_reports(
        self,
        workspace_id: str,
        scenario_id: str,
        scenario_markdown: str,
        overall_report: str | None = None,
    ) -> None:
        if not self.config.mirror_to_workspace:
            return
        scenario_suffix = scenario_id.split("_")[-1].upper()
        self.client.write_text_file(
            workspace_id,
            f"memory/packs/EVAL_RUN_{self.config.run_id}_{scenario_suffix}_SUMMARY.md",
            scenario_markdown,
        )
        if overall_report:
            self.client.write_text_file(
                workspace_id,
                f"memory/packs/EVAL_RUN_{self.config.run_id}_INDEX.md",
                overall_report,
            )
            self.client.write_text_file(
                workspace_id,
                f"memory/packs/EVAL_RUN_{self.config.run_id}_SCOREBOARD.md",
                overall_report,
            )

    def _retryable_exception_message(self, exc: Exception) -> str:
        if isinstance(exc, requests.exceptions.HTTPError):
            response = exc.response
            if response is not None:
                response_text = (response.text or '').strip()
                if response_text:
                    return self._single_line(
                        f"{type(exc).__name__}: status={response.status_code} {response_text}",
                        limit=180,
                    )
                return f"{type(exc).__name__}: status={response.status_code}"
        return self._single_line(f"{type(exc).__name__}: {exc}", limit=180)

    def _is_retryable_turn_exception(self, exc: Exception) -> bool:
        if isinstance(
            exc,
            (
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.ChunkedEncodingError,
            ),
        ):
            return True
        if isinstance(exc, requests.exceptions.HTTPError):
            response = exc.response
            if response is None:
                return False
            return response.status_code in {408, 425, 429, 500, 502, 503, 504}
        message = str(exc).lower()
        transient_markers = (
            'timed out',
            'timeout',
            'temporarily unavailable',
            'response ended prematurely',
            'connection reset',
            'connection aborted',
            'server disconnected',
            'remote protocol error',
        )
        return any(marker in message for marker in transient_markers)

    def _execute_turn_once(
        self,
        scenario_package,
        session: dict[str, Any],
        turn: dict[str, Any],
        workspace_id: str,
        backend_session_id: str,
        session_state: SessionRuntimeState,
    ) -> dict[str, Any]:
        attachments = self._materialize_attachments(scenario_package.package_dir, workspace_id, turn)
        route = turn.get('route', session.get('route', 'default'))
        self._log(
            f"[TURN][START] {scenario_package.scenario_id} / {session['session_id']} / turn {turn['turn_id']} "
            f"route={route}"
        )
        assistant_chunks: list[str] = []
        token_chars_since_log = 0
        for event in self.client.stream_chat(
            workspace_id=workspace_id,
            session_id=backend_session_id,
            message=turn['user_input'],
            route=route,
            attachments=attachments,
            prompt_context={
                'scenario_id': scenario_package.scenario_id,
                'session_id': session['session_id'],
                'turn_id': turn['turn_id'],
            },
        ):
            self.store.append_event(
                event.event,
                {
                    'scenario_id': scenario_package.scenario_id,
                    'session_id': session['session_id'],
                    'turn_id': turn['turn_id'],
                    'backend_session_id': backend_session_id,
                    'data': event.data,
                },
            )
            if event.event == 'token':
                chunk = event.data.get('content', '')
                assistant_chunks.append(chunk)
                token_chars_since_log += len(chunk)
                if token_chars_since_log >= 240:
                    assistant_chars = sum(len(item) for item in assistant_chunks)
                    self._log(f'[STREAM][TOKEN] assistant_chars={assistant_chars}')
                    token_chars_since_log = 0
            elif event.event == 'tool_start':
                tool_name = event.data.get('tool', 'unknown')
                tool_input = self._summarize_value(event.data.get('input'))
                self._log(f'[STREAM][TOOL_START] {tool_name} {tool_input}')
            elif event.event == 'tool_end':
                tool_name = event.data.get('tool', 'unknown')
                tool_output = self._summarize_value(event.data.get('output'))
                self._log(f'[STREAM][TOOL_END] {tool_name} {tool_output}')
            elif event.event == 'done':
                self._log(f"[STREAM][DONE] backend_session_id={event.data.get('session_id', backend_session_id)}")
            elif event.event == 'error':
                self._log(f"[STREAM][ERROR] {self._summarize_value(event.data)}")

        history = self.client.get_history(workspace_id, backend_session_id)
        assistant_text = self._last_assistant_text(history) or ''.join(assistant_chunks)
        trace_events = self._fetch_trace_delta(workspace_id, backend_session_id, session_state)
        created_paths = self._extract_created_paths(trace_events)
        probe_root = self._prepare_probe_workspace(
            scenario_package.scenario_id,
            session['session_id'],
            turn['turn_id'],
            workspace_id,
            turn,
        )
        temporary_snapshot, temporary_text_files = self._capture_temporary_dir_probe(
            probe_root,
            workspace_id,
            backend_session_id,
        )
        if temporary_snapshot.get('file_count', 0):
            self._log(
                f"[PROBE][TEMP] {scenario_package.scenario_id} / {session['session_id']} / turn {turn['turn_id']} "
                f"files={temporary_snapshot['file_count']}"
            )
        raw_eval = scenario_package.runbook_module.evaluate_turn(
            session=session,
            turn=turn,
            assistant_text=assistant_text,
            trace_events=trace_events,
            workspace_root=probe_root,
            created_paths=created_paths,
        )
        judge_result = self.judge.evaluate(raw_eval['llm_job'], turn, assistant_text, trace_events)
        temporary_result = self._evaluate_temporary_expectations(turn, temporary_snapshot, temporary_text_files)
        secondary_score = (
            raw_eval['artifact_result']['score']
            if raw_eval.get('artifact_result')
            else raw_eval['trace_result']['score']
        )
        score_components = [
            raw_eval['content_result']['score'],
            secondary_score,
            judge_result['score'],
        ]
        if temporary_result is not None:
            score_components.append(temporary_result['score'])
            self._log(
                f"[PROBE][TEMP_CHECK] {scenario_package.scenario_id} / {session['session_id']} / turn {turn['turn_id']} "
                f"score={temporary_result['score']:.2f}"
            )
        final_score = round(sum(score_components) / len(score_components), 2)
        result = {
            'scenario_id': scenario_package.scenario_id,
            'session_id': session['session_id'],
            'turn_id': turn['turn_id'],
            'workspace_id': workspace_id,
            'backend_session_id': backend_session_id,
            'assistant_text': assistant_text,
            'attachments_used': [item.__dict__ for item in attachments],
            'trace_events': trace_events,
            'created_paths': created_paths,
            'temporary_dir_snapshot': temporary_snapshot,
            'temporary_result': temporary_result,
            'content_result': raw_eval['content_result'],
            'trace_result': raw_eval['trace_result'],
            'artifact_result': raw_eval.get('artifact_result'),
            'judge_result': judge_result,
            'hallucination_flags': raw_eval.get('hallucination_flags', {}),
            'expected_artifacts': turn.get('expected_artifacts', []),
            'temporary_expectations': turn.get('temporary_expectations'),
            'provisional_turn_score': raw_eval.get('provisional_turn_score', 0.0),
            'final_turn_score': final_score,
        }
        self._log(
            f"[TURN][DONE] {scenario_package.scenario_id} / {session['session_id']} / turn {turn['turn_id']} "
            f"score={final_score:.2f}"
        )
        return result

    def _execute_turn(
        self,
        scenario_package,
        session: dict[str, Any],
        turn: dict[str, Any],
        workspace_id: str,
        backend_session_id: str,
        session_state: SessionRuntimeState,
    ) -> dict[str, Any]:
        max_attempts = max(1, int(self.config.max_turn_attempts))
        backoff_seconds = max(0.0, float(self.config.retry_backoff_seconds))
        turn_label = f"{scenario_package.scenario_id} / {session['session_id']} / turn {turn['turn_id']}"

        for attempt in range(1, max_attempts + 1):
            if max_attempts > 1:
                self._log(f'[TURN][ATTEMPT] {turn_label} attempt {attempt}/{max_attempts}')
            try:
                return self._execute_turn_once(
                    scenario_package=scenario_package,
                    session=session,
                    turn=turn,
                    workspace_id=workspace_id,
                    backend_session_id=backend_session_id,
                    session_state=session_state,
                )
            except Exception as exc:
                reason = self._retryable_exception_message(exc)
                should_retry = attempt < max_attempts and self._is_retryable_turn_exception(exc)
                if should_retry:
                    wait_suffix = f' backoff={backoff_seconds:.1f}s' if backoff_seconds > 0 else ''
                    self._log(
                        f'[TURN][RETRY] {turn_label} attempt {attempt}/{max_attempts} '
                        f'reason={reason}{wait_suffix}'
                    )
                    if backoff_seconds > 0:
                        time.sleep(backoff_seconds)
                    continue
                self._log(
                    f'[TURN][FAIL] {turn_label} attempt {attempt}/{max_attempts} reason={reason}'
                )
                raise

    def run(self) -> dict[str, Any]:
        self.config.run_root.mkdir(parents=True, exist_ok=True)
        checkpoint = self.store.load_checkpoint(self.config.run_id) if self.config.resume else RunCheckpoint(self.config.run_id)
        scenario_packages = [load_scenario_package(path) for path in self.config.scenario_paths]
        planned_turn_keys = self._planned_turn_keys(scenario_packages)
        total_turns = len(planned_turn_keys)
        completed_turns_for_plan = sum(1 for key in planned_turn_keys if key in checkpoint.completed_turns)

        self.store.write_json(
            "run_manifest.json",
            {
                "run_id": self.config.run_id,
                "backend_url": self.config.backend_url,
                "scenario_paths": [str(path) for path in self.config.scenario_paths],
                "source_root": str(self.config.source_root) if self.config.source_root else None,
                "judge_mode": self.config.judge_mode,
                "session_limit": self.config.session_limit,
                "turn_limit": self.config.turn_limit,
                "request_timeout_seconds": self.config.request_timeout_seconds,
                "max_turn_attempts": self.config.max_turn_attempts,
                "retry_backoff_seconds": self.config.retry_backoff_seconds,
            },
        )

        scenario_summaries: list[dict[str, Any]] = []
        workspace_ids_for_index: list[str] = []

        self._log_progress(completed_turns_for_plan, total_turns, prefix="[PROGRESS][START]")

        for scenario_package in scenario_packages:
            scenario = scenario_package.document
            self._log(f"[SCENARIO][START] {scenario_package.scenario_id} {scenario_package.scenario_name}")
            scenario_state = self._scenario_state(checkpoint, scenario_package.scenario_id)

            if not scenario_state.workspace_id:
                workspace_id = self._build_workspace_id(scenario_package.scenario_id)
                display_name = scenario.get("workspace_init", {}).get(
                    "workspace_display_name_template",
                    f"[EVAL] {scenario_package.scenario_id} {self.config.run_id}",
                ).replace("{run_id}", self.config.run_id)
                description = scenario.get("workspace_init", {}).get("workspace_description", scenario_package.scenario_name)
                manifest = self.client.create_workspace(workspace_id, display_name, description)
                scenario_state.workspace_id = manifest["workspace_id"]
                self._log(f"[WORKSPACE][CREATED] {scenario_state.workspace_id}")
            workspace_id = scenario_state.workspace_id
            workspace_ids_for_index.append(workspace_id)

            manifest = self.client.get_manifest(workspace_id)
            if scenario.get("workspace_init", {}).get("bootstrap_required") and manifest.get("bootstrap_status") != "completed":
                self._log(f"[BOOTSTRAP][START] {workspace_id}")
                self.client.start_bootstrap(workspace_id)

            turn_results = self.store.load_turn_results(scenario_package.scenario_id)
            sessions = scenario["sessions"]
            if self.config.session_limit is not None:
                sessions = sessions[: self.config.session_limit]

            for session in sessions:
                session_type = session.get("session_type", "normal")
                if session_type == "bootstrap":
                    backend_session_id = scenario.get("workspace_init", {}).get("bootstrap_session_id", "__bootstrap__")
                    try:
                        self.client.rename_session(workspace_id, backend_session_id, session["session_title"])
                    except Exception:
                        pass
                else:
                    existing = scenario_state.session_backend_ids.get(session["session_id"])
                    if existing:
                        backend_session_id = existing.backend_session_id
                    else:
                        created = self.client.create_session(workspace_id, session["session_title"])
                        backend_session_id = created["id"]
                        self.client.rename_session(workspace_id, backend_session_id, session["session_title"])
                        self._log(f"[SESSION][CREATED] {session['session_id']} -> {backend_session_id}")
                session_state = self._session_state(scenario_state, session["session_id"], backend_session_id)

                turns = session["dialogue"]
                if self.config.turn_limit is not None:
                    turns = turns[: self.config.turn_limit]
                for turn in turns:
                    key = turn_key(scenario_package.scenario_id, session["session_id"], turn["turn_id"])
                    if key in checkpoint.completed_turns:
                        self._log(f"[TURN][SKIP] {key}")
                        continue
                    result = self._execute_turn(
                        scenario_package=scenario_package,
                        session=session,
                        turn=turn,
                        workspace_id=workspace_id,
                        backend_session_id=backend_session_id,
                        session_state=session_state,
                    )
                    turn_results.append(result)
                    self.store.write_turn_result(
                        scenario_package.scenario_id,
                        session["session_id"],
                        turn["turn_id"],
                        result,
                    )
                    checkpoint.completed_turns.add(key)
                    completed_turns_for_plan += 1
                    self.store.save_checkpoint(checkpoint)
                    self._log_progress(completed_turns_for_plan, total_turns)

            runbook_summary = scenario_package.runbook_module.summarize_scenario(turn_results)
            scenario_summary = self._scenario_summary_payload(scenario, runbook_summary, turn_results)
            scenario_summaries.append(scenario_summary)
            scenario_markdown = build_scenario_summary_markdown(
                self.config.run_id,
                scenario,
                scenario_summary,
                turn_results,
            )
            self.store.write_json(f"scenarios/{scenario_package.scenario_id}/summary.json", scenario_summary)
            self.store.write_text(f"scenarios/{scenario_package.scenario_id}/summary.md", scenario_markdown)
            self._write_workspace_reports(workspace_id, scenario_package.scenario_id, scenario_markdown)
            self._log(
                f"[SCENARIO][DONE] {scenario_package.scenario_id} "
                f"avg_score={scenario_summary['average_score']:.2f}"
            )

        overall_score = round(
            sum(item["average_score"] for item in scenario_summaries) / max(1, len(scenario_summaries)),
            2,
        )
        overall_summary = {
            "run_id": self.config.run_id,
            "overall_score": overall_score,
            "completed_turns": len(checkpoint.completed_turns),
            "scenario_summaries": scenario_summaries,
        }
        report_md = build_overall_report_markdown(self.config.run_id, overall_summary)
        self.store.write_json("reports/overall_summary.json", overall_summary)
        self.store.write_text("reports/report.md", report_md)
        for workspace_id in workspace_ids_for_index:
            self._write_workspace_reports(
                workspace_id,
                scenario_id="overall",
                scenario_markdown=report_md,
                overall_report=report_md,
            )

        self._log(f"[RUN][DONE] run_id={self.config.run_id} overall_score={overall_score:.2f}")
        self.store.export_console_replay()
        return overall_summary






