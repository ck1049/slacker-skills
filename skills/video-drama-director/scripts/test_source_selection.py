"""选片区间与有意复用的声明回归；临时文本夹具不构成媒体检验。"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from validate_scene_plan import validate_plan


class SourceSelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        (self.base / "source.stub").write_text("not media", encoding="utf-8")
        (self.base / "evidence.txt").write_text("declaration fixture", encoding="utf-8")

    def selection(self, **fields: object) -> dict:
        return {
            "media_path": "source.stub",
            "end_evidence": "evidence.txt",
            "state_reviewed": True,
            **fields,
        }

    def check(self, *selections: dict) -> dict:
        plan = {
            "entities": {"prop": {"kind": "prop"}},
            "initial_state": {},
            "units": [
                {"id": f"shot-{i}", "selected": item}
                for i, item in enumerate(selections)
            ],
        }
        return validate_plan(plan, "execution", self.base)

    @staticmethod
    def errors(result: dict) -> set[str]:
        return {item["code"] for item in result["issues"] if item["severity"] == "error"}

    def test_adjacent_nonoverlapping_ranges_from_one_source_pass(self) -> None:
        result = self.check(
            self.selection(source_range_s=[0, 1]),
            self.selection(source_range_s=[1, 2]),
        )
        self.assertEqual([], result["issues"])

    def test_overlapping_and_identical_ranges_need_a_reason(self) -> None:
        for second in ([0, 1], [0.5, 1.5]):
            with self.subTest(second=second):
                result = self.check(
                    self.selection(source_range_s=[0, 1]),
                    self.selection(source_range_s=second),
                )
                self.assertIn("duplicate_selection", self.errors(result))

    def test_explicit_replay_is_a_warning_not_an_error(self) -> None:
        result = self.check(
            self.selection(source_range_s=[0, 1]),
            self.selection(source_range_s=[0, 1], reuse_reason="回忆同一事件"),
        )
        self.assertEqual(set(), self.errors(result))
        self.assertIn("intentional_reuse", {item["code"] for item in result["issues"]})

    def test_legacy_whole_source_selection_remains_supported(self) -> None:
        self.assertEqual([], self.check(self.selection())["issues"])
        self.assertIn("duplicate_selection", self.errors(self.check(self.selection(), self.selection())))

    def test_whole_source_overlaps_a_partial_selection(self) -> None:
        for selections in (
            [self.selection(), self.selection(source_range_s=[2, 3])],
            [self.selection(source_range_s=[2, 3]), self.selection()],
        ):
            with self.subTest(selections=selections):
                self.assertIn("duplicate_selection", self.errors(self.check(*selections)))

    def test_path_aliases_do_not_bypass_overlap_detection(self) -> None:
        result = self.check(
            self.selection(source_range_s=[0, 1]),
            self.selection(media_path=str(self.base / "source.stub"), source_range_s=[0, 1]),
        )
        self.assertIn("duplicate_selection", self.errors(result))

    def test_invalid_source_ranges_are_rejected(self) -> None:
        values = [None, "0,1", [], [0], [0, 1, 2], [-1, 1], [1, 1], [2, 1],
                  [False, 1], [0, True], [0, "1"], [0, float("inf")], [float("nan"), 1],
                  [0, 10 ** 400]]
        for value in values:
            with self.subTest(value=value):
                result = self.check(self.selection(source_range_s=value))
                self.assertIn("source_range", self.errors(result))

    def test_range_is_bounded_when_source_duration_is_declared(self) -> None:
        self.assertEqual([], self.check(self.selection(source_range_s=[1, 2], source_duration_s=2))["issues"])
        result = self.check(self.selection(source_range_s=[1, 3], source_duration_s=2))
        self.assertIn("source_range", self.errors(result))

    def test_invalid_declared_source_duration_is_rejected(self) -> None:
        for value in (None, True, 0, -1, "2", float("inf"), 10 ** 400):
            with self.subTest(value=value):
                self.assertIn("source_duration", self.errors(self.check(self.selection(source_duration_s=value))))

    def test_empty_or_nontext_replay_reason_cannot_bypass_duplicate(self) -> None:
        for value in (None, "", " ", True):
            with self.subTest(value=value):
                result = self.check(self.selection(), self.selection(reuse_reason=value))
                self.assertTrue({"duplicate_selection", "reuse_reason"}.issubset(self.errors(result)))

    def test_reuse_does_not_hide_missing_files_or_unreviewed_state(self) -> None:
        result = self.check(self.selection(
            media_path="missing.stub", state_reviewed=False, reuse_reason="有意回放"))
        self.assertTrue({"missing_evidence", "unreviewed_output"}.issubset(self.errors(result)))

    def test_replay_does_not_bypass_state_continuity(self) -> None:
        unit = {"id": "shot", "start_state": {"prop": {"ready": True}},
                "end_state": {"prop": {"ready": True}},
                "selected": self.selection(source_range_s=[0, 1], reuse_reason="回忆")}
        plan = {"entities": {"prop": {}}, "initial_state": {"prop": {"ready": False}},
                "units": [deepcopy(unit)]}
        result = validate_plan(plan, "execution", self.base)
        self.assertIn("state_reset", self.errors(result))

    def run_cli(self, selections: list[dict], *extra: str) -> subprocess.CompletedProcess[str]:
        plan = {"entities": {"prop": {}}, "initial_state": {},
                "units": [{"id": f"shot-{i}", "selected": item}
                          for i, item in enumerate(selections)]}
        path = self.base / "plan.json"
        path.write_text(json.dumps(plan), encoding="utf-8")
        return subprocess.run(
            [sys.executable, "-B", "-X", "utf8",
             str(Path(__file__).with_name("validate_scene_plan.py")),
             str(path), "--phase", "execution", *extra],
            capture_output=True, text=True, encoding="utf-8", timeout=15,
        )

    def test_cli_accepts_disjoint_selection(self) -> None:
        result = self.run_cli([
            self.selection(source_range_s=[0, 1]),
            self.selection(source_range_s=[1, 2]),
        ])
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(0, json.loads(result.stdout)["errors"])

    def test_cli_reports_bad_range_and_preserves_existing_report(self) -> None:
        selection = self.selection(source_range_s=[2, 1])
        result = self.run_cli([selection])
        self.assertEqual(1, result.returncode, result.stderr)
        self.assertIn("source_range", self.errors(json.loads(result.stdout)))
        report = self.base / "existing-report.json"
        report.write_text("preserve previous evidence", encoding="utf-8")
        result = self.run_cli([selection], "--report", str(report))
        self.assertEqual(2, result.returncode)
        self.assertEqual("preserve previous evidence", report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
