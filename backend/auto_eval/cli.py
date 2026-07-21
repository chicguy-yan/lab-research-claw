from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from auto_eval.models import EvalConfig
from auto_eval.runner import EvalRunner
from auto_eval.scenario_loader import resolve_scenario_paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="HTTP-driven auto evaluation runner")
    parser.add_argument("--backend-url", default="http://127.0.0.1:8002")
    parser.add_argument(
        "--scenario",
        action="append",
        required=True,
        help="Builtin letter (B/C/D/E) or a scenario package directory path. Repeatable.",
    )
    parser.add_argument("--source-root", default="")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--run-root", default="")
    parser.add_argument("--session-limit", type=int, default=None)
    parser.add_argument("--turn-limit", type=int, default=None)
    parser.add_argument("--judge-mode", default="heuristic", choices=["heuristic", "off"])
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--no-mirror", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=900)
    parser.add_argument("--max-turn-attempts", type=int, default=3)
    parser.add_argument("--retry-backoff-seconds", type=float, default=2.0)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    run_id = args.run_id or f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    base_dir = Path(__file__).resolve().parent
    run_root = Path(args.run_root) if args.run_root else (base_dir / "eval_runs" / run_id)
    scenario_paths = resolve_scenario_paths(args.scenario)
    source_root = Path(args.source_root).resolve() if args.source_root else None

    config = EvalConfig(
        backend_url=args.backend_url,
        run_id=run_id,
        run_root=run_root,
        scenario_paths=scenario_paths,
        source_root=source_root,
        session_limit=args.session_limit,
        turn_limit=args.turn_limit,
        judge_mode=args.judge_mode,
        mirror_to_workspace=not args.no_mirror,
        resume=args.resume,
        request_timeout_seconds=args.timeout_seconds,
        max_turn_attempts=args.max_turn_attempts,
        retry_backoff_seconds=args.retry_backoff_seconds,
    )
    EvalRunner(config).run()


if __name__ == "__main__":
    main()
