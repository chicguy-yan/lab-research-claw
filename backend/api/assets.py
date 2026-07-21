"""Assets API - 文件上传 + 下载 + 轻量摘要

Phase 4 职责：上传文件到 assets 子目录
Phase 5.2 新增：
- 自动分类（auto 模式根据扩展名选目录）
- SHA8 命名去重（防同名覆盖破坏溯源）
- quick_summary（轻量文件元信息）
- download 端点（支持二进制文件预览/下载）

Phase 5.3: workspace-aware via X-Workspace-Id header.
"""

from __future__ import annotations

import hashlib
import mimetypes
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse

from api.runtime_context import get_runtime
from graph.path_utils import PathSecurityError, resolve_safe_path

router = APIRouter(prefix="/assets", tags=["assets"])

# 扩展名 → 目标子目录
AUTO_CLASSIFY = {
    ".csv": "data", ".xlsx": "data", ".xls": "data", ".tsv": "data",
    ".pdf": "uploads",
    ".pptx": "ppt_pack", ".ppt": "ppt_pack",
    ".docx": "uploads", ".doc": "uploads",
    ".png": "figures", ".jpg": "figures", ".jpeg": "figures",
    ".tif": "figures", ".tiff": "figures", ".svg": "figures", ".bmp": "figures",
    ".md": "uploads", ".txt": "uploads", ".json": "data",
}

ALLOWED_DIRS = ["uploads", "data", "figures", "ppt_pack"]


def _detect_file_type(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    return suffix.lstrip(".") if suffix else "unknown"


def _quick_summary(file_path: Path, file_type: str) -> str:
    """轻量摘要，只做文件级元信息，不做深度解析。"""
    size_kb = file_path.stat().st_size / 1024
    if file_type in ("csv", "tsv"):
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                first_line = f.readline().strip()
                lines = 1 + sum(1 for _ in f)
            return f"CSV, {lines} 行, 列: {first_line[:100]}"
        except Exception:
            return f"CSV, {size_kb:.0f}KB"
    if file_type in ("xlsx", "xls"):
        return f"Excel (.{file_type}), {size_kb:.0f}KB"
    if file_type == "pdf":
        try:
            from pypdf import PdfReader
            return f"PDF, {len(PdfReader(str(file_path)).pages)} 页, {size_kb:.0f}KB"
        except Exception:
            return f"PDF, {size_kb:.0f}KB"
    if file_type in ("pptx", "ppt"):
        return f"PPT (.{file_type}), {size_kb:.0f}KB"
    if file_type in ("docx", "doc"):
        return f"Word (.{file_type}), {size_kb:.0f}KB"
    if file_type in ("png", "jpg", "jpeg", "tif", "tiff", "svg", "bmp"):
        return f"图片 (.{file_type}), {size_kb:.0f}KB"
    return f".{file_type} 文件, {size_kb:.0f}KB"


@router.post("/upload")
async def upload_asset(
    request: Request,
    file: UploadFile = File(...),
    target_dir: str = "auto",
):
    """
    上传文件到 assets。

    Args:
        file: 上传的文件
        target_dir: 目标目录。"auto" 根据扩展名自动分类，
                    或指定 uploads/data/figures/ppt_pack

    Returns:
        saved_path, sha256, size, file_type, mime_type, target_dir, quick_summary
    """
    filename = file.filename or "unnamed"
    file_type = _detect_file_type(filename)
    suffix = Path(filename).suffix.lower()

    # 自动分类
    if target_dir == "auto":
        target_dir = AUTO_CLASSIFY.get(suffix, "uploads")

    if target_dir not in ALLOWED_DIRS:
        raise HTTPException(400, f"Invalid target_dir: {target_dir}. Allowed: {ALLOWED_DIRS}")

    workspace_dir = get_runtime(request).workspace_dir

    try:
        content = await file.read()
        sha256 = hashlib.sha256(content).hexdigest()
        sha8 = sha256[:8]

        # SHA8 前缀命名：防同名覆盖，同内容幂等
        safe_filename = f"{sha8}_{filename}"
        relative_path = f"assets/{target_dir}/{safe_filename}"

        target_path = resolve_safe_path(workspace_dir, relative_path, require_writable=True)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(content)

        mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        summary = _quick_summary(target_path, file_type)

        return {
            "saved_path": relative_path,
            "sha256": sha256,
            "size": len(content),
            "file_type": file_type,
            "mime_type": mime_type,
            "target_dir": target_dir,
            "quick_summary": summary,
        }

    except PathSecurityError as e:
        raise HTTPException(403, f"Path security violation: {e}")
    except Exception as e:
        raise HTTPException(500, f"Failed to upload file: {str(e)}")


@router.get("/download")
async def download_asset(request: Request, path: str = Query(..., description="Asset path relative to workspace")):
    """下载/预览 asset 文件（支持二进制）。仅允许 assets/ 目录下的文件。"""
    workspace_dir = get_runtime(request).workspace_dir

    try:
        resolved = resolve_safe_path(workspace_dir, path)
    except PathSecurityError as e:
        raise HTTPException(403, str(e))

    # 仅允许 assets/ 下的文件
    rel = str(resolved.relative_to(workspace_dir.resolve())).replace("\\", "/")
    if not rel.startswith("assets/"):
        raise HTTPException(403, "Only assets/ files can be downloaded")

    if not resolved.exists():
        raise HTTPException(404, f"File not found: {path}")
    if resolved.is_dir():
        raise HTTPException(400, f"Path is a directory: {path}")

    return FileResponse(resolved, filename=resolved.name)
