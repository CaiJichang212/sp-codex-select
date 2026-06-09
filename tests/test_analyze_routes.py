from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "scripts" / "analyze_routes.py"


class AnalyzeRoutesTest(unittest.TestCase):
    def test_analyzes_jsonl_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            log = Path(temp) / "routes.jsonl"
            records = [
                {"task_id": "T1", "role": "implementer", "tier": "T1", "agent": "spc_quick", "model": "gpt-5.4-mini", "score": 1, "status": "DONE", "review_pass": True, "tests_pass": True, "escalated": False},
                {"task_id": "T2", "role": "implementer", "tier": "T2", "agent": "spc_spark", "model": "gpt-5.3-codex-spark", "score": 5, "status": "DONE_WITH_CONCERNS", "review_pass": False, "tests_pass": True, "escalated": True}
            ]
            log.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")
            result = subprocess.run(
                ["python3", "-B", str(ANALYZER), str(log)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("route_count=2", result.stdout)
            self.assertIn("review_failure_rate=0.50", result.stdout)
            self.assertIn("escalation_rate=0.50", result.stdout)

    def test_reports_missing_required_field(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            log = Path(temp) / "routes.jsonl"
            log.write_text(json.dumps({"task_id": "T1"}) + "\n", encoding="utf-8")
            result = subprocess.run(
                ["python3", "-B", str(ANALYZER), str(log)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing required field", result.stderr)

    def test_empty_jsonl_reports_clean_error_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            log = Path(temp) / "routes.jsonl"
            log.write_text("", encoding="utf-8")
            result = subprocess.run(
                ["python3", "-B", str(ANALYZER), str(log)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("no route records found", result.stderr)
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
