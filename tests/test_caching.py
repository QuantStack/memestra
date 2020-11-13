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

    def test_cache_dir(self):
        tmpdir = tempfile.mkdtemp()
        cachedir = os.path.join(tmpdir, "memestra-test")
        try:
            cache = memestra.caching.Cache(cache_dir=cachedir)
            self.assertTrue(os.path.isdir(cachedir))
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
    
    def test_set_cache(self):
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as tmppy:
            code = '''
                def foo()
                    pass

                def bar()
                    pass

                foo()
                bar()'''

            tmppy.write(dedent(code).encode())

        ref = ''
        set_args = ['memestra-cache', 'set',
                    '--deprecated', 'foo',
                    '--deprecated', 'bar',
                    tmppy.name]
        with mock.patch.object(sys, 'argv', set_args):
            from memestra.caching import run
            run()

        expected = {
            'deprecated': ['foo', 'bar'],
            'generator': 'manual',
            'name':  os.path.splitext(os.path.basename(tmppy.name))[0],
            'version': 1,
        }
        cache = memestra.caching.Cache()
        key = memestra.caching.CacheKeyFactory()(tmppy.name)
        os.remove(tmppy.name)
        self.assertEqual(cache[key], expected)

    def test_cache_dir(self):
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as tmppy:
            code = '''
                def foo()
                    pass

                foo()'''

            tmppy.write(dedent(code).encode())

        try:
            tmpdir = tempfile.mkdtemp()
            ref = ''
            set_args = ['memestra-cache',
                        '--cache-dir=' + tmpdir,
                        'set',
                        '--deprecated=foo',
                        tmppy.name]
            with mock.patch.object(sys, 'argv', set_args):
                from memestra.caching import run
                run()

            key = memestra.caching.CacheKeyFactory()(tmppy.name)
            cachefile = os.path.join(tmpdir, key.module_hash)
            self.assertTrue(os.path.isfile(cachefile))
        finally:
            os.remove(tmppy.name)
            shutil.rmtree(tmpdir)

