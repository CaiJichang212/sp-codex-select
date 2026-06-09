from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "install_codex_assets.sh"


class InstallCodexAssetsTest(unittest.TestCase):
    def run_installer(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(INSTALLER), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "repo"
            result = self.run_installer("--dry-run", str(target))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("DRY RUN", result.stdout)
            self.assertFalse((target / ".agents").exists())
            self.assertFalse((target / ".codex").exists())

    def test_existing_install_refuses_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "repo"
            existing = target / ".agents" / "skills" / "sp-codex-select"
            existing.mkdir(parents=True)
            marker = existing / "local-change.txt"
            marker.write_text("keep me", encoding="utf-8")

            result = self.run_installer(str(target))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("already exists", result.stderr)
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep me")

    def test_force_install_backs_up_existing_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "repo"
            existing = target / ".agents" / "skills" / "sp-codex-select"
            existing.mkdir(parents=True)
            marker = existing / "local-change.txt"
            marker.write_text("keep me", encoding="utf-8")

            result = self.run_installer("--force", str(target))

            self.assertEqual(result.returncode, 0, result.stderr)
            backups = sorted((target / ".agents" / "skills").glob("sp-codex-select.backup-*"))
            self.assertEqual(len(backups), 1)
            self.assertEqual((backups[0] / "local-change.txt").read_text(encoding="utf-8"), "keep me")
            self.assertTrue((target / ".agents" / "skills" / "sp-codex-select" / "SKILL.md").exists())
            self.assertTrue(any((target / ".codex" / "agents").glob("spc_*.toml")))

    def test_rejects_root_target(self) -> None:
        result = self.run_installer("--dry-run", "/")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Refusing unsafe target", result.stderr)


if __name__ == "__main__":
    unittest.main()
