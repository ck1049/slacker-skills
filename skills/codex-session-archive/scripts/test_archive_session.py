"""Behavior checks use disposable logs only; never target real Codex state."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import uuid

import archive_session as archive


class Fixtures(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='codex-archive-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.home = self.root / 'fake-codex'
        self.thread = str(uuid.uuid4())
        self.source = self.home / 'sessions/2026/01/01/session.jsonl'
        self.source.parent.mkdir(parents=True)
        self.prefix = (json.dumps({'type': 'session_meta', 'payload': {'id': self.thread}})
                       + '\n{"message":"图片和工具原始证据"}\n').encode('utf-8')
        self.source.write_bytes(self.prefix)
        self.out = self.root / '归档 with space'
        self.db = self.home / 'shared.sqlite'
        self.db.write_bytes(b'shared database sentinel')
        self.other = self.source.with_name('other.jsonl')
        self.other.write_bytes(b'other chat sentinel')
        self.addCleanup(self.assert_unrelated_intact)

    def assert_unrelated_intact(self):
        self.assertEqual(self.db.read_bytes(), b'shared database sentinel')
        self.assertEqual(self.other.read_bytes(), b'other chat sentinel')

    def snapshot(self, fmt='gzip'):
        return archive.snapshot(self.source, self.out, self.home, self.thread, fmt)

    def seal(self, *, delete=False):
        # Real OS locks/deletion below, but process enumeration is fixture-isolated.
        with patch.object(archive, 'assert_codex_closed'):
            return archive.seal(self.out, delete=delete, confirm=self.thread if delete else None)


class ArchiveChecks(Fixtures):
    def test_snapshot_and_portable_restore(self):
        self.snapshot()
        moved = self.root / 'moved'
        shutil.move(self.out, moved)
        target = self.root / 'restored.jsonl'
        result = archive.restore(moved, target)
        self.assertTrue(result['verified'])
        self.assertEqual(target.read_bytes(), self.prefix)
        self.assertTrue(self.source.exists())

    def test_snapshot_drops_partial_record_only_until_seal(self):
        self.source.write_bytes(self.prefix + b'{"unfinished":')
        data = self.snapshot()
        self.assertEqual(data['plain_bytes'], len(self.prefix))
        if os.name == 'nt':
            self.seal()
            target = self.root / 'complete.jsonl'
            archive.restore(self.out, target)
            self.assertEqual(target.read_bytes(), self.prefix + b'{"unfinished":')

    @unittest.skipIf(archive.zstd is None, 'Existing Zstd unavailable')
    def test_zstd_large_record_roundtrip(self):
        self.prefix += b'{"image":"' + b'abcd0123' * 160000 + b'"}\n'
        self.source.write_bytes(self.prefix)
        self.snapshot('zstd')
        archive.restore(self.out, self.root / 'zstd.jsonl')
        self.assertEqual((self.root / 'zstd.jsonl').read_bytes(), self.prefix)

    def test_no_overwrite_backup(self):
        self.snapshot()
        with self.assertRaises(FileExistsError):
            self.snapshot()

    def test_wrong_identity_no_archive(self):
        with self.assertRaises(ValueError):
            archive.snapshot(self.source, self.out, self.home, str(uuid.uuid4()), 'gzip')
        self.assertFalse(self.out.exists())

    def test_wrong_root_no_archive(self):
        with self.assertRaises(ValueError):
            archive.snapshot(self.db, self.out, self.home, self.thread, 'gzip')
        self.assertFalse(self.out.exists())

    def test_restore_existing_file_retained(self):
        self.snapshot()
        target = self.root / 'existing.jsonl'
        target.write_bytes(b'do not replace')
        with self.assertRaises(FileExistsError):
            archive.restore(self.out, target)
        self.assertEqual(target.read_bytes(), b'do not replace')

    def test_restore_to_codex_state_refused(self):
        self.snapshot()
        with self.assertRaises(ValueError):
            archive.restore(self.out, self.home / 'sessions/new.jsonl')

    def test_corrupt_part_refuses_restore(self):
        data = self.snapshot()
        (self.out / data['parts'][0]['file']).write_bytes(b'corrupt')
        with self.assertRaises(ValueError):
            archive.restore(self.out, self.root / 'bad.jsonl')
        self.assertFalse((self.root / 'bad.jsonl').exists())

    def test_part_directory_escape_refused(self):
        data = self.snapshot()
        data['parts'][0]['file'] = '../other.jsonl'
        with self.assertRaises(ValueError):
            archive.verify_manifest(self.out, data)

    def test_part_order_refused(self):
        data = self.snapshot()
        data['parts'][0]['offset'] = 1
        with self.assertRaises(ValueError):
            archive.verify_manifest(self.out, data)

    def test_confirmation_required(self):
        self.snapshot()
        with self.assertRaises(ValueError):
            archive.seal(self.out, delete=True, confirm=None)
        self.assertTrue(self.source.exists())

    def test_running_app_blocks_non_deleting_seal(self):
        self.snapshot()
        with patch.object(archive, 'assert_codex_closed', side_effect=RuntimeError('fixture busy')):
            with self.assertRaises(RuntimeError):
                archive.seal(self.out, delete=False, confirm=None)
        self.assertTrue(self.source.exists())

    def test_operation_lock_refuses_second_runner(self):
        self.snapshot()
        with archive.operation(self.out):
            with self.assertRaises(FileExistsError):
                with archive.operation(self.out):
                    self.fail('Second operation entered')

    def test_hardlinked_source_refused(self):
        os.link(self.source, self.root / 'linked.jsonl')
        with self.assertRaises(ValueError):
            self.snapshot()


@unittest.skipUnless(os.name == 'nt', 'Real Windows exclusive handle checks')
class WindowsChecks(Fixtures):
    def test_full_tail_delete_and_restore_exact(self):
        self.snapshot()
        tail = b'{"after":"snapshot"}\n'
        with self.source.open('ab') as stream:
            stream.write(tail)
        data = self.seal(delete=True)
        self.assertEqual(data['state'], 'SOURCE_DELETED')
        self.assertFalse(self.source.exists())
        self.assertEqual(len(data['parts']), 2)
        archive.restore(self.out, self.root / 'all.jsonl')
        self.assertEqual((self.root / 'all.jsonl').read_bytes(), self.prefix + tail)
        self.assertEqual(self.seal(delete=True)['state'], 'SOURCE_DELETED')

    def test_changed_prefix_preserves_original(self):
        self.snapshot()
        self.source.write_bytes(self.prefix.replace(b'message', b'changed'))
        with self.assertRaises(ValueError):
            self.seal(delete=True)
        self.assertTrue(self.source.exists())

    def test_corrupt_archive_prevents_deletion(self):
        data = self.snapshot()
        (self.out / data['parts'][0]['file']).write_bytes(b'broken archive')
        with self.assertRaises(ValueError):
            self.seal(delete=True)
        self.assertEqual(self.source.read_bytes(), self.prefix)

    def test_truncation_preserves_original(self):
        self.snapshot()
        self.source.write_bytes(self.prefix.splitlines(keepends=True)[0])
        with self.assertRaises(ValueError):
            self.seal(delete=True)
        self.assertTrue(self.source.exists())

    def test_wrong_thread_in_source_preserves_original(self):
        self.snapshot()
        self.source.write_bytes(self.prefix.replace(self.thread.encode(), str(uuid.uuid4()).encode()))
        with self.assertRaises(ValueError):
            self.seal(delete=True)
        self.assertTrue(self.source.exists())

    def test_replaced_source_same_bytes_preserved(self):
        self.snapshot()
        replacement = self.root / 'replacement'
        replacement.write_bytes(self.prefix)
        os.replace(replacement, self.source)
        with self.assertRaises(ValueError):
            self.seal(delete=True)
        self.assertTrue(self.source.exists())

    def test_occupied_source_refused(self):
        self.snapshot()
        with archive.exclusive_source(self.source):
            with self.assertRaises(OSError):
                self.seal(delete=True)
        self.assertTrue(self.source.exists())

    def test_sealed_append_then_delete_retains_all(self):
        self.snapshot()
        with self.source.open('ab') as out:
            out.write(b'{"tail":1}\n')
        self.seal()
        self.assertTrue(self.source.exists())
        with self.source.open('ab') as out:
            out.write(b'{"tail":2}\n')
        data = self.seal(delete=True)
        self.assertEqual(len(data['parts']), 3)
        archive.restore(self.out, self.root / 'three.jsonl')
        self.assertEqual((self.root / 'three.jsonl').read_bytes(), self.prefix + b'{"tail":1}\n{"tail":2}\n')

    def test_reappeared_source_is_not_deleted(self):
        self.snapshot()
        self.seal(delete=True)
        self.source.write_bytes(self.prefix)
        with self.assertRaises(ValueError):
            self.seal(delete=True)
        self.assertTrue(self.source.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
