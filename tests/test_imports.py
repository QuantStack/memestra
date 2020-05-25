from unittest import TestCase
from textwrap import dedent
from io import StringIO
import memestra

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'misc'))

class TestImports(TestCase):

    def checkDeprecatedUses(self, code, expected_output):
        sio = StringIO(dedent(code))
        output = memestra.memestra(sio, ('decoratortest', 'deprecated'))
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
            [('foo', '<>', 5, 4), ('foo', '<>', 8, 0)])

    def test_import_from_as(self):
        code = '''
            from some_module import foo as Foo, bar as Bar

            def foobar():
                Foo()
                Bar()

            Foo()'''

        self.checkDeprecatedUses(
            code,
            [('Foo', '<>', 5, 4), ('Foo', '<>', 8, 0)])

    def test_import(self):
        code = '''
            import some_module

            def bar():
                some_module.foo()
                some_module.bar()

            some_module.foo()'''

        self.checkDeprecatedUses(
            code,
            [('some_module.foo', '<>', 5, 4), ('some_module.foo', '<>', 8, 0)])

    def test_import_as(self):
        code = '''
            import some_module as Module

            def bar():
                Module.foo()
                Module.bar()

            Module.foo()'''

        self.checkDeprecatedUses(
            code,
            [('Module.foo', '<>', 5, 4), ('Module.foo', '<>', 8, 0)])
