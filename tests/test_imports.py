from unittest import TestCase
from textwrap import dedent
from io import StringIO
import memestra

import os
import sys
TESTS_FAKE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'misc', 'test.py'))

class TestImports(TestCase):

    def checkDeprecatedUses(self, code, expected_output):
        sio = StringIO(dedent(code))
        output = memestra.memestra(sio, ('decoratortest', 'deprecated'), None,
                                    file_path=TESTS_FAKE_FILE)
        self.assertEqual(output, expected_output)

    def test_import_from(self):
        code = '''
            from some_module import foo, bar

            def foobar():
                foo()
                bar()

            foo()'''

        self.checkDeprecatedUses(
            code,
            [('foo', '<>', 5, 4, None), ('foo', '<>', 8, 0, None)])

    def test_import_from_as(self):
        code = '''
            from some_module import foo as Foo, bar as Bar

            def foobar():
                Foo()
                Bar()

            Foo()'''

        self.checkDeprecatedUses(
            code,
            [('Foo', '<>', 5, 4, None), ('Foo', '<>', 8, 0, None)])

    def test_import(self):
        code = '''
            import some_module

            def bar():
                some_module.foo()
                some_module.bar()

            some_module.foo()'''

        self.checkDeprecatedUses(
            code,
            [('some_module.foo', '<>', 5, 4, None), ('some_module.foo', '<>', 8, 0, None)])

    def test_import_as(self):
        code = '''
            import some_module as Module

            def bar():
                Module.foo()
                Module.bar()

            Module.foo()'''

        self.checkDeprecatedUses(
            code,
            [('Module.foo', '<>', 5, 4, None), ('Module.foo', '<>', 8, 0, None)])

class TestRecImports(TestCase):

    def checkDeprecatedUses(self, code, expected_output):
        sio = StringIO(dedent(code))
        output = memestra.memestra(sio, ('decoratortest', 'deprecated'), None,
                                   file_path=TESTS_FAKE_FILE, recursive=True)
        self.assertEqual(output, expected_output)

    def test_import(self):
        code = '''
            import some_rec_module

            def foobar():
                some_rec_module.foo()
                some_rec_module.bar()

            some_rec_module.foo()'''

        self.checkDeprecatedUses(
            code,
            [('some_rec_module.foo', '<>', 5, 4, None),
             ('some_rec_module.foo', '<>', 8, 0, None)])

    def test_import_from0(self):
        code = '''
            from some_rec_module import foo

            def foobar():
                foo()

            foo()'''

        self.checkDeprecatedUses(
            code,
            [('foo', '<>', 5, 4, None), ('foo', '<>', 7, 0, None)])

    def test_import_from1(self):
        code = '''
            from some_rec_module import bar

            def foobar():
                bar()

            bar()'''

        self.checkDeprecatedUses(
            code,
            [])
