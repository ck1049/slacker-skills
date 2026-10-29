"""Portable local configuration; never downloads or installs dependencies."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def add_arguments(parser: argparse.ArgumentParser, ffmpeg: bool = True) -> None:
    parser.add_argument("--config", type=Path, help="Local JSON config; relative values resolve beside it")
    parser.add_argument("--library", type=Path, help="Independent audio library directory")
    if ffmpeg:
        parser.add_argument("--ffmpeg", help="FFmpeg executable path or PATH command")


def settings(args: argparse.Namespace, require_ffmpeg: bool = False) -> tuple[Path, Path | None]:
    explicit_config = getattr(args, "config", None) or os.environ.get("MANJU_SFX_CONFIG")
    config = Path(explicit_config).expanduser() if explicit_config else Path.home() / ".config/manju-sfx-library/config.json"
    config = config.resolve()
    data = {}
    if config.exists():
        data = json.loads(config.read_text(encoding="utf-8-sig"))
        if not isinstance(data, dict) or set(data) - {"schema_version", "library", "ffmpeg"}:
            raise ValueError("Invalid local config fields")
        if data.get("schema_version") != 1:
            raise ValueError("Config schema_version must be 1")
    elif explicit_config:
        raise FileNotFoundError(f"Config not found: {config}")
    for key in ("library", "ffmpeg"):
        if key in data and (not isinstance(data[key], str) or not data[key].strip()):
            raise ValueError(f"Config {key} must be a nonempty string")
    library = getattr(args, "library", None) or os.environ.get("MANJU_SFX_LIBRARY")
    if library:
        root = Path(library).expanduser().resolve()
    elif data.get("library"):
        root = (config.parent / Path(data["library"]).expanduser()).resolve()
    else:
        raise ValueError("Set --library, MANJU_SFX_LIBRARY, or a local config; no library is bundled")
    executable = getattr(args, "ffmpeg", None) or os.environ.get("MANJU_SFX_FFMPEG")
    if not executable and data.get("ffmpeg"):
        configured = Path(data["ffmpeg"]).expanduser()
        executable = str((config.parent / configured).resolve()) if len(configured.parts) > 1 or configured.is_absolute() else str(configured)
    executable = str(executable or "ffmpeg")
    found = shutil.which(executable)
    ffmpeg_path = Path(found).resolve() if found else None
    if require_ffmpeg and ffmpeg_path is None:
        raise FileNotFoundError("FFmpeg missing; configure --ffmpeg or MANJU_SFX_FFMPEG; nothing installed automatically")
    return root, ffmpeg_path
