from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_skill.py"


class ValidateSkillTest(unittest.TestCase):
    def run_validator(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(VALIDATOR), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_help_mentions_stage(self) -> None:
        result = self.run_validator("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("--stage", result.stdout)

    def test_draft_stage_passes_current_tree_after_contract_sections(self) -> None:
        result = self.run_validator("--stage", "draft", ".")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK: draft", result.stdout)

    def test_pilot_stage_passes_current_tree_after_pilot_materials(self) -> None:
        result = self.run_validator("--stage", "pilot", ".")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK: pilot", result.stdout)

    def test_missing_governance_fails_pilot_with_actionable_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            copy = Path(temp) / "skill"
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            shutil.rmtree(copy / "governance")
            result = self.run_validator("--stage", "pilot", str(copy))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("governance/risk_assessment.md", result.stderr)


if __name__ == "__main__":
    unittest.main()
