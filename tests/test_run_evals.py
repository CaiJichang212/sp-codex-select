from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_EVALS = ROOT / "scripts" / "run_evals.py"


class RunEvalsTest(unittest.TestCase):
    def run_eval(self, suite: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(RUN_EVALS), "--suite", str(suite)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_route_suite_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            suite = Path(temp) / "routes.json"
            suite.write_text(json.dumps({
                "suite": "routes",
                "cases": [{
                    "id": "route-quick-readme",
                    "role": "implementer",
                    "text": "Fix typo in README",
                    "expect": {
                        "tier": "T1",
                        "agent_type": "spc_quick",
                        "sandbox_mode": "workspace-write",
                        "hard_flags": []
                    }
                }]
            }), encoding="utf-8")
            result = self.run_eval(suite)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("passed=1 failed=0", result.stdout)

    def test_route_suite_reports_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            suite = Path(temp) / "routes.json"
            suite.write_text(json.dumps({
                "suite": "routes",
                "cases": [{
                    "id": "route-wrong-tier",
                    "role": "implementer",
                    "text": "Fix typo in README",
                    "expect": {"tier": "T4"}
                }]
            }), encoding="utf-8")
            result = self.run_eval(suite)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("route-wrong-tier", result.stdout)
            self.assertIn("expected", result.stdout)
            self.assertIn("actual", result.stdout)

    def test_query_suite_passes_negative_case(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            suite = Path(temp) / "queries.json"
            suite.write_text(json.dumps({
                "suite": "queries",
                "cases": [{
                    "id": "query-general-llm",
                    "text": "Which LLM should I use for writing a poem?",
                    "expected_use_skill": False
                }]
            }), encoding="utf-8")
            result = self.run_eval(suite)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("passed=1 failed=0", result.stdout)

    def test_query_suite_matches_final_verifier_trigger(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            suite = Path(temp) / "queries.json"
            suite.write_text(json.dumps({
                "suite": "queries",
                "cases": [{
                    "id": "query-final-verifier",
                    "text": "Select a final verifier for a release-critical branch.",
                    "expected_use_skill": True
                }]
            }), encoding="utf-8")
            result = self.run_eval(suite)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("passed=1 failed=0", result.stdout)

    def test_query_suite_matches_reviewer_role_trigger(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            suite = Path(temp) / "queries.json"
            suite.write_text(json.dumps({
                "suite": "queries",
                "cases": [{
                    "id": "query-reviewer-roles",
                    "text": "Map reviewer roles to spec-review and quality-review agents.",
                    "expected_use_skill": True
                }]
            }), encoding="utf-8")
            result = self.run_eval(suite)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("passed=1 failed=0", result.stdout)

    def test_schema_error_names_case_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            suite = Path(temp) / "broken.json"
            suite.write_text(json.dumps({
                "suite": "routes",
                "cases": [{"id": "missing-text", "expect": {"tier": "T1"}}]
            }), encoding="utf-8")
            result = self.run_eval(suite)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing-text", result.stderr)
            self.assertIn("text", result.stderr)


if __name__ == "__main__":
    unittest.main()
