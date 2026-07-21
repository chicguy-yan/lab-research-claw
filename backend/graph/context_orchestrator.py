"""Context Orchestrator - 生成 Memory Map（简化版）

Phase 3 职责：
- 扫描 workspace 的 memory 目录结构
- 生成 Memory Map（Layer 1/2/3 + Assets）
- 基于用户消息推荐相关文件（简单关键词匹配）
"""

from __future__ import annotations

from pathlib import Path


class ContextOrchestrator:
    """简化版 Context Orchestrator - 只生成 Memory Map"""

    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir

    def generate_memory_map(self, user_message: str = None) -> dict:
        """
        生成 Memory Map (目录结构 + 可选的推荐文件)

        Args:
            user_message: 用户消息，用于推荐相关文件

        Returns:
            {
                "layer1": ["memory/identity/user.md", ...],
                "layer2": ["memory/timeline/180d_index.md", ...],
                "layer3": ["memory/concepts/CONCEPT_*.md", ...],
                "assets": ["assets/uploads/", ...],
                "recommended": ["memory/identity/project.md", ...]  # 可选
            }
        """
        memory_map = {
            "layer1": self._scan_layer1(),
            "layer2": self._scan_layer2(),
            "layer3": self._scan_layer3(),
            "assets": self._scan_assets(),
        }

        # 可选: 基于用户消息推荐文件
        if user_message:
            memory_map["recommended"] = self._recommend_files(user_message)

        return memory_map

    def _scan_layer1(self) -> list[str]:
        """扫描 Layer1 文件（Identity 层）"""
        layer1_dir = self.workspace_dir / "memory" / "identity"
        if not layer1_dir.exists():
            return []
        return [
            str(f.relative_to(self.workspace_dir))
            for f in layer1_dir.glob("*.md")
            if f.is_file()
        ]

    def _scan_layer2(self) -> list[str]:
        """扫描 Layer2 文件（Timeline 层）"""
        layer2_dir = self.workspace_dir / "memory" / "timeline"
        if not layer2_dir.exists():
            return []

        files = []

        # 180d_index
        index_file = layer2_dir / "180d_index.md"
        if index_file.exists():
            files.append(str(index_file.relative_to(self.workspace_dir)))

        # phases
        phases_dir = layer2_dir / "phases"
        if phases_dir.exists():
            files.extend([
                str(f.relative_to(self.workspace_dir))
                for f in phases_dir.glob("*.md")
                if f.is_file()
            ])

        # 最近的 weeks (最多5个)
        weeks_dir = layer2_dir / "weeks"
        if weeks_dir.exists():
            weeks = sorted(weeks_dir.glob("*.md"), reverse=True)[:5]
            files.extend([
                str(f.relative_to(self.workspace_dir))
                for f in weeks
                if f.is_file()
            ])

        # 最近的 days (最多10个)
        days_dir = layer2_dir / "days"
        if days_dir.exists():
            days = sorted(days_dir.glob("*.md"), reverse=True)[:10]
            files.extend([
                str(f.relative_to(self.workspace_dir))
                for f in days
                if f.is_file()
            ])

        # stage_reports (阶段汇报，最近5个)
        stage_reports_dir = layer2_dir / "stage_reports"
        if stage_reports_dir.exists():
            stage_reports = sorted(stage_reports_dir.glob("*.md"), reverse=True)[:5]
            files.extend([
                str(f.relative_to(self.workspace_dir))
                for f in stage_reports
                if f.is_file()
            ])

        return files

    def _scan_layer3(self) -> list[str]:
        """扫描 Layer3 文件（Atom Notes 层）"""
        layer3_dir = self.workspace_dir / "memory"
        if not layer3_dir.exists():
            return []

        files = []

        # concepts
        concepts_dir = layer3_dir / "concepts"
        if concepts_dir.exists():
            files.extend([
                str(f.relative_to(self.workspace_dir))
                for f in concepts_dir.glob("*.md")
                if f.is_file()
            ])

        # tasks
        tasks_dir = layer3_dir / "tasks"
        if tasks_dir.exists():
            files.extend([
                str(f.relative_to(self.workspace_dir))
                for f in tasks_dir.glob("*.md")
                if f.is_file()
            ])

        # packs
        packs_dir = layer3_dir / "packs"
        if packs_dir.exists():
            files.extend([
                str(f.relative_to(self.workspace_dir))
                for f in packs_dir.glob("*.md")
                if f.is_file()
            ])

        return files

    def _scan_assets(self) -> list[dict]:
        """扫描 Assets 目录，返回文件级清单（Phase 5.2 增强）"""
        assets_dir = self.workspace_dir / "assets"
        if not assets_dir.exists():
            return []

        result = []
        subdirs = ["uploads", "data", "figures", "ppt_pack"]
        for subdir in subdirs:
            sub_path = assets_dir / subdir
            if not sub_path.exists():
                continue
            for f in sorted(sub_path.iterdir()):
                if f.is_file() and not f.name.startswith("."):
                    result.append({
                        "path": str(f.relative_to(self.workspace_dir)),
                        "type": f.suffix.lstrip(".").lower() or "unknown",
                        "size": f.stat().st_size,
                    })
        return result

    def _recommend_files(self, user_message: str) -> list[str]:
        """基于用户消息推荐文件 (简单关键词匹配)"""
        recommended = []

        # 总是推荐 project.md
        project_file = self.workspace_dir / "memory/identity/project.md"
        if project_file.exists():
            recommended.append("memory/identity/project.md")

        # 关键词匹配
        if "汇报" in user_message or "R0" in user_message:
            index_file = self.workspace_dir / "memory/timeline/180d_index.md"
            if index_file.exists():
                recommended.append("memory/timeline/180d_index.md")

            # 查找最近的 stage_report
            stage_reports_dir = self.workspace_dir / "memory/timeline/stage_reports"
            if stage_reports_dir.exists():
                stage_reports = sorted(stage_reports_dir.glob("*.md"), reverse=True)
                if stage_reports:
                    recommended.append(str(stage_reports[0].relative_to(self.workspace_dir)))

        if "合成" in user_message or "checklist" in user_message:
            lab_context = self.workspace_dir / "memory/identity/lab_context.md"
            if lab_context.exists():
                recommended.append("memory/identity/lab_context.md")

        if "机理" in user_message or "证据链" in user_message:
            # 查找 mechanism 相关的 packs
            packs_dir = self.workspace_dir / "memory/packs"
            if packs_dir.exists():
                mechanism_packs = packs_dir.glob("PACK_mechanism_*.md")
                recommended.extend([
                    str(f.relative_to(self.workspace_dir))
                    for f in mechanism_packs
                    if f.is_file()
                ])

        return recommended
