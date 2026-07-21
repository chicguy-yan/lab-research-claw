from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
import sys


def _build_new_state() -> dict:
    run_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return {
        "version": 1,
        "run_stamp": run_stamp,
        "run_ids": {
            "B": f"one_click_B_{run_stamp}",
            "C": f"one_click_C_{run_stamp}",
            "D": f"one_click_D_{run_stamp}",
            "E": f"one_click_E_{run_stamp}",
        },
        "status": {
            "B": "pending",
            "C": "pending",
            "D": "pending",
            "E": "pending",
        },
        "current_scenario": "",
        "finished": False,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "last_error": "",
    }


def _load_state(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = datetime.now().isoformat(timespec="seconds")
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _emit_env(state: dict, mode: str) -> None:
    print(f"MODE={mode}")
    print(f"RUN_STAMP={state['run_stamp']}")
    for letter in ("B", "C", "D", "E"):
        print(f"RUN_{letter}={state['run_ids'][letter]}")
        print(f"STATUS_{letter}={state['status'].get(letter, 'pending')}")
    print(f"FINISHED={'1' if state.get('finished') else '0'}")


def init_or_resume(state_file: Path) -> int:
    state = _load_state(state_file)
    if state is None or state.get("finished"):
        state = _build_new_state()
        mode = "new"
    else:
        mode = "resume"
    _save_state(state_file, state)
    _emit_env(state, mode)
    return 0


def update_state(state_file: Path, scenario: str, status: str, error: str = "") -> int:
    state = _load_state(state_file) or _build_new_state()
    scenario = scenario.upper()
    if scenario not in {"B", "C", "D", "E"}:
        raise SystemExit(f"Unsupported scenario: {scenario}")
    state["current_scenario"] = scenario
    state["status"][scenario] = status
    state["last_error"] = error
    state["finished"] = all(state["status"].get(letter) == "completed" for letter in ("B", "C", "D", "E"))
    _save_state(state_file, state)
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        raise SystemExit("Usage: one_click_state.py <init-or-resume|update> <state_file> [scenario] [status] [error]")

    command = argv[1]
    state_file = Path(argv[2])

    if command == "init-or-resume":
        return init_or_resume(state_file)

    if command == "update":
        if len(argv) < 5:
            raise SystemExit("Usage: one_click_state.py update <state_file> <scenario> <status> [error]")
        scenario = argv[3]
        status = argv[4]
        error = argv[5] if len(argv) > 5 else ""
        return update_state(state_file, scenario, status, error)

    raise SystemExit(f"Unknown command: {command}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
