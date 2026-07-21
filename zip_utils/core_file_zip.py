from __future__ import annotations

import argparse
import fnmatch
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT = SCRIPT_DIR / "core_files_bundle.zip"
DEFAULT_MANIFEST = SCRIPT_DIR / "core_files_manifest.md"
BACKEND_PYTHON_ROOTS = (
    "app.py",
    "config.py",
    "api",
    "graph",
    "runtime",
    "scripts",
    "skills",
    "tests",
    "tools",
)


@dataclass(frozen=True)
class BundleCategory:
    name: str
    description: str


CATEGORIES = OrderedDict(
    [
        (
            BundleCategory(
                name="backend_python",
                description="All Python source files from the backend's application, runtime, tools, skills, scripts, and tests.",
            ),
            "backend_python",
        ),
        (
            BundleCategory(
                name="workspace_templates",
                description="Markdown and JSON files under backend/workspace-templates that define prompts, memory, context trace, and workspace scaffolding.",
            ),
            "workspace_templates",
        ),
        (
            BundleCategory(
                name="backend_support",
                description="Non-Python backend files that help explain dependencies, skill behavior, and bundle generation.",
            ),
            "backend_support",
        ),
        (
            BundleCategory(
                name="frontend_core",
                description="Frontend source and key configs that explain how the UI talks to the backend and renders the workspace flow.",
            ),
            "frontend_core",
        ),
    ]
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a curated zip bundle of the project's core backend/frontend files."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Zip output path. Defaults to {DEFAULT_OUTPUT}",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help=f"Manifest output path. Defaults to {DEFAULT_MANIFEST}",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Resolve the bundle without writing files.",
    )
    parser.add_argument(
        "--list-files",
        action="store_true",
        help="Print every included file path after the summary.",
    )
    return parser.parse_args()


def relative_key(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def archive_key(path: Path) -> str:
    try:
        return relative_key(path)
    except ValueError:
        return path.name


def is_excluded_by_pattern(relative_path: Path, patterns: tuple[str, ...]) -> bool:
    rel_posix = relative_path.as_posix()
    return any(fnmatch.fnmatch(rel_posix, pattern) for pattern in patterns)


def collect_backend_python() -> list[Path]:
    backend_dir = REPO_ROOT / "backend"
    files: list[Path] = []
    for entry in BACKEND_PYTHON_ROOTS:
        candidate = backend_dir / entry
        if candidate.is_file() and candidate.suffix.lower() == ".py":
            files.append(candidate)
            continue
        if candidate.is_dir():
            files.extend(path for path in candidate.rglob("*.py") if path.is_file())
    return sorted(set(files), key=relative_key)


def collect_workspace_templates() -> list[Path]:
    template_dir = REPO_ROOT / "backend" / "workspace-templates"
    allowed_suffixes = {".md", ".json"}
    return sorted(
        path
        for path in template_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in allowed_suffixes
    )


def collect_backend_support() -> list[Path]:
    files: list[Path] = []
    explicit_files = [
        REPO_ROOT / "backend" / ".env.example",
        REPO_ROOT / "backend" / "requirements.txt",
        REPO_ROOT / "backend" / "requirements.lock",
        REPO_ROOT / "backend" / "skills" / "README.md",
        REPO_ROOT / "backend" / "skills" / "registry.json",
        REPO_ROOT / "backend" / "scripts" / "README_SKILL_CREATOR.md",
        REPO_ROOT / "zip_utils" / "core_file_zip.py",
    ]
    files.extend(path for path in explicit_files if path.is_file())

    skill_dir = REPO_ROOT / "backend" / "skills"
    allowed_suffixes = {".md", ".json", ".xml", ".txt", ".html"}
    excluded_patterns = (
        "*/schemas/*",
        "*/__pycache__/*",
    )
    for path in sorted(skill_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in allowed_suffixes:
            continue
        relative_path = path.relative_to(skill_dir)
        if is_excluded_by_pattern(relative_path, excluded_patterns):
            continue
        files.append(path)

    return sorted(set(files), key=relative_key)


def collect_frontend_core() -> list[Path]:
    frontend_dir = REPO_ROOT / "frontend"
    files: list[Path] = []

    explicit_files = [
        frontend_dir / "package.json",
        frontend_dir / "index.html",
        frontend_dir / "tsconfig.json",
        frontend_dir / "tsconfig.node.json",
        frontend_dir / "vite.config.ts",
        frontend_dir / "playwright.config.ts",
    ]
    files.extend(path for path in explicit_files if path.is_file())

    src_dir = frontend_dir / "src"
    allowed_suffixes = {".ts", ".tsx", ".css", ".d.ts"}
    excluded_patterns = (
        "test/*",
        "**/test/*",
        "**/*.test.ts",
        "**/*.test.tsx",
    )
    for path in sorted(src_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in allowed_suffixes:
            continue
        relative_path = path.relative_to(src_dir)
        if is_excluded_by_pattern(relative_path, excluded_patterns):
            continue
        files.append(path)

    return sorted(set(files), key=relative_key)


def collect_bundle() -> OrderedDict[BundleCategory, list[Path]]:
    collectors = {
        "backend_python": collect_backend_python,
        "workspace_templates": collect_workspace_templates,
        "backend_support": collect_backend_support,
        "frontend_core": collect_frontend_core,
    }

    collected: OrderedDict[BundleCategory, list[Path]] = OrderedDict()
    seen: set[str] = set()
    for category, collector_key in CATEGORIES.items():
        category_files: list[Path] = []
        for path in collectors[collector_key]():
            rel_path = relative_key(path)
            if rel_path in seen:
                continue
            seen.add(rel_path)
            category_files.append(path)
        collected[category] = category_files
    return collected


def render_manifest(bundle: OrderedDict[BundleCategory, list[Path]], output_path: Path) -> str:
    total_files = sum(len(paths) for paths in bundle.values())
    lines = [
        "# Core File Bundle Manifest",
        "",
        f"Archive target: `{output_path}`",
        f"Repository root: `{REPO_ROOT}`",
        f"Included files: `{total_files}`",
        "",
        "## Selection Rules",
    ]
    for category, paths in bundle.items():
        lines.append(f"- `{category.name}`: {category.description} ({len(paths)} files)")

    lines.append("")
    lines.append("## Included Files")
    for category, paths in bundle.items():
        lines.append("")
        lines.append(f"### {category.name} ({len(paths)})")
        for path in paths:
            lines.append(f"- `{relative_key(path)}`")

    lines.append("")
    return "\n".join(lines)


def write_bundle(
    bundle: OrderedDict[BundleCategory, list[Path]],
    output_path: Path,
    manifest_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    manifest_text = render_manifest(bundle, output_path)
    manifest_path.write_text(manifest_text, encoding="utf-8")

    with ZipFile(output_path, "w", compression=ZIP_DEFLATED) as archive:
        for paths in bundle.values():
            for path in paths:
                archive.write(path, arcname=relative_key(path))
        archive.writestr(archive_key(manifest_path), manifest_text)


def print_summary(
    bundle: OrderedDict[BundleCategory, list[Path]],
    output_path: Path,
    manifest_path: Path,
    *,
    list_files: bool,
    dry_run: bool,
) -> None:
    total_files = sum(len(paths) for paths in bundle.values())
    action = "Planned" if dry_run else "Created"
    print(f"{action} bundle: {output_path}")
    if not dry_run:
        print(f"Manifest: {manifest_path}")
    print(f"Total files: {total_files}")
    for category, paths in bundle.items():
        print(f"- {category.name}: {len(paths)}")

    if list_files:
        print("")
        for category, paths in bundle.items():
            print(f"[{category.name}]")
            for path in paths:
                print(relative_key(path))
            print("")


def main() -> int:
    args = parse_args()
    bundle = collect_bundle()
    if args.dry_run:
        print_summary(
            bundle,
            args.output.resolve(),
            args.manifest.resolve(),
            list_files=args.list_files,
            dry_run=True,
        )
        return 0

    output_path = args.output.resolve()
    manifest_path = args.manifest.resolve()
    write_bundle(bundle, output_path, manifest_path)
    print_summary(
        bundle,
        output_path,
        manifest_path,
        list_files=args.list_files,
        dry_run=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
