"""Search/export verified assets and render a timed sound-effects-only stem."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
import sys
import tempfile
import wave
from datetime import datetime, timezone
from pathlib import Path

from runtime import add_arguments, settings

ALLOWED_LICENSES = {"CC0-1.0", "LicenseRef-Self-Owned"}


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def json_text(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def contained(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or Path(relative).is_absolute():
        raise ValueError("A library-relative path is required")
    result = (root / relative).resolve()
    if not result.is_relative_to(root.resolve()):
        raise ValueError("Path escapes library")
    return result


def load_catalog(root: Path) -> dict[str, dict]:
    catalog = read_json(root / "catalog.json")
    if catalog.get("schema_version") != 1 or not isinstance(catalog.get("assets"), list):
        raise ValueError("Unsupported catalogue")
    result = {}
    for asset in catalog["assets"]:
        if not isinstance(asset, dict) or not isinstance(asset.get("id"), str):
            raise ValueError("Invalid asset record")
        if asset["id"] in result:
            raise ValueError("Duplicate ID")
        result[asset["id"]] = asset
    return result


def verify_asset(root: Path, asset: dict) -> Path:
    if asset.get("license") not in ALLOWED_LICENSES or asset.get("license_verified") is not True:
        raise ValueError(f"Asset license not admitted: {asset['id']}")
    receipt = read_json(contained(root, asset["source_receipt"]))
    if receipt.get("license") != asset["license"] or receipt.get("license_verified") is not True:
        raise ValueError("Source license not verified")
    if not isinstance(asset.get("license_files"), list) or not asset["license_files"] or asset["license_files"] != receipt.get("license_files"):
        raise ValueError("License evidence binding is missing or changed")
    if receipt["license"] == "LicenseRef-Self-Owned" and (receipt.get("source_kind") != "self_recorded" or receipt.get("rights_confirmed") is not True):
        raise ValueError("Self-owned recording requires an ownership declaration")
    evidence = {item["path"]: item["sha256"] for item in receipt["files"]}
    for relative in asset["license_files"]:
        file = contained(root, relative)
        if digest(file) != evidence.get(relative):
            raise ValueError(f"License evidence changed: {relative}")
    source = contained(root, asset["source_path"])
    if digest(source) != asset["source_sha256"] or evidence.get(asset["source_path"]) != asset["source_sha256"]:
        raise ValueError(f"Original changed: {asset['id']}")
    path = contained(root, asset["path"])
    if digest(path) != asset["sha256"]:
        raise ValueError(f"Editing copy changed: {asset['id']}")
    return path


def output_paths(root: Path, output: Path) -> tuple[Path, Path, Path]:
    output = output.resolve()
    if output.suffix.lower() != ".wav":
        raise ValueError("Output must be a new .wav file")
    for name in ("原始素材", "剪辑素材", "来源与许可", "下载包"):
        if output.is_relative_to((root / name).resolve()):
            raise ValueError("Cannot write into protected library assets")
    request = output.with_suffix(".request.json")
    receipt = output.with_suffix(".receipt.json")
    for path in (output, request, receipt):
        if path.exists():
            raise FileExistsError(f"Choose a new version; already exists: {path}")
    return output, request, receipt


def source_record(root: Path, asset: dict) -> dict:
    return {
        "id": asset["id"], "name": asset["name"], "author": asset["author"],
        "source_url": asset["source_url"], "license": asset["license"],
        "license_url": asset["license_url"], "attribution_required": asset["attribution_required"],
        "source_kind": asset.get("source_kind", "downloaded"),
        "recording_metadata": asset.get("recording_metadata", {}),
        "source_sha256": asset["source_sha256"], "editing_sha256": asset["sha256"],
        "library_path": str(contained(root, asset["path"])),
        "license_texts": {rel: contained(root, rel).read_text(encoding="utf-8-sig")
                          for rel in asset["license_files"]},
        "listening_status": asset["listening_status"],
    }


def finish(output: Path, request: Path, receipt: Path, request_data: dict, sources: list[dict]) -> dict:
    with wave.open(str(output), "rb") as audio:
        info = {"duration_seconds": audio.getnframes() / audio.getframerate(),
                "sample_rate": audio.getframerate(), "channels": audio.getnchannels()}
    result = {
        "created_at": datetime.now(timezone.utc).isoformat(), "output": str(output),
        "sha256": digest(output), **info, "sources": sources,
        "technical_status": "rendered", "listening_status": "unreviewed",
        "scene_fit_status": "unverified", "request_sha256": hashlib.sha256(json_text(request_data).encode()).hexdigest(),
    }
    with request.open("x", encoding="utf-8") as stream:
        stream.write(json_text(request_data))
    with receipt.open("x", encoding="utf-8") as stream:
        stream.write(json_text(result))
    return result


def export_asset(root: Path, asset: dict, output: Path) -> dict:
    source = verify_asset(root, asset)
    output, request, receipt = output_paths(root, output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as src, output.open("xb") as dst:
        shutil.copyfileobj(src, dst)
    return finish(output, request, receipt, {"operation": "export", "asset_id": asset["id"]},
                  [source_record(root, asset)])


def number(value: object, name: str, minimum: float, maximum: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise ValueError(f"{name} must be a number")
    value = float(value)
    if not math.isfinite(value) or not minimum <= value <= maximum:
        raise ValueError(f"{name} must be within [{minimum}, {maximum}]")
    return value


def render(root: Path, catalog: dict[str, dict], plan: dict, output: Path, ffmpeg: Path) -> dict:
    if plan.get("schema_version") != 1:
        raise ValueError("Plan schema_version must be 1")
    length = number(plan.get("duration_seconds"), "duration_seconds", 0.01, 14400)
    events = plan.get("events")
    if not isinstance(events, list) or not 1 <= len(events) <= 200:
        raise ValueError("events must contain 1..200 entries")
    output, request, receipt = output_paths(root, output)
    sources, paths, filters = {}, [], []
    allowed = {"asset_id", "at_seconds", "trim_start_seconds", "duration_seconds", "gain_db",
               "fade_in_seconds", "fade_out_seconds", "note"}
    for index, event in enumerate(events):
        if not isinstance(event, dict) or set(event) - allowed:
            raise ValueError("Unknown event fields; refusing to silently ignore parameters")
        asset_id = event.get("asset_id")
        if not isinstance(asset_id, str) or asset_id not in catalog:
            raise ValueError(f"Unknown asset_id: {asset_id}")
        asset = catalog[asset_id]
        path = verify_asset(root, asset)
        source_duration = asset["duration_seconds"]
        start = number(event.get("at_seconds"), "at_seconds", 0, length)
        trim = number(event.get("trim_start_seconds", 0), "trim_start_seconds", 0, source_duration)
        duration = number(event.get("duration_seconds", source_duration - trim), "event duration", 1 / 48000, source_duration - trim)
        if start + duration > length + 1 / 48000:
            raise ValueError("Event exceeds output duration; extend the plan or explicitly trim the event")
        gain = number(event.get("gain_db", -12), "gain_db", -96, 12)
        fade_in = number(event.get("fade_in_seconds", 0), "fade_in_seconds", 0, duration)
        fade_out = number(event.get("fade_out_seconds", 0), "fade_out_seconds", 0, duration)
        if fade_in + fade_out > duration:
            raise ValueError("Fades overlap")
        paths.append(path)
        sources[asset_id] = source_record(root, asset)
        filters.append(
            f"[{index}:a]atrim=start={trim}:duration={duration},asetpts=PTS-STARTPTS,"
            f"aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,"
            f"volume={gain}dB,afade=t=in:d={fade_in},"
            f"afade=t=out:st={duration - fade_out}:d={fade_out},"
            f"adelay={round(start * 48000)}S:all=1[a{index}]"
        )
    labels = "".join(f"[a{i}]" for i in range(len(events)))
    filters.append(f"{labels}amix=inputs={len(events)}:normalize=0:duration=longest,"
                   f"apad,atrim=duration={length},alimiter=limit=0.891251:level=false:latency=true[out]")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="sfx-render-", dir=output.parent) as directory:
        graph = Path(directory) / "filter.txt"
        graph.write_text(";\n".join(filters), encoding="utf-8")
        temporary = Path(directory) / "stem.wav"
        command = [str(ffmpeg), "-hide_banner", "-loglevel", "error", "-nostdin", "-n"]
        for path in paths:
            command.extend(["-i", str(path)])
        command.extend(["-filter_complex_script", str(graph), "-map", "[out]", "-ar", "48000",
                        "-ac", "2", "-c:a", "pcm_s16le", str(temporary)])
        subprocess.run(command, check=True, timeout=max(120, length * 2), capture_output=True)
        with temporary.open("rb") as src, output.open("xb") as dst:
            shutil.copyfileobj(src, dst)
    request_data = {"operation": "render_sfx_stem", "plan": plan,
                    "ffmpeg": str(ffmpeg), "filter_graph": filters,
                    "limiter": "sample peak -1 dBFS, auto level off, latency compensated; not true-peak mastering"}
    return finish(output, request, receipt, request_data, list(sources.values()))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_arguments(parser)
    sub = parser.add_subparsers(dest="command", required=True)
    search = sub.add_parser("search", help="AND-match Chinese/English terms")
    search.add_argument("query", nargs="?", default="")
    search.add_argument("--limit", type=int, default=20)
    export = sub.add_parser("export")
    export.add_argument("asset_id")
    export.add_argument("--out", type=Path, required=True)
    mix = sub.add_parser("render", help="Render SFX only; does not modify any video")
    mix.add_argument("plan", type=Path)
    mix.add_argument("--out", type=Path, required=True)
    mix.add_argument("--ffmpeg", default=argparse.SUPPRESS)
    sub.add_parser("verify")
    sub.add_parser("doctor")
    sub.add_parser("init", help="Create an empty library; no downloads")
    args = parser.parse_args()
    args.library, ffmpeg = settings(args, require_ffmpeg=args.command in {"render", "doctor"})
    if args.command == "init":
        target = args.library / "catalog.json"
        if target.exists():
            raise FileExistsError("Library already initialized")
        args.library.mkdir(parents=True, exist_ok=True)
        with target.open("x", encoding="utf-8") as stream:
            stream.write(json_text({"schema_version": 1, "count": 0, "assets": []}))
        print(json_text({"initialized": str(args.library), "downloads": 0}))
        return
    catalog = load_catalog(args.library)
    if args.command == "doctor":
        version = subprocess.run([str(ffmpeg), "-version"], capture_output=True, text=True, encoding="utf-8", errors="replace", check=True, timeout=15).stdout.splitlines()[0]
        print(json_text({"library": str(args.library), "asset_count": len(catalog), "ffmpeg": str(ffmpeg), "version": version, "python": sys.version.split()[0], "asset_hashes_checked": False}))
        return
    if args.command == "search":
        if args.limit < 1:
            raise ValueError("limit must be positive")
        terms = args.query.lower().split()
        matches = [asset for asset in catalog.values() if all(term in
                   (asset["name"] + " " + asset["id"] + " " + asset["category"] + " " + " ".join(asset["tags"])).lower()
                   for term in terms)]
        print(json_text({"total": len(matches), "results": [
            {key: item[key] for key in ("id", "name", "category", "tags", "duration_seconds", "path", "license", "listening_status")}
            for item in matches[:args.limit]]}))
    elif args.command == "verify":
        for asset in catalog.values():
            verify_asset(args.library, asset)
        receipts = set(asset["source_receipt"] for asset in catalog.values())
        for relative in receipts:
            record = read_json(contained(args.library, relative))
            for item in record["files"]:
                if digest(contained(args.library, item["path"])) != item["sha256"]:
                    raise ValueError(f"Evidence changed: {item['path']}")
        print(json_text({"verified_assets": len(catalog), "verified_source_packs": len(receipts), "listening_verified": False}))
    elif args.command == "export":
        if args.asset_id not in catalog:
            raise ValueError("Unknown asset ID")
        result = export_asset(args.library, catalog[args.asset_id], args.out)
        print(json_text({"output": result["output"], "sha256": result["sha256"]}))
    else:
        result = render(args.library, catalog, read_json(args.plan), args.out, ffmpeg)
        print(json_text({"output": result["output"], "sha256": result["sha256"], "duration_seconds": result["duration_seconds"]}))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.SubprocessError, wave.Error) as error:
        print(f"SFX failed: {error}", file=sys.stderr)
        if isinstance(error, subprocess.CalledProcessError) and error.stderr:
            print(error.stderr.decode("utf-8", errors="replace")[-2000:], file=sys.stderr)
        sys.exit(1)
