#!/usr/bin/env python3
"""Mutation fixtures for the NPC material production-chain audit (#174).

The fixtures exercise only the public ``audit_repository(root)`` surface.  Each
mutation lives in a temporary repository fragment, so the real NPC drafts and
ledgers remain byte-for-byte unchanged.
"""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from validate_npc_materials import audit_repository


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_REL = Path("design/spec/material/npc-materials-manifest.json")
DRAFTS_REL = Path("design/spec/material/drafts")
PATIENT_LEDGER_RELS = (
    Path("design/spec/material/患者生态索引.md"),
    Path("design/spec/material/多样性记账表.md"),
)
EXPECTED_REPLAYED = {
    "周卫国",
    "杨秀兰",
    "苏晴",
    "吴桐",
    "唐念安",
    "许一鸣",
    "贺春兰",
}


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


class NpcMaterialAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory(prefix="npc-material-audit-")
        self.root = Path(self.tempdir.name)
        for relative in (MANIFEST_REL, *PATIENT_LEDGER_RELS):
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, destination)
        shutil.copytree(ROOT / DRAFTS_REL, self.root / DRAFTS_REL)

        # Mutation fixtures are independent of the documentation branch that
        # installs the real marked regions.  The real-baseline test below still
        # audits ROOT itself and therefore proves those markers exist in the
        # integrated repository.
        manifest = self.manifest()
        patient_names = [item["name"] for item in manifest["materials"] if item["patient_pool"]]
        other_names = [item["name"] for item in manifest["materials"] if not item["patient_pool"]]
        self._ensure_marked_region(
            self.root / PATIENT_LEDGER_RELS[0],
            "npc-patient-pool",
            patient_names,
        )
        self._ensure_marked_region(
            self.root / PATIENT_LEDGER_RELS[0],
            "npc-non-patient-materials",
            other_names,
        )
        self._ensure_marked_region(
            self.root / PATIENT_LEDGER_RELS[1],
            "npc-patient-pool",
            patient_names,
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    @staticmethod
    def _ensure_marked_region(path: Path, marker: str, names: list[str]) -> None:
        text = path.read_text(encoding="utf-8")
        start = f"<!-- {marker}:start -->"
        end = f"<!-- {marker}:end -->"
        if start in text or end in text:
            return
        lines = "\n".join(f"- {name}" for name in names)
        path.write_text(f"{text.rstrip()}\n\n{start}\n{lines}\n{end}\n", encoding="utf-8")

    def manifest(self) -> dict:
        return _read_json(self.root / MANIFEST_REL)

    def write_manifest(self, manifest: dict) -> None:
        _write_json(self.root / MANIFEST_REL, manifest)

    def entry(self, manifest: dict, name: str) -> dict:
        return next(item for item in manifest["materials"] if item["name"] == name)

    def assert_fails_with(self, *expected_codes: str):
        report = audit_repository(self.root)
        self.assertFalse(report.ok)
        self.assertTrue(report.findings)
        for code in expected_codes:
            self.assertIn(code, report.codes())
        return report

    def test_real_repository_baseline(self) -> None:
        report = audit_repository(ROOT)
        self.assertTrue(report.ok, [(item.code, item.subject) for item in report.findings])
        self.assertEqual(16, report.material_count)
        self.assertEqual(13, report.patient_count)
        self.assertEqual(7, report.replay_count)
        self.assertEqual(EXPECTED_REPLAYED, set(report.replayed_names))

    def test_fixture_baseline_matches_real_contract(self) -> None:
        report = audit_repository(self.root)
        self.assertTrue(report.ok, [(item.code, item.subject) for item in report.findings])
        self.assertEqual((16, 13, 7), (report.material_count, report.patient_count, report.replay_count))
        self.assertEqual(EXPECTED_REPLAYED, set(report.replayed_names))

    def test_missing_pair_members_fail(self) -> None:
        with self.subTest("missing-json"):
            path = self.root / DRAFTS_REL / "郑晓敏.gen.json"
            path.unlink()
            self.assert_fails_with("DRAFT_PAIR_MISSING_JSON", "MANIFEST_JSON_MISSING")
            shutil.copy2(ROOT / DRAFTS_REL / path.name, path)
        with self.subTest("missing-narrative"):
            path = self.root / DRAFTS_REL / "郑晓敏-叙事视图.md"
            path.unlink()
            self.assert_fails_with("DRAFT_PAIR_MISSING_NARRATIVE", "MANIFEST_NARRATIVE_MISSING")

    def test_manifest_omission_and_duplicates_fail(self) -> None:
        original = self.manifest()
        with self.subTest("omission"):
            mutated = json.loads(json.dumps(original, ensure_ascii=False))
            mutated["materials"] = [item for item in mutated["materials"] if item["name"] != "刘建军"]
            self.write_manifest(mutated)
            self.assert_fails_with("MATERIAL_COUNT_MISMATCH", "DRAFT_UNREGISTERED_JSON")
        with self.subTest("duplicate-name"):
            mutated = json.loads(json.dumps(original, ensure_ascii=False))
            mutated["materials"][1]["name"] = mutated["materials"][0]["name"]
            self.write_manifest(mutated)
            self.assert_fails_with("MANIFEST_DUPLICATE_NAME")
        with self.subTest("duplicate-path"):
            mutated = json.loads(json.dumps(original, ensure_ascii=False))
            mutated["materials"][1]["json_path"] = mutated["materials"][0]["json_path"]
            self.write_manifest(mutated)
            self.assert_fails_with("MANIFEST_DUPLICATE_JSON_PATH")

    def test_removed_or_false_declaration_cannot_replay(self) -> None:
        path = self.root / DRAFTS_REL / "贺春兰.gen.json"
        original = _read_json(path)
        with self.subTest("removed-block"):
            mutated = json.loads(json.dumps(original, ensure_ascii=False))
            del mutated["资格声明（#87 规范化声明）"]
            _write_json(path, mutated)
            self.assert_fails_with("ADAPTER_DECLARATION_BLOCK_MISSING")
        with self.subTest("required-atom-zero"):
            mutated = json.loads(json.dumps(original, ensure_ascii=False))
            mutated["资格声明（#87 规范化声明）"]["BINGE_HISTORY"] = 0
            _write_json(path, mutated)
            report = self.assert_fails_with("TARGET_REPLAY_NOT_ELIGIBLE")
            self.assertNotIn("贺春兰", report.replayed_names)

    def test_unknown_event_is_rejected_by_strict_input(self) -> None:
        path = self.root / DRAFTS_REL / "贺春兰.gen.json"
        draft = _read_json(path)
        draft["trauma_memories"][0]["event_type"] = "不存在的事件类型"
        _write_json(path, draft)
        self.assert_fails_with("ELIGIBILITY_INPUT_INVALID")

    def test_legacy_relabelled_validated_cannot_false_pass(self) -> None:
        manifest = self.manifest()
        self.entry(manifest, "顾维扬")["status"] = "validated"
        self.write_manifest(manifest)
        report = self.assert_fails_with("ADAPTER_DECLARATION_BLOCK_MISSING")
        self.assertNotIn("顾维扬", report.replayed_names)

    def test_patient_ledger_drift_fails_each_human_view(self) -> None:
        for relative in PATIENT_LEDGER_RELS:
            with self.subTest(ledger=str(relative)):
                path = self.root / relative
                original = path.read_text(encoding="utf-8")
                path.write_text(original.replace("- 顾维扬\n", "", 1), encoding="utf-8")
                self.assert_fails_with("PATIENT_LEDGER_MISMATCH")
                path.write_text(original, encoding="utf-8")

    def test_non_patient_ledger_drift_fails(self) -> None:
        path = self.root / PATIENT_LEDGER_RELS[0]
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("- 郑晓敏\n", "", 1), encoding="utf-8")
        self.assert_fails_with("NON_PATIENT_LEDGER_MISMATCH")

    def test_cli_returns_nonzero_and_prints_stable_code(self) -> None:
        (self.root / DRAFTS_REL / "郑晓敏.gen.json").unlink()
        result = subprocess.run(
            [sys.executable, str(ROOT / "code/tools/validate_npc_materials.py"), str(self.root)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(1, result.returncode)
        self.assertIn("DRAFT_PAIR_MISSING_JSON", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
