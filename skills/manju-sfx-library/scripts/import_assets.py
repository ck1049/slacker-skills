"""Admit a small, explicitly reviewed batch of local audio and rights evidence.

No network. License verification is an accountable human/agent input, not an
inference from a filename. Rendering a catalogue remains a separate operation.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from fetch_kenney import save_new
from runtime import add_arguments, digest, settings
from sfx import contained, read_json

AUDIO_TYPES = {".wav", ".ogg", ".flac", ".mp3"}


def admit(root: Path, manifest: Path) -> dict:
    data = read_json(manifest)
    if data.get("schema_version") != 1 or data.get("license_verified") is not True:
        raise ValueError("A version 1 manifest with reviewed license evidence is required")
    batch = data.get("batch_id")
    if not isinstance(batch, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,63}", batch):
        raise ValueError("batch_id must be a unique lowercase slug, 3..64 characters")
    kind = data.get("source_kind")
    if kind not in {"downloaded", "self_recorded", "procedural"}:
        raise ValueError("Unknown source_kind")
    license_id = data.get("license")
    if license_id not in {"CC0-1.0", "LicenseRef-Self-Owned"}:
        raise ValueError("Only reviewed CC0 or declared self-owned recordings are supported")
    if license_id == "LicenseRef-Self-Owned" and (kind != "self_recorded" or data.get("rights_confirmed") is not True):
        raise ValueError("Self-owned audio requires explicit ownership confirmation")
    for field in ("author", "source_url", "license_url", "verified_by", "verified_at"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            raise ValueError(f"Missing provenance: {field}")
    for field in ("source_url", "license_url"):
        if not data[field].startswith(("https://", "http://", "urn:")):
            raise ValueError(f"Unsupported URL scheme in {field}")
    evidence = data.get("evidence_files")
    assets = data.get("assets")
    if not isinstance(evidence, list) or not evidence or not all(isinstance(x, str) for x in evidence):
        raise ValueError("evidence_files must name local UTF-8 text documents")
    if not isinstance(assets, list) or not 1 <= len(assets) <= 200:
        raise ValueError("assets must contain 1..200 items")
    receipt_path = contained(root, f"来源与许可/imported/{batch}/receipt.json")
    manifest_sha = digest(manifest)
    if receipt_path.exists():
        previous = read_json(receipt_path)
        if previous.get("manifest_sha256") != manifest_sha:
            raise FileExistsError("Batch exists with a different manifest; use a new batch_id")
        for item in previous["files"]:
            if digest(contained(root, item["path"])) != item["sha256"]:
                raise ValueError("Previously imported data changed")
        return {"batch": batch, "status": "already_verified"}
    prepared: list[tuple[Path, bytes]] = []
    license_files = []
    for index, relative in enumerate(evidence):
        source = (manifest.parent / relative).resolve()
        if source.stat().st_size > 4 * 1024 * 1024:
            raise ValueError("Rights evidence exceeds 4 MiB")
        content = source.read_bytes()
        if not content.decode("utf-8-sig").strip():
            raise ValueError("Empty rights evidence")
        target = receipt_path.parent / f"evidence-{index:02d}.txt"
        prepared.append((target, content))
        license_files.append(target.relative_to(root).as_posix())
    metadata = {}
    total_size = 0
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            raise ValueError("Invalid asset entry")
        for field in ("file", "name", "category"):
            if not isinstance(asset.get(field), str) or not asset[field].strip():
                raise ValueError(f"Missing asset {field}")
        if not isinstance(asset.get("tags"), list) or not all(isinstance(x, str) for x in asset["tags"]):
            raise ValueError("tags must be a list of strings")
        recording = asset.get("recording_metadata", {})
        if not isinstance(recording, dict):
            raise ValueError("recording_metadata must be an object")
        if kind == "self_recorded" and not all(isinstance(recording.get(k), str) and recording[k].strip()
                                                for k in ("recorded_by", "recorded_at", "rights_note")):
            raise ValueError("Self-recorded assets need recorded_by, recorded_at and rights_note")
        source = (manifest.parent / asset["file"]).resolve()
        size = source.stat().st_size
        total_size += size
        if source.suffix.lower() not in AUDIO_TYPES or size > 100 * 1024 * 1024 or total_size > 500 * 1024 * 1024:
            raise ValueError("Unsupported audio type or batch exceeds local import size limit")
        content = source.read_bytes()
        target = contained(root, f"原始素材/imported/{batch}/{index:03d}{source.suffix.lower()}")
        prepared.append((target, content))
        metadata[target.relative_to(root).as_posix()] = {
            "name": asset["name"], "category": asset["category"], "tags": asset["tags"],
            "recording_metadata": recording,
        }
    # Validate the whole manifest before creating any admitted receipt.
    for target, content in prepared:
        save_new(target, content)
    manifest_copy = receipt_path.parent / "import-manifest.json"
    save_new(manifest_copy, manifest.read_bytes())
    files = [target for target, _ in prepared] + [manifest_copy]
    record = {
        "schema_version": 1, "source": "local_import", "source_kind": kind,
        "pack": "imported-" + batch, "author": data["author"],
        "source_url": data["source_url"], "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "license": license_id, "license_url": data["license_url"], "license_verified": True,
        "verified_by": data["verified_by"], "verified_at": data["verified_at"],
        "rights_confirmed": data.get("rights_confirmed", False),
        "license_files": license_files, "manifest_sha256": manifest_sha, "asset_metadata": metadata,
        "files": [{"path": p.relative_to(root).as_posix(), "sha256": digest(p), "bytes": p.stat().st_size} for p in files],
    }
    save_new(receipt_path, (json.dumps(record, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    return {"batch": batch, "imported": len(assets), "status": "source_admitted_run_build_catalog_next"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    add_arguments(parser, ffmpeg=False)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    root, _ = settings(args)
    print(json.dumps(admit(root, args.manifest.resolve()), ensure_ascii=False))
