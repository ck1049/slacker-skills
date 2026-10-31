"""Stream one Codex JSONL into a portable verified archive; Windows-only offline removal."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid
from typing import BinaryIO, Iterator

try:
    from compression import zstd
except ImportError:
    zstd = None

CHUNK = 8 * 1024 * 1024
META_LIMIT = 2 * 1024 * 1024
MANIFEST = 'archive.manifest.json'


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_id(value: str) -> str:
    result = str(uuid.UUID(value))
    if result != value.lower():
        raise ValueError('Thread ID must be a complete UUID')
    return result


def plain_path(path: Path) -> Path:
    """Reject reparse components before resolving; private local paths only."""
    path = Path(os.path.abspath(path))
    for part in (path, *path.parents):
        if part.is_symlink() or (hasattr(part, 'is_junction') and part.is_junction()):
            raise ValueError(f'Symlink/junction excluded: {part}')
        if part.exists() and getattr(part.stat(), 'st_file_attributes', 0) & 0x400:
            raise ValueError(f'Reparse point excluded: {part}')
    return path.resolve()


def home_path(value: str | None) -> Path:
    return plain_path(Path(value or os.environ.get('CODEX_HOME') or Path.home() / '.codex'))


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(CHUNK), b''):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, data: dict) -> None:
    temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.partial')
    with temp.open('x', encoding='utf-8', newline='\n') as out:
        json.dump(data, out, ensure_ascii=False, indent=2)
        out.write('\n')
        out.flush()
        os.fsync(out.fileno())
    os.replace(temp, path)


def read_json(path: Path) -> dict:
    if path.stat().st_size > 16 * 1024 * 1024:
        raise ValueError('Manifest is unexpectedly large')
    value = json.loads(path.read_text(encoding='utf-8-sig'))
    if not isinstance(value, dict):
        raise ValueError('Expected JSON object')
    return value


def identity(stream: BinaryIO, thread: str) -> dict:
    stream.seek(0)
    line = stream.readline(META_LIMIT + 1)
    if len(line) > META_LIMIT or not line.endswith(b'\n'):
        raise ValueError('No bounded complete session_meta first record')
    meta = json.loads(line)
    if meta.get('type') != 'session_meta' or meta.get('payload', {}).get('id') != thread:
        raise ValueError('Session identity mismatch')
    stream.seek(0)
    return meta['payload']


def source_path(source: str, home: Path, thread: str) -> Path:
    path = plain_path(Path(source))
    if path.suffix != '.jsonl' or not any(path.is_relative_to(home / root) for root in ('sessions', 'archived_sessions')):
        raise ValueError('Only one JSONL under the selected Codex sessions roots is supported')
    stat = path.stat()
    if not path.is_file() or stat.st_nlink != 1:
        raise ValueError('Source must be a single-link regular file')
    with path.open('rb') as stream:
        identity(stream, thread)
    return path


def stat_id(stat: os.stat_result) -> list[int]:
    return [stat.st_dev, stat.st_ino]


@contextmanager
def operation(folder: Path) -> Iterator[None]:
    lock = folder / '.archive-operation.lock'
    with lock.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps({'pid': os.getpid(), 'at': now()}))
    try:
        yield
    finally:
        lock.unlink()


def choose_format(request: str) -> str:
    result = ('zstd' if zstd is not None else 'gzip') if request == 'auto' else request
    if result == 'zstd' and zstd is None:
        raise ValueError('Zstd requires existing Python 3.14+ compression.zstd; nothing is installed automatically')
    return result


def open_codec(raw: BinaryIO, fmt: str, mode: str):
    if fmt == 'gzip':
        return gzip.GzipFile(fileobj=raw, mode=mode, compresslevel=1, mtime=0)
    if fmt == 'zstd' and zstd is not None:
        options = None
        if mode == 'wb':
            options = {zstd.CompressionParameter.compression_level: 3,
                       zstd.CompressionParameter.window_log: 27,
                       zstd.CompressionParameter.enable_long_distance_matching: 1,
                       zstd.CompressionParameter.checksum_flag: 1}
        return zstd.ZstdFile(raw, mode=mode, options=options)
    raise ValueError('Unsupported archive format or unavailable Zstd decoder')


def compress_range(stream: BinaryIO, start: int, count: int, folder: Path, fmt: str, stem: str) -> dict:
    name = stem + ('.jsonl.zst' if fmt == 'zstd' else '.jsonl.gz')
    target = folder / name
    temp = target.with_name(target.name + '.partial')
    if target.exists():
        raise FileExistsError(target)
    digest = hashlib.sha256()
    copied = 0
    stream.seek(start)
    with temp.open('xb') as raw:
        with open_codec(raw, fmt, 'wb') as compressed:
            while copied < count:
                block = stream.read(min(CHUNK, count - copied))
                if not block:
                    raise ValueError('Source truncated; original retained')
                compressed.write(block)
                digest.update(block)
                copied += len(block)
        raw.flush()
        os.fsync(raw.fileno())
    # Only task-owned temporary files are renamed; operation lock excludes a second runner.
    temp.rename(target)
    return {'file': name, 'format': fmt, 'offset': start, 'plain_bytes': count,
            'plain_sha256': digest.hexdigest(), 'compressed_bytes': target.stat().st_size,
            'compressed_sha256': sha_file(target)}


def checked_part(folder: Path, part: dict) -> Path:
    name = part['file']
    if not isinstance(name, str) or Path(name).name != name or '/' in name or '\\' in name or name in ('', '.', '..'):
        raise ValueError('Archive parts must be relative basenames')
    path = plain_path(folder / name)
    if path.parent != folder or not path.is_file() or path.stat().st_nlink != 1:
        raise ValueError('Archive part path/link is invalid')
    if path.stat().st_size != part['compressed_bytes'] or sha_file(path) != part['compressed_sha256']:
        raise ValueError('Compressed archive fingerprint mismatch')
    return path


def verify_parts(folder: Path, parts: list[dict], output: BinaryIO | None = None) -> tuple[str, int]:
    combined = hashlib.sha256()
    count = 0
    if not parts:
        raise ValueError('No archive parts')
    for part in parts:
        if part['offset'] != count or type(part['plain_bytes']) is not int or part['plain_bytes'] <= 0:
            raise ValueError('Invalid ordered part offsets/lengths')
        path = checked_part(folder, part)
        digest = hashlib.sha256()
        size = 0
        with path.open('rb') as raw, open_codec(raw, part['format'], 'rb') as stream:
            while block := stream.read(CHUNK):
                size += len(block)
                if size > part['plain_bytes']:
                    raise ValueError('Decompressed part exceeds declared size')
                digest.update(block)
                combined.update(block)
                if output is not None:
                    output.write(block)
        if size != part['plain_bytes'] or digest.hexdigest() != part['plain_sha256']:
            raise ValueError('Decompressed archive fingerprint mismatch')
        count += size
    return combined.hexdigest(), count


def load_manifest(folder: Path) -> dict:
    folder = plain_path(folder)
    data = read_json(folder / MANIFEST)
    if data.get('schema') != 'codex-session-archive/1' or data.get('verified') is not True:
        raise ValueError('Unsupported or unverified manifest')
    canonical_id(data['thread_id'])
    if not isinstance(data.get('parts'), list):
        raise ValueError('Missing ordered parts')
    return data


def verify_manifest(folder: Path, data: dict, output: BinaryIO | None = None) -> None:
    digest, count = verify_parts(folder, data['parts'], output)
    if digest != data['plain_sha256'] or count != data['plain_bytes']:
        raise ValueError('Combined archive bytes/hash mismatch')


def last_newline(stream: BinaryIO, size: int) -> int:
    position = size
    while position:
        start = max(0, position - CHUNK)
        stream.seek(start)
        found = stream.read(position - start).rfind(b'\n')
        if found >= 0:
            return start + found + 1
        position = start
    raise ValueError('No complete JSONL record')


def digest_prefix(stream: BinaryIO, count: int) -> str:
    digest = hashlib.sha256()
    stream.seek(0)
    remaining = count
    while remaining:
        block = stream.read(min(CHUNK, remaining))
        if not block:
            raise ValueError('Short source')
        digest.update(block)
        remaining -= len(block)
    return digest.hexdigest()


def snapshot(source: Path, folder: Path, home: Path, thread: str, fmt: str) -> dict:
    source = source_path(str(source), home, thread)
    folder = plain_path(folder)
    if folder.is_relative_to(home):
        raise ValueError('Archive destination must be outside Codex state')
    if folder.exists() and any(folder.iterdir()):
        raise FileExistsError('Use a new empty archive directory; no overwrite')
    folder.mkdir(parents=True, exist_ok=True)
    (folder / '.gitignore').write_text('*\n!.gitignore\n', encoding='utf-8')
    with operation(folder), source.open('rb') as original:
        meta = identity(original, thread)
        before = os.fstat(original.fileno())
        cutoff = last_newline(original, before.st_size)
        part = compress_range(original, 0, cutoff, folder, fmt, 'snapshot')
        after = os.fstat(original.fileno())
        if stat_id(before) != stat_id(source.stat()) or after.st_size < cutoff:
            raise ValueError('Source replaced/truncated during snapshot')
        if digest_prefix(original, cutoff) != part['plain_sha256']:
            raise ValueError('Source prefix changed during snapshot')
        data = {'schema': 'codex-session-archive/1', 'created_at': now(), 'thread_id': thread,
                'source': str(source), 'codex_home': str(home), 'source_file_id': stat_id(before),
                'source_cwd': meta.get('cwd'), 'source_bytes_at_start': before.st_size,
                'snapshot_complete_record_bytes': cutoff, 'parts': [part], 'plain_bytes': cutoff,
                'plain_sha256': part['plain_sha256'], 'verified': True, 'state': 'SNAPSHOT_VERIFIED',
                'source_deleted': False, 'shared_databases_modified': False, 'project_assets_modified': False,
                'tool_version': 1, 'source_may_append': True}
        verify_manifest(folder, data)
        tool = folder / 'archive_session.py'
        shutil.copyfile(Path(__file__).resolve(), tool)
        data['tool_sha256'] = sha_file(tool)
        write_json(folder / MANIFEST, data)
    return data


def assert_codex_closed() -> None:
    if os.name != 'nt':
        raise RuntimeError('Offline sealing/deletion is implemented and tested only on Windows')
    shell = Path(os.environ.get('SystemRoot', r'C:\Windows')) / 'System32/WindowsPowerShell/v1.0/powershell.exe'
    command = "Get-CimInstance Win32_Process -ErrorAction Stop | Where-Object { $_.Name -ieq 'codex.exe' -or $_.ExecutablePath -like '*OpenAI.Codex_*' } | Select-Object ProcessId,Name | ConvertTo-Json -Compress"
    result = subprocess.run([str(shell), '-NoProfile', '-NonInteractive', '-Command', command],
                            check=True, capture_output=True, text=True, timeout=30,
                            encoding='utf-8', errors='replace')
    if result.stdout.strip() and json.loads(result.stdout):
        raise RuntimeError('Codex is running. Fully exit it first; no process is terminated by this tool')


@contextmanager
def exclusive_source(path: Path) -> Iterator[BinaryIO]:
    if os.name != 'nt':
        raise RuntimeError('Windows exclusive handle required')
    import ctypes
    from ctypes import wintypes
    import msvcrt
    api = ctypes.WinDLL('kernel32', use_last_error=True)
    api.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                               wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    api.CreateFileW.restype = wintypes.HANDLE
    handle = api.CreateFileW(str(path), 0x80000000 | 0x00010000, 0, None, 3, 0x00200000, None)
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        fd = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
    except (OSError, ValueError):
        api.CloseHandle.argtypes = [wintypes.HANDLE]
        api.CloseHandle(handle)
        raise
    with os.fdopen(fd, 'rb') as stream:
        yield stream


def delete_open_handle(stream: BinaryIO) -> None:
    import ctypes
    from ctypes import wintypes
    import msvcrt
    api = ctypes.WinDLL('kernel32', use_last_error=True)
    api.SetFileInformationByHandle.argtypes = [wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD]
    api.SetFileInformationByHandle.restype = wintypes.BOOL
    disposition = wintypes.BOOL(True)
    if not api.SetFileInformationByHandle(msvcrt.get_osfhandle(stream.fileno()), 4,
                                        ctypes.byref(disposition), ctypes.sizeof(disposition)):
        raise ctypes.WinError(ctypes.get_last_error())


def seal(folder: Path, *, delete: bool, confirm: str | None) -> dict:
    folder = plain_path(folder)
    data = load_manifest(folder)
    if delete and (confirm is None or canonical_id(confirm) != data['thread_id']):
        raise ValueError('Deletion requires --delete-source and --confirm-thread matching this archive')
    assert_codex_closed()
    with operation(folder):
        data = load_manifest(folder)
        verify_manifest(folder, data)
        if data.get('source_deleted'):
            if Path(data['source']).exists():
                raise ValueError('Source path has reappeared; never delete a recreated log')
            return data
        home = plain_path(Path(data['codex_home']))
        source = source_path(data['source'], home, data['thread_id'])
        with exclusive_source(source) as original:
            before = os.fstat(original.fileno())
            if stat_id(before) != data['source_file_id'] or before.st_nlink != 1:
                raise ValueError('Source file identity/link changed')
            identity(original, data['thread_id'])
            prefix_size = data['plain_bytes']
            if before.st_size < prefix_size or digest_prefix(original, prefix_size) != data['plain_sha256']:
                raise ValueError('Source prefix changed or source was truncated; retained')
            full_hash = digest_prefix(original, before.st_size)
            if before.st_size > prefix_size:
                tail = compress_range(original, prefix_size, before.st_size - prefix_size, folder,
                                      data['parts'][0]['format'], 'tail-' + uuid.uuid4().hex)
                data['parts'].append(tail)
            data.update(plain_bytes=before.st_size, plain_sha256=full_hash,
                        state='SEALED_VERIFIED', sealed_at=now(), source_may_append=False)
            verify_manifest(folder, data)
            write_json(folder / MANIFEST, data)
            # Final journal is durable before attempting disposition of this exact locked handle.
            if delete:
                assert_codex_closed()
                delete_open_handle(original)
        if delete:
            if source.exists():
                raise RuntimeError('Source remains; verified archive retained')
            data.update(source_deleted=True, deleted_at=now(), state='SOURCE_DELETED')
            write_json(folder / MANIFEST, data)
    return data


def restore(folder: Path, target: Path) -> dict:
    folder = plain_path(folder)
    target = plain_path(target)
    data = load_manifest(folder)
    home = plain_path(Path(data['codex_home']))
    if target.is_relative_to(home) or target == Path(data['source']):
        raise ValueError('Restore only to a NEW file outside Codex state, never the source path')
    if target.exists():
        raise FileExistsError(target)
    if not target.parent.is_dir():
        raise ValueError('Restore parent must already exist')
    if shutil.disk_usage(target.parent).free < data['plain_bytes']:
        raise OSError('Insufficient space for uncompressed restore')
    with operation(folder):
        # Incomplete output is visibly partial. os.link publishes without replacing existing data.
        temp = target.with_name(target.name + '.' + uuid.uuid4().hex + '.partial')
        with temp.open('xb') as out:
            verify_manifest(folder, data, out)
            out.flush()
            os.fsync(out.fileno())
        os.link(temp, target)
        temp.unlink()
    return {'restored_to': str(target), 'plain_bytes': data['plain_bytes'],
            'plain_sha256': data['plain_sha256'], 'verified': True}


def inspect_source(source: Path, home: Path, thread: str) -> dict:
    source = source_path(str(source), home, thread)
    with source.open('rb') as stream:
        meta = identity(stream, thread)
        stat = os.fstat(stream.fileno())
    return {'thread_id': thread, 'source': str(source), 'bytes': stat.st_size,
            'cwd': meta.get('cwd'), 'file_id': stat_id(stat), 'read_only': True}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    for name in ('inspect', 'snapshot'):
        item = subs.add_parser(name)
        item.add_argument('--source', required=True)
        item.add_argument('--thread-id', required=True)
        item.add_argument('--codex-home')
        if name == 'snapshot':
            item.add_argument('--output', required=True)
            item.add_argument('--format', choices=('auto', 'zstd', 'gzip'), default='auto')
    for name in ('verify', 'seal', 'restore'):
        item = subs.add_parser(name)
        item.add_argument('--archive', required=True)
        if name == 'seal':
            item.add_argument('--delete-source', action='store_true')
            item.add_argument('--confirm-thread')
        if name == 'restore':
            item.add_argument('--to', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command in ('inspect', 'snapshot'):
            home = home_path(args.codex_home)
            thread = canonical_id(args.thread_id)
            source = Path(args.source)
            if args.command == 'inspect':
                result = inspect_source(source, home, thread)
            else:
                data = snapshot(source, Path(args.output), home, thread, choose_format(args.format))
                result = {k: data[k] for k in ('thread_id', 'state', 'plain_bytes', 'plain_sha256', 'source_deleted')}
                result.update(archive=str(plain_path(Path(args.output))), compressed_bytes=sum(p['compressed_bytes'] for p in data['parts']))
        else:
            folder = plain_path(Path(args.archive))
            if args.command == 'verify':
                with operation(folder):
                    data = load_manifest(folder)
                    verify_manifest(folder, data)
                result = {'verified': True, 'state': data['state'], 'plain_bytes': data['plain_bytes'], 'plain_sha256': data['plain_sha256'], 'parts': len(data['parts'])}
            elif args.command == 'seal':
                data = seal(folder, delete=args.delete_source, confirm=args.confirm_thread)
                result = {k: data[k] for k in ('thread_id', 'state', 'plain_bytes', 'plain_sha256', 'source_deleted')}
            else:
                result = restore(folder, Path(args.to))
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (OSError, ValueError, RuntimeError, KeyError, TypeError, EOFError, subprocess.SubprocessError) as error:
        print(f'FAILED; no unverified source deletion: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
