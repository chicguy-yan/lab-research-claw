from __future__ import annotations

import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import config as cfg
from graph.context_orchestrator import ContextOrchestrator
from graph.prompt_builder import PromptBuilder


class SystemPromptContractTests(unittest.TestCase):
    def test_prompt_includes_execution_authenticity_contract(self) -> None:
        workspace = cfg.DEFAULT_WORKSPACE_DIR
        memory_map = ContextOrchestrator(workspace).generate_memory_map(
            "write a hello file into memory concepts"
        )
        prompt = PromptBuilder(workspace).build(
            memory_map=memory_map,
            metadata={"current_date": "2026-03-12"},
        )

        self.assertIn("Control Plane Files are preloaded by the system prompt.", prompt)
        self.assertIn("Only say", prompt)
        self.assertIn("Asset Traceability Rule", prompt)

    def test_bootstrap_template_contains_question_and_answer_placeholders(self) -> None:
        bootstrap_template = cfg.WORKSPACE_TEMPLATES_DIR / "BOOTSTRAP.md"
        content = bootstrap_template.read_text(encoding="utf-8")

        self.assertIn("<!-- BOOTSTRAP_QUESTION_START -->", content)
        self.assertIn("<!-- BOOTSTRAP_QUESTION_END -->", content)
        self.assertIn("<!-- BOOTSTRAP_QA_START -->", content)
        self.assertIn("<!-- BOOTSTRAP_QA_END -->", content)
        self.assertIn("update `IDENTITY.md`", content)
        self.assertIn("update `USER.md`", content)
        self.assertIn("update `SOUL.md`", content)


if __name__ == "__main__":
    unittest.main()
