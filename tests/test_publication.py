import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from asteria.pipeline import publish


class PublicationTests(unittest.TestCase):
    def prepare(self, folder):
        (folder / 'analysis').mkdir()
        payload = b'complete dashboard'
        (folder / 'analysis/dashboard.html').write_bytes(payload)
        (folder / 'analysis/pipeline_manifest.json').write_text(json.dumps({
            'status': 'success', 'outputs': {
                'analysis/dashboard.html': hashlib.sha256(payload).hexdigest()}}))

    def test_failed_and_interrupted_runs_preserve_published_release(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = publish(root, self.prepare)
            pointer = root / 'releases/current.json'
            previous = pointer.read_bytes()
            for failure in (RuntimeError, KeyboardInterrupt):
                def broken(folder):
                    self.prepare(folder)
                    (folder / 'analysis/dashboard.html').write_text('partial')
                    raise failure('interrupted after an output was written')
                with self.assertRaises(failure):
                    publish(root, broken)
                self.assertEqual(pointer.read_bytes(), previous)
                self.assertEqual((first / 'analysis/dashboard.html').read_bytes(), b'complete dashboard')

    def test_corrupt_output_cannot_publish(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def corrupt(folder):
                self.prepare(folder)
                (folder / 'analysis/dashboard.html').write_text('corrupt')
            with self.assertRaisesRegex(RuntimeError, 'hash mismatch'):
                publish(root, corrupt)
            self.assertFalse((root / 'releases/current.json').exists())

    def test_pointer_failure_keeps_old_release_and_success_switches(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = publish(root, self.prepare)
            pointer = root / 'releases/current.json'
            previous = pointer.read_bytes()
            with patch('asteria.pipeline.os.replace', side_effect=OSError('locked pointer')):
                with self.assertRaises(OSError):
                    publish(root, self.prepare)
            self.assertEqual(pointer.read_bytes(), previous)
            second = publish(root, self.prepare)
            self.assertNotEqual(first, second)
            self.assertEqual(json.loads(pointer.read_text())['release'], second.name)
            self.assertTrue(first.exists())
