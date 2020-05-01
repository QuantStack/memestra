from unittest import TestCase
import os
import tempfile
import shutil

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
            key = memestra.caching.CacheKey(__file__)
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
            key = memestra.caching.CacheKey(__file__)
            self.assertNotIn(key, cache)
            cache[key] = {}
            data = cache[key]
            self.assertEquals(data['version'], memestra.caching.Format.version)
            self.assertEquals(data['obsolete_functions'], [])
            self.assertEquals(data['generator'], 'manual')
        finally:
            shutil.rmtree(tmpdir)

    def test_invalid_version(self):
        tmpdir = tempfile.mkdtemp()
        try:
            os.environ['XDG_CONFIG_HOME'] = tmpdir
            cache = memestra.caching.Cache()
            key = memestra.caching.CacheKey(__file__)
            with self.assertRaises(ValueError):
                cache[key] = {'version': -1,
                              'obsolete_functions': [],
                              'generator': 'manual'}
        finally:
            shutil.rmtree(tmpdir)
