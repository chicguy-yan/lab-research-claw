"""Path security utilities - resolve and validate user-supplied paths.

Solves PRD §6.9 high-risk: prevent path traversal attacks.
"""

from __future__ import annotations

from pathlib import Path

# Directories that allow write operations (relative to workspace root)
WRITABLE_PREFIXES = ("memory/", "assets/", "context_trace/", "skills/", "temporary_dir/")
# Control-plane files that may be updated directly at workspace root.
ROOT_WRITABLE_FILES = frozenset({
    "AGENTS.md",
    "BOOTSTRAP.md",
    "IDENTITY.md",
    "MEMORY.md",
    "SOUL.md",
    "TOOLS.md",
    "USER.md",
})


class PathSecurityError(Exception):
    """Raised when a user-supplied path violates security constraints."""


def resolve_safe_path(
    base_dir: Path,
    user_path: str,
    *,
    require_writable: bool = False,
) -> Path:
    """Resolve *user_path* relative to *base_dir* and validate safety."""
    if ".." in user_path.replace("\\", "/").split("/"):
        raise PathSecurityError(f"Path traversal detected: {user_path}")

    resolved = (base_dir / user_path).resolve()
    base_resolved = base_dir.resolve()

    try:
        resolved.relative_to(base_resolved)
    except ValueError as exc:
        raise PathSecurityError(f"Path escapes workspace boundary: {user_path}") from exc

    if require_writable:
        rel = str(resolved.relative_to(base_resolved)).replace("\\", "/")
        is_root_control_file = "/" not in rel and rel in ROOT_WRITABLE_FILES
        if not is_root_control_file and not any(rel.startswith(prefix) for prefix in WRITABLE_PREFIXES):
            allowed = list(WRITABLE_PREFIXES) + sorted(ROOT_WRITABLE_FILES)
            raise PathSecurityError(
                f"Path is not in a writable directory: {user_path} (allowed: {', '.join(allowed)})"
            )

    return resolved


def resolve_safe_dir(base_dir: Path, user_cwd: str | None) -> Path:
    """Resolve a workspace-relative directory and ensure it exists."""
    safe_dir = resolve_safe_path(base_dir, user_cwd or ".", require_writable=False)
    if not safe_dir.exists():
        raise PathSecurityError(f"CWD not found: {user_cwd}")
    if not safe_dir.is_dir():
        raise PathSecurityError(f"CWD is not a directory: {user_cwd}")
    return safe_dir


def resolve_safe_path_from_cwd(
    base_dir: Path,
    user_path: str,
    *,
    cwd: str = ".",
    require_writable: bool = False,
) -> Path:
    """Resolve *user_path* relative to *cwd* inside *base_dir* safely."""
    if not user_path:
        raise PathSecurityError("Path cannot be empty")

    path_obj = Path(user_path)
    if path_obj.is_absolute():
        return resolve_safe_path(base_dir, user_path, require_writable=require_writable)

    safe_cwd = resolve_safe_dir(base_dir, cwd)
    base_resolved = base_dir.resolve()
    cwd_relative = safe_cwd.resolve().relative_to(base_resolved)
    combined = cwd_relative / path_obj
    return resolve_safe_path(
        base_dir,
        str(combined).replace("\\", "/"),
        require_writable=require_writable,
    )
