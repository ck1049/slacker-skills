"""Behavioral checks against actual local assets and FFmpeg; no network."""
from __future__ import annotations

import argparse
import array
import json
import math
import os
import subprocess
import sys
import copy
import shutil
import tempfile
import unittest
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import sfx
import runtime
from build_catalog import build
from import_assets import admit


class SfxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = tempfile.TemporaryDirectory(prefix="sfx-portable-fixture-")
        cls.root = Path(cls.fixture.name) / "independent library"
        incoming = Path(cls.fixture.name) / "incoming"
        incoming.mkdir()
        cls.ffmpeg = Path(os.environ["MANJU_SFX_TEST_FFMPEG"])
        audio_path = incoming / "source.wav"
        with wave.open(str(audio_path), "wb") as audio:
            audio.setparams((2, 2, 48000, 0, "NONE", "not compressed"))
            pcm = array.array("h", [int(8000 * math.sin(2 * math.pi * 440 * n / 48000)) for n in range(12000) for _ in range(2)])
            if sys.byteorder != "little":
                pcm.byteswap()
            audio.writeframes(pcm.tobytes())
        (incoming / "rights.txt").write_text("CC0 synthetic test fixture, generated locally; no third-party audio.", encoding="utf-8")
        manifest = {"schema_version": 1, "batch_id": "synthetic-test-001", "source_kind": "downloaded",
                    "author": "Test fixture", "source_url": "https://example.invalid/test-fixture",
                    "license": "CC0-1.0", "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
                    "license_verified": True, "verified_by": "test", "verified_at": "test-run",
                    "evidence_files": ["rights.txt"], "assets": [{"file": "source.wav", "name": "footstep_wood_000",
                    "category": "脚步", "tags": ["脚步", "木", "synthetic fixture"]}]}
        cls.manifest = incoming / "manifest.json"
        cls.manifest.write_text(json.dumps(manifest), encoding="utf-8")
        admit(cls.root, cls.manifest)
        owned = copy.deepcopy(manifest)
        owned.update({"batch_id": "self-recorded-test-001", "source_kind": "self_recorded",
                      "license": "LicenseRef-Self-Owned", "license_url": "urn:license:self-owned",
                      "rights_confirmed": True})
        owned["assets"][0].update({"name": "owned_test", "recording_metadata": {
            "recorded_by": "Test fixture", "recorded_at": "test-run", "rights_note": "Synthetic fixture for testing ownership metadata only"}})
        cls.owned_manifest = incoming / "owned.json"
        cls.owned_manifest.write_text(json.dumps(owned), encoding="utf-8")
        admit(cls.root, cls.owned_manifest)
        build(cls.root, cls.ffmpeg)
        cls.catalog = sfx.load_catalog(cls.root)
        cls.asset = next(item for item in cls.catalog.values() if item["name"] == "footstep_wood_000")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fixture.cleanup()

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="漫剧音效测试 有空格 ")
        self.folder = Path(self.temporary.name)
        self.output = self.folder / "音效_v001.wav"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def plan(self) -> dict:
        return {"schema_version": 1, "duration_seconds": 2,
                "events": [{"asset_id": self.asset["id"], "at_seconds": 0.5, "gain_db": -12}]}

    def test_export_preserves_bytes_and_license(self) -> None:
        result = sfx.export_asset(self.root, self.asset, self.output)
        self.assertEqual(result["sha256"], self.asset["sha256"])
        self.assertIn("CC0", next(iter(result["sources"][0]["license_texts"].values())))
        self.assertTrue(self.output.with_suffix(".request.json").exists())
        self.assertTrue(self.output.with_suffix(".receipt.json").exists())

    def test_existing_output_preserved(self) -> None:
        self.output.write_bytes(b"keep me")
        with self.assertRaises(FileExistsError):
            sfx.export_asset(self.root, self.asset, self.output)
        self.assertEqual(self.output.read_bytes(), b"keep me")

    def test_render_actual_timing_and_silence(self) -> None:
        result = sfx.render(self.root, self.catalog, self.plan(), self.output, self.ffmpeg)
        self.assertAlmostEqual(result["duration_seconds"], 2, places=4)
        with wave.open(str(self.output), "rb") as audio:
            self.assertEqual((audio.getframerate(), audio.getnchannels()), (48000, 2))
            samples = array.array("h", audio.readframes(audio.getnframes()))
        self.assertEqual(max(abs(x) for x in samples[:int(0.49 * 48000) * 2]), 0)
        self.assertGreater(max(abs(x) for x in samples[int(0.5 * 48000) * 2:int(0.9 * 48000) * 2]), 20)
        self.assertEqual(max(abs(x) for x in samples[48000 * 2:]), 0)
        self.assertLessEqual(max(abs(x) for x in samples), 29205)

    def test_unknown_id_rejected_before_writing(self) -> None:
        plan = self.plan()
        plan["events"][0]["asset_id"] = "MISSING"
        with self.assertRaises(ValueError):
            sfx.render(self.root, self.catalog, plan, self.output, self.ffmpeg)
        self.assertFalse(self.output.exists())

    def test_nonfinite_time_rejected(self) -> None:
        plan = self.plan()
        plan["events"][0]["at_seconds"] = float("nan")
        with self.assertRaises(ValueError):
            sfx.render(self.root, self.catalog, plan, self.output, self.ffmpeg)

    def test_truncated_tail_rejected(self) -> None:
        plan = self.plan()
        plan["events"][0]["at_seconds"] = 1.99
        with self.assertRaises(ValueError):
            sfx.render(self.root, self.catalog, plan, self.output, self.ffmpeg)

    def test_tampered_audio_rejected(self) -> None:
        root = self.folder / "isolated_library"
        paths = [self.asset["source_receipt"], self.asset["source_path"], self.asset["path"], *self.asset["license_files"]]
        for relative in paths:
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.root / relative, target)
        (root / self.asset["path"]).write_bytes(b"corrupt")
        with self.assertRaises(ValueError):
            sfx.verify_asset(root, self.asset)

    def test_non_cc0_rejected(self) -> None:
        asset = copy.deepcopy(self.asset)
        asset["license"] = "CC-BY-NC-4.0"
        with self.assertRaises(ValueError):
            sfx.export_asset(self.root, asset, self.output)

    def test_path_escape_rejected(self) -> None:
        with self.assertRaises(ValueError):
            sfx.contained(self.root, "../outside.wav")

    def test_unknown_parameter_rejected(self) -> None:
        plan = self.plan()
        plan["events"][0]["pan"] = 0.8
        with self.assertRaises(ValueError):
            sfx.render(self.root, self.catalog, plan, self.output, self.ffmpeg)


    def test_relocated_library_and_cli(self) -> None:
        relocated = self.folder / "moved library"
        shutil.copytree(self.root, relocated)
        config = self.folder / "config.local.json"
        config.write_text(json.dumps({"schema_version": 1, "library": "moved library", "ffmpeg": str(self.ffmpeg)}), encoding="utf-8")
        command = [sys.executable, "-X", "utf8", str(Path(sfx.__file__)), "--config", str(config)]
        result = subprocess.run(command + ["search", "脚步 木"], cwd=self.folder, capture_output=True, text=True, encoding="utf-8", check=True)
        self.assertGreater(json.loads(result.stdout)["total"], 0)
        plan_file = self.folder / "plan.json"
        plan_file.write_text(json.dumps(self.plan()), encoding="utf-8")
        subprocess.run(command + ["render", str(plan_file), "--out", str(self.output)], cwd=self.folder, check=True, capture_output=True)
        self.assertTrue(self.output.exists())
        exported = self.folder / "export.wav"
        subprocess.run(command + ["export", self.asset["id"], "--out", str(exported)], cwd=self.folder, check=True, capture_output=True)
        self.assertEqual(sfx.digest(exported), self.asset["sha256"])

    def test_self_owned_keeps_rights_and_metadata(self) -> None:
        asset = next(a for a in self.catalog.values() if a["name"] == "owned_test")
        result = sfx.export_asset(self.root, asset, self.output)
        self.assertEqual(result["sources"][0]["license"], "LicenseRef-Self-Owned")
        self.assertEqual(result["sources"][0]["recording_metadata"]["recorded_by"], "Test fixture")

    def test_import_idempotent(self) -> None:
        self.assertEqual(admit(self.root, self.manifest)["status"], "already_verified")

    def test_unconfirmed_ownership_refused(self) -> None:
        data = sfx.read_json(self.owned_manifest)
        data["rights_confirmed"] = False
        manifest = self.folder / "invalid.json"
        manifest.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(ValueError):
            admit(self.folder / "empty", manifest)
        self.assertFalse((self.folder / "empty").exists())

    def test_bad_config_does_not_fallback(self) -> None:
        args = argparse.Namespace(config=self.folder / "missing.json", library=self.root, ffmpeg=str(self.ffmpeg))
        with self.assertRaises(FileNotFoundError):
            runtime.settings(args)

    def test_cli_library_overrides_config(self) -> None:
        config = self.folder / "config.json"
        config.write_text(json.dumps({"schema_version": 1, "library": "other", "ffmpeg": str(self.ffmpeg)}), encoding="utf-8")
        root, _ = runtime.settings(argparse.Namespace(config=config, library=self.root, ffmpeg=None))
        self.assertEqual(root, self.root.resolve())

    def test_missing_ffmpeg_clear_error(self) -> None:
        with self.assertRaises(FileNotFoundError):
            runtime.settings(argparse.Namespace(config=None, library=self.root, ffmpeg="missing-ffmpeg-abcdef"), require_ffmpeg=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ffmpeg", default=shutil.which("ffmpeg"))
    args, remaining = parser.parse_known_args()
    if not args.ffmpeg:
        parser.error("Provide --ffmpeg; tests do not install dependencies")
    os.environ["MANJU_SFX_TEST_FFMPEG"] = str(Path(args.ffmpeg).resolve())
    unittest.main(argv=[sys.argv[0], *remaining], verbosity=2)
