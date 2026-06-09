from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_skill.py"


def copy_clean_tree(target: Path) -> None:
    shutil.copytree(
        ROOT,
        target,
        ignore=shutil.ignore_patterns(".git", "__pycache__", ".DS_Store", "*.pyc"),
    )


class ValidateSkillTest(unittest.TestCase):
    def run_validator(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", "-B", str(VALIDATOR), *args],
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

    def test_runtime_stage_accepts_installed_runtime_skill_without_source_materials(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            copy = Path(temp) / "runtime-skill"
            copy.mkdir()
            for file_name in ["SKILL.md", "README.md"]:
                shutil.copy2(ROOT / file_name, copy / file_name)
            for dir_name in ["scripts", "assets", "references", "agents"]:
                shutil.copytree(ROOT / dir_name, copy / dir_name)

            result = self.run_validator("--stage", "runtime", str(copy))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("OK: runtime", result.stdout)

    def test_missing_governance_fails_pilot_with_actionable_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            copy = Path(temp) / "skill"
            copy_clean_tree(copy)
            shutil.rmtree(copy / "governance")
            result = self.run_validator("--stage", "pilot", str(copy))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("governance/risk_assessment.md", result.stderr)

    def test_missing_openai_yaml_fields_fail_pilot(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            copy = Path(temp) / "skill"
            copy_clean_tree(copy)
            (copy / "agents" / "openai.yaml").write_text("name: sp-codex-select\n", encoding="utf-8")
            result = self.run_validator("--stage", "pilot", str(copy))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("agents/openai.yaml missing short_description", result.stderr)
            self.assertIn("agents/openai.yaml missing default_prompt", result.stderr)

    def test_model_map_drift_fails_pilot(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            copy = Path(temp) / "skill"
            copy_clean_tree(copy)
            model_map = copy / "references" / "model-map.json"
            payload = json.loads(model_map.read_text(encoding="utf-8"))
            payload["tiers"]["quick"]["model"] = "wrong-model"
            model_map.write_text(json.dumps(payload), encoding="utf-8")
            result = self.run_validator("--stage", "pilot", str(copy))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("model-map quick.model", result.stderr)

    def test_missing_frontmatter_metadata_fails_pilot(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            copy = Path(temp) / "skill"
            copy_clean_tree(copy)
            skill_path = copy / "SKILL.md"
            skill = skill_path.read_text(encoding="utf-8")
            skill = skill.replace(
                'metadata:\n  org.owner: "sp-codex-select maintainers"\n  org.version: "0.2.0"\n  org.status: "pilot"\n  org.risk_level: "R2"\n  org.last_reviewed: "2026-06-09"\n',
                "",
            )
            skill_path.write_text(skill, encoding="utf-8")
            result = self.run_validator("--stage", "pilot", str(copy))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SKILL.md frontmatter missing metadata.org.owner", result.stderr)

    def test_ignored_artifacts_fail_pilot(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            copy = Path(temp) / "skill"
            copy_clean_tree(copy)
            (copy / ".DS_Store").write_text("local artifact", encoding="utf-8")
            pycache = copy / "scripts" / "__pycache__"
            pycache.mkdir()
            (pycache / "route_tasks.cpython-312.pyc").write_bytes(b"local artifact")
            result = self.run_validator("--stage", "pilot", str(copy))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("ignored artifact present: .DS_Store", result.stderr)
            self.assertIn("ignored artifact present: scripts/__pycache__", result.stderr)


if __name__ == "__main__":
    unittest.main()
