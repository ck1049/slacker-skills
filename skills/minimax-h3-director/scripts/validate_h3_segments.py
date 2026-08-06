#!/usr/bin/env python3
"""Validate multi-unit MiniMax H3 prompt documents."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


UNIT_HEADING = re.compile(r"^## H3 Generation Unit (\d+)\s*$", re.MULTILINE)
TOTAL_DURATION = re.compile(
    r"(?:Target total duration|目标总时长|目标)[^\n]{0,40}?"
    r"(\d+(?:\.\d+)?)\s*(?:seconds?|秒)",
    re.IGNORECASE,
)
REQUEST_DURATION = re.compile(
    r"^- Request duration:\s*(\d+(?:\.\d+)?)\s*$", re.MULTILINE
)
MODE = re.compile(
    r"^- Mode:\s*(T2VA|I2VA|FL2VA|L2VA|Ref2VA)\s*$",
    re.MULTILINE | re.IGNORECASE,
)
INPUT_ASSETS = re.compile(
    r"^- Input assets:\s*(\d+) images?,\s*(\d+) videos?,\s*"
    r"(\d+) audio(?: clips?)?,\s*(\d+) total\s*$",
    re.MULTILINE | re.IGNORECASE,
)
CUT_TIME = re.compile(r"\bAt\s+(\d{2}):(\d{2}\.\d{3})\b")
COPY_READY_BLOCK = re.compile(
    r"^### Copy-ready prompt[^\n]*\n+```text\s*\n(.*?)\n```\s*$",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)
MANIFEST_LINE = re.compile(
    r"^-\s*(<(Picture|Video|Audio)\s+(\d+)>)\s*\|\s*"
    r"([A-Z0-9][A-Z0-9_-]*)\s*\|\s*(.+?)\s*\|\s*"
    r"(image|video|audio)\s*\|\s*(.+?)\s*$",
    re.MULTILINE | re.IGNORECASE,
)
MEDIA_LABEL = re.compile(r"<(Picture|Video|Audio)\s+(\d+)>", re.IGNORECASE)
PATH_LEAK = re.compile(
    r"(?:[A-Za-z]:[\\/]|\\\\|(?:^|[\s\"'])[^\s\"']+\."
    r"(?:png|jpe?g|webp|gif|bmp|mp4|mov|webm|mkv|avi|mp3|wav|flac|aac|m4a)\b)",
    re.MULTILINE | re.IGNORECASE,
)
PLATFORM_LEAK = re.compile(
    r"\b(?:ComfyUI|MiniMax\s+Hub|LibTV)\b|\b(?:upload|attach)\s+(?:the\s+)?(?:file|asset)\b|\bthe\s+file\s+at\b",
    re.IGNORECASE,
)

EXTENSION_TYPES = {
    "image": {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"},
    "video": {".mp4", ".mov", ".webm", ".mkv", ".avi"},
    "audio": {".mp3", ".wav", ".flac", ".aac", ".m4a"},
}

BASE_FIELDS = (
    "integrated_multimodal_description:",
    "overall_soundscape:",
    "non_diegetic_music:",
)
REF_FIELDS = (
    "subject_definitions:",
    "summary:",
    "retention_analysis:",
    "detailed_description:",
    "overall_soundscape:",
    "non_diegetic_music:",
)


@dataclass
class Unit:
    number: int
    body: str


@dataclass
class ManifestEntry:
    label: str
    category: str
    number: int
    asset_id: str
    path: str
    asset_type: str


def parse_units(text: str) -> list[Unit]:
    matches = list(UNIT_HEADING.finditer(text))
    units: list[Unit] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        units.append(Unit(int(match.group(1)), text[match.end() : end]))
    return units


def timestamp_seconds(match: re.Match[str]) -> float:
    return int(match.group(1)) * 60 + float(match.group(2))


def validate_field_order(body: str, fields: tuple[str, ...]) -> list[str]:
    errors: list[str] = []
    positions: list[int] = []
    for field in fields:
        count = body.count(field)
        if count != 1:
            errors.append(f"field `{field}` occurs {count} times; expected exactly once")
        positions.append(body.find(field))
    present_positions = [position for position in positions if position >= 0]
    if len(present_positions) == len(fields) and present_positions != sorted(present_positions):
        errors.append("required fields are not in official order")
    return errors


def normalize_label(category: str, number: int) -> str:
    return f"<{category.title()} {number}>"


def parse_manifest(body: str) -> list[ManifestEntry]:
    entries: list[ManifestEntry] = []
    for match in MANIFEST_LINE.finditer(body):
        category = match.group(2).title()
        number = int(match.group(3))
        entries.append(
            ManifestEntry(
                label=normalize_label(category, number),
                category=category,
                number=number,
                asset_id=match.group(4),
                path=match.group(5).strip(),
                asset_type=match.group(6).lower(),
            )
        )
    return entries


def extract_copy_ready_prompt(body: str) -> tuple[str | None, list[str]]:
    matches = list(COPY_READY_BLOCK.finditer(body))
    if len(matches) != 1:
        return None, [
            f"copy-ready prompt block occurs {len(matches)} times; expected exactly one canonical block"
        ]
    return matches[0].group(1), []


def validate_manifest(
    body: str,
    prompt: str,
    mode: str | None,
    expected_counts: tuple[int, int, int, int] | None,
    asset_root: Path,
    check_asset_existence: bool,
) -> list[str]:
    errors: list[str] = []
    entries = parse_manifest(body)
    manifest_labels = [entry.label for entry in entries]
    prompt_labels = {
        normalize_label(match.group(1), int(match.group(2)))
        for match in MEDIA_LABEL.finditer(prompt)
    }

    if mode == "T2VA" and entries:
        errors.append("T2VA unit must not contain a media binding manifest")
    if mode in {"I2VA", "FL2VA", "L2VA", "REF2VA"} and not entries:
        errors.append("media-input unit is missing reference asset binding manifest entries")

    if len(manifest_labels) != len(set(manifest_labels)):
        errors.append("manifest contains duplicate media labels")
    asset_ids = [entry.asset_id for entry in entries]
    if len(asset_ids) != len(set(asset_ids)):
        errors.append("manifest contains duplicate project asset IDs")
    normalized_paths = [entry.path.casefold() for entry in entries]
    if len(normalized_paths) != len(set(normalized_paths)):
        errors.append("one file path is bound to multiple upload labels")

    for category in ("Picture", "Video", "Audio"):
        numbers = sorted(entry.number for entry in entries if entry.category == category)
        if numbers and numbers != list(range(1, len(numbers) + 1)):
            errors.append(
                f"{category} labels are numbered {numbers}; expected consecutive numbering from 1"
            )

    for entry in entries:
        expected_type = {
            "Picture": "image",
            "Video": "video",
            "Audio": "audio",
        }[entry.category]
        if entry.asset_type != expected_type:
            errors.append(
                f"{entry.label} declares type `{entry.asset_type}`; expected `{expected_type}`"
            )
        suffix = Path(entry.path).suffix.lower()
        if suffix and suffix not in EXTENSION_TYPES[entry.asset_type]:
            errors.append(
                f"{entry.label} path extension `{suffix}` is incompatible with `{entry.asset_type}`"
            )
        if check_asset_existence:
            written_path = Path(entry.path)
            resolved_path = written_path if written_path.is_absolute() else asset_root / written_path
            try:
                resolved_path = resolved_path.resolve(strict=True)
            except (OSError, RuntimeError):
                errors.append(f"{entry.label} references a missing asset: `{entry.path}`")
            else:
                if not resolved_path.is_file():
                    errors.append(f"{entry.label} does not resolve to a regular file: `{entry.path}`")

    missing = sorted(prompt_labels - set(manifest_labels))
    unused = sorted(set(manifest_labels) - prompt_labels)
    if missing:
        errors.append(f"prompt labels missing from manifest: {', '.join(missing)}")
    if unused:
        errors.append(f"manifest labels unused by prompt: {', '.join(unused)}")

    if expected_counts is not None:
        expected_images, expected_videos, expected_audio, expected_total = expected_counts
        actual_images = sum(entry.category == "Picture" for entry in entries)
        actual_videos = sum(entry.category == "Video" for entry in entries)
        actual_audio = sum(entry.category == "Audio" for entry in entries)
        actual_total = len(entries)
        actual = (actual_images, actual_videos, actual_audio, actual_total)
        expected = (expected_images, expected_videos, expected_audio, expected_total)
        if actual != expected:
            errors.append(f"manifest counts {actual} do not match `Input assets` counts {expected}")

    for entry in entries:
        if entry.asset_id in prompt:
            errors.append(f"project asset ID `{entry.asset_id}` leaks into copy-ready prompt")
    if PATH_LEAK.search(prompt):
        errors.append("filename, file extension, or local path leaks into copy-ready prompt")
    if PLATFORM_LEAK.search(prompt):
        errors.append("platform or upload instruction leaks into copy-ready prompt")

    return errors


def validate_unit(unit: Unit, asset_root: Path, check_asset_existence: bool) -> list[str]:
    errors: list[str] = []
    duration_match = REQUEST_DURATION.search(unit.body)
    mode_match = MODE.search(unit.body)

    if not duration_match:
        errors.append("missing `- Request duration: N`")
        duration = None
    else:
        duration = float(duration_match.group(1))
        if duration < 4 or duration > 15:
            errors.append(f"request duration {duration:g}s is outside the official 4–15s range")

    if not mode_match:
        errors.append("missing or invalid `- Mode:`")
        mode = None
    else:
        mode = mode_match.group(1).upper()

    prompt, prompt_errors = extract_copy_ready_prompt(unit.body)
    errors.extend(prompt_errors)
    prompt_for_checks = prompt if prompt is not None else ""
    expected_counts = None

    if mode == "REF2VA":
        errors.extend(validate_field_order(prompt_for_checks, REF_FIELDS))
        assets_match = INPUT_ASSETS.search(unit.body)
        if not assets_match:
            errors.append(
                "Ref2VA unit is missing canonical `- Input assets: X images, Y videos, Z audio, N total`"
            )
        else:
            images, videos, audio, total = map(int, assets_match.groups())
            expected_counts = (images, videos, audio, total)
            if images > 9:
                errors.append(f"image count {images} exceeds 9")
            if videos > 3:
                errors.append(f"video count {videos} exceeds 3")
            if audio > 3:
                errors.append(f"audio count {audio} exceeds 3")
            if total != images + videos + audio:
                errors.append(
                    f"asset total {total} does not equal {images + videos + audio}"
                )
            if total > 12:
                errors.append(f"mixed asset count {total} exceeds 12")
            if audio > 0 and images + videos == 0:
                errors.append("audio cannot be the sole Ref2VA input modality")
    elif mode:
        errors.extend(validate_field_order(prompt_for_checks, BASE_FIELDS))
        assets_match = INPUT_ASSETS.search(unit.body)
        if assets_match:
            expected_counts = tuple(map(int, assets_match.groups()))

    if prompt is not None:
        errors.extend(
            validate_manifest(
                unit.body,
                prompt,
                mode,
                expected_counts,
                asset_root,
                check_asset_existence,
            )
        )

    cut_times = [timestamp_seconds(match) for match in CUT_TIME.finditer(prompt_for_checks)]
    if cut_times != sorted(cut_times) or len(cut_times) != len(set(cut_times)):
        errors.append("cut timestamps are not strictly increasing")
    if duration is not None:
        for cut_time in cut_times:
            if cut_time >= duration:
                errors.append(
                    f"cut timestamp {cut_time:.3f}s reaches or exceeds request duration {duration:g}s"
                )

    return errors


def validate_document(
    text: str, asset_root: Path, check_asset_existence: bool = True
) -> list[str]:
    errors: list[str] = []
    units = parse_units(text)
    total_match = TOTAL_DURATION.search(text)
    total_duration = float(total_match.group(1)) if total_match else None

    if total_duration is not None and total_duration > 15 and len(units) < 2:
        errors.append(
            f"target runtime is {total_duration:g}s but the document contains {len(units)} canonical H3 generation unit(s)"
        )

    if not units:
        if any(marker in text for marker in REF_FIELDS + BASE_FIELDS):
            errors.append(
                "prompt fields exist outside canonical `## H3 Generation Unit NN` sections"
            )
        return errors

    expected_numbers = list(range(1, len(units) + 1))
    actual_numbers = [unit.number for unit in units]
    if actual_numbers != expected_numbers:
        errors.append(
            f"generation unit numbers are {actual_numbers}; expected {expected_numbers}"
        )

    for unit in units:
        for message in validate_unit(unit, asset_root, check_asset_existence):
            errors.append(f"Unit {unit.number:02d}: {message}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", type=Path, help="Markdown prompt document to validate")
    parser.add_argument(
        "--asset-root",
        type=Path,
        help="base directory for relative manifest paths (defaults to the document directory)",
    )
    parser.add_argument(
        "--skip-asset-existence",
        action="store_true",
        help="skip filesystem existence checks for synthetic test fixtures only",
    )
    args = parser.parse_args()

    try:
        text = args.document.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"ERROR: cannot read {args.document}: {exc}", file=sys.stderr)
        return 2

    asset_root = (args.asset_root or args.document.parent).resolve()
    errors = validate_document(text, asset_root, not args.skip_asset_existence)
    if errors:
        print(f"FAIL: {args.document}")
        for error in errors:
            print(f"- {error}")
        return 1

    units = parse_units(text)
    print(f"PASS: {args.document} ({len(units)} generation unit(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
