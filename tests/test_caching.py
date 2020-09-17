from unittest import TestCase, mock
from textwrap import dedent
import os
import sys
import tempfile
import shutil
import contextlib
from io import StringIO

import memestra

class TestCaching(TestCase):

    def test_xdg_config(self):
        tmpdir = tempfile.mkdtemp()
        try:
            os.environ['XDG_CONFIG_HOME'] = tmpdir
            cache = memestra.caching.Cache()
            self.assertTrue(os.path.isdir(os.path.join(tmpdir, 'memestra')))
        finally:
            shutil.rmtree(tmpdir)

    def test_contains(self):
        tmpdir = tempfile.mkdtemp()
        try:
            os.environ['XDG_CONFIG_HOME'] = tmpdir
            cache = memestra.caching.Cache()
            key = memestra.caching.CacheKeyFactory()(__file__)
            self.assertNotIn(key, cache)
            cache[key] = {}
            self.assertIn(key, cache)
        finally:
            shutil.rmtree(tmpdir)

    def test_defaults(self):
        tmpdir = tempfile.mkdtemp()
        try:
            os.environ['XDG_CONFIG_HOME'] = tmpdir
            cache = memestra.caching.Cache()
            key = memestra.caching.CacheKeyFactory()(__file__)
            self.assertNotIn(key, cache)
            cache[key] = {}
            data = cache[key]
            self.assertEqual(data['version'], memestra.caching.Format.version)
            self.assertEqual(data['name'], 'test_caching')
            self.assertEqual(data['deprecated'], [])
            self.assertEqual(data['generator'], 'manual')
        finally:
            shutil.rmtree(tmpdir)

    def test_invalid_version(self):
        tmpdir = tempfile.mkdtemp()
        try:
            os.environ['XDG_CONFIG_HOME'] = tmpdir
            cache = memestra.caching.Cache()
            key = memestra.caching.CacheKeyFactory()(__file__)
            with self.assertRaises(ValueError):
                cache[key] = {'version': -1,
                              'deprecated': [],
                              'generator': 'manual'}
        finally:
            shutil.rmtree(tmpdir)

class TestCLI(TestCase):

    def test_docparse(self):
        fid, tmppy = tempfile.mkstemp(suffix='.py')
        code = '''
            def foo(): "deprecated since 1999"

            foo()'''

        ref = 'Found 1 deprecated identifiers\nfoo\n'
        os.write(fid, dedent(code).encode())
        os.close(fid)
        test_args = ['memestra-cache', 'docparse',
                     '--pattern', 'deprecated since',
                     '--verbose',
                     tmppy]
        with mock.patch.object(sys, 'argv', test_args):
            from memestra.caching import run
            with StringIO() as buf:
                with contextlib.redirect_stdout(buf):
                    run()
                self.assertEqual(buf.getvalue(), ref)
