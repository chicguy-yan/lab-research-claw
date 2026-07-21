from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from auto_eval.models import ScenarioPackage


def resolve_builtin_scenario_path(name: str) -> Path:
    base_dir = Path(__file__).resolve().parent
    normalized = name.strip().upper()
    mapping = {
        "B": base_dir / "B_questions_and_eval_methods",
        "C": base_dir / "C_questions_and_eval_methods",
        "D": base_dir / "D_questions_and_eval_methods",
        "E": base_dir / "E_questions_and_eval_methods",
    }
    if normalized not in mapping:
        raise ValueError(f"Unknown builtin scenario: {name}")
    return mapping[normalized]


def _discover_one(package_dir: Path, pattern: str) -> Path:
    matches = sorted(package_dir.glob(pattern))
    if len(matches) != 1:
        raise FileNotFoundError(f"Expected exactly one {pattern} in {package_dir}, got {len(matches)}")
    return matches[0]


def _load_module(module_path: Path):
    module_name = f"auto_eval_dynamic_{module_path.parent.name}_{module_path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to import scenario runbook: {module_path}")

    scenario_dir = str(module_path.parent)
    if scenario_dir not in sys.path:
        sys.path.insert(0, scenario_dir)

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_scenario_package(package_dir: Path) -> ScenarioPackage:
    package_dir = package_dir.resolve()
    question_file = _discover_one(package_dir, "*_scenario_questions.json")
    runbook_file = _discover_one(package_dir, "scenario_*_runbook.py")
    runbook_module = _load_module(runbook_file)

    if hasattr(runbook_module, "load_scenario_document"):
        document = runbook_module.load_scenario_document()
    else:
        payload = json.loads(question_file.read_text(encoding="utf-8-sig"))
        if not isinstance(payload, list) or len(payload) != 1:
            raise ValueError(f"Scenario file must contain a single scenario object: {question_file}")
        document = payload[0]

    if "scenario_id" not in document or "sessions" not in document:
        raise ValueError(f"Scenario document is missing required fields: {question_file}")

    return ScenarioPackage(
        scenario_id=document["scenario_id"],
        scenario_name=document.get("scenario_name", document["scenario_id"]),
        package_dir=package_dir,
        question_file=question_file,
        runbook_file=runbook_file,
        document=document,
        runbook_module=runbook_module,
    )


def resolve_scenario_paths(items: list[str]) -> list[Path]:
    paths: list[Path] = []
    for item in items:
        candidate = Path(item)
        if candidate.exists():
            paths.append(candidate.resolve())
            continue
        paths.append(resolve_builtin_scenario_path(item))
    return paths

