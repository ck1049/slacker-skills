"""Download explicitly selected, public Kenney CC0 packs; preserve evidence.

No login, model download, paid service, or automatic catalogue-wide crawl.
"""
from __future__ import annotations

import argparse
import hashlib
import http.cookiejar
import json
import re
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

from runtime import add_arguments, settings
PACKS = {"impact-sounds", "rpg-audio", "interface-sounds", "digital-audio"}
LIMIT = 100 * 1024 * 1024
OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def fetch(url: str, maximum: int = LIMIT, referer: str | None = None) -> tuple[bytes, str]:
    if not url.startswith("https://"):
        raise ValueError("HTTPS required")
    headers = {"User-Agent": "ManjuSfxLibrary/1.0"}
    if referer:
        headers["Referer"] = referer
    request = urllib.request.Request(url, headers=headers)
    with OPENER.open(request, timeout=60) as response:
        if not response.url.startswith("https://"):
            raise ValueError("Non-HTTPS redirect")
        content = response.read(maximum + 1)
        if len(content) > maximum:
            raise ValueError("Download exceeds size limit")
        return content, response.url


def save_new(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f"Existing content differs: {path}")
        return
    with path.open("xb") as stream:
        stream.write(data)


def acquire(root: Path, slug: str) -> None:
    folder = root / "来源与许可" / "kenney" / slug
    receipt = folder / "receipt.json"
    if receipt.exists():
        record = json.loads(receipt.read_text(encoding="utf-8"))
        for item in record["files"]:
            path = (root / item["path"]).resolve()
            if not path.is_relative_to(root.resolve()) or digest(path) != item["sha256"]:
                raise ValueError(f"Stored evidence/file changed: {path}")
        print(json.dumps({"pack": slug, "status": "already_verified"}))
        return
    page_url = f"https://kenney.nl/assets/{slug}"
    snapshot = folder / "source.html"
    if snapshot.exists():
        page = snapshot.read_bytes()
        fetch(page_url, 4 * 1024 * 1024)  # Establish the public download session.
    else:
        page, _ = fetch(page_url, 4 * 1024 * 1024)
        save_new(snapshot, page)
    text = page.decode("utf-8")
    if "creativecommons.org/publicdomain/zero/1.0" not in text:
        raise ValueError(f"No CC0 link on official page: {slug}")
    archive = root / "下载包" / f"kenney_{slug}.zip"
    if not archive.exists():
        found = re.search(r"data-download-id=['\"]([^'\"]+)['\"]", text)
        if not found:
            raise ValueError("No public download link identifier")
        link_data, _ = fetch("https://kenney.nl/download-link/" + found.group(1), 65536, page_url)
        download_url = json.loads(link_data)["url"]
        payload, _ = fetch(download_url, referer=page_url)
        save_new(archive, payload)
    files = [snapshot, archive]
    licenses: list[str] = []
    with zipfile.ZipFile(archive) as bundle:
        if sum(item.file_size for item in bundle.infolist()) > 500 * 1024 * 1024:
            raise ValueError("Unpacked archive exceeds limit")
        for item in bundle.infolist():
            name = PurePosixPath(item.filename.replace("\\", "/"))
            if name.is_absolute() or ".." in name.parts or ":" in item.filename:
                raise ValueError("Unsafe archive path")
            if item.is_dir():
                continue
            is_license = "license" in name.name.lower() and name.suffix.lower() == ".txt"
            is_audio = name.suffix.lower() in {".ogg", ".wav", ".mp3", ".flac"}
            if not (is_license or is_audio):
                continue
            if is_license:
                content = bundle.read(item)
                if not re.search(rb"CC0|Creative Commons Zero", content, re.I):
                    raise ValueError("Bundle license does not confirm CC0")
                target = folder / name.name
                licenses.append(target.relative_to(root).as_posix())
            else:
                target = root / "原始素材" / "kenney" / slug / Path(*name.parts)
                content = bundle.read(item)
            save_new(target, content)
            files.append(target)
    if not licenses:
        raise ValueError("Missing bundle CC0 license: not admitted to catalogue")
    record = {
        "schema_version": 1, "source": "Kenney", "author": "Kenney",
        "pack": slug, "source_url": page_url,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "download_method": "Official page Continue without donating / download-link endpoint",
        "license": "CC0-1.0", "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
        "license_files": licenses, "license_verified": True,
        "files": [{"path": p.relative_to(root).as_posix(), "sha256": digest(p),
                   "bytes": p.stat().st_size} for p in files],
    }
    save_new(receipt, (json.dumps(record, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({"pack": slug, "files": len(files), "download_bytes": archive.stat().st_size}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    add_arguments(parser, ffmpeg=False)
    parser.add_argument("packs", nargs="+", choices=sorted(PACKS))
    args = parser.parse_args()
    root, _ = settings(args)
    for pack in args.packs:
        acquire(root, pack)
