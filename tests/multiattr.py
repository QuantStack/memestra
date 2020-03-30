from unittest import TestCase
from textwrap import dedent
from io import StringIO
import memestra

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'misc'))

class TestMultiAttr(TestCase):

    def checkDeprecatedUses(self, code, expected_output):
        sio = StringIO(dedent(code))
        output = memestra.memestra(sio, ('decorator', 'sub', 'deprecated'))
        self.assertEqual(output, expected_output)

    def test_import(self):
        code = '''
            import decorator

            @decorator.sub.deprecated
            def foo(): pass

            def bar():
                foo()

            foo()'''

        self.checkDeprecatedUses(
            code,
            [('foo', '<>', 8, 4), ('foo', '<>', 10, 0)])

    def test_import_alias(self):
        code = '''
            import decorator as dp

            @dp.sub.deprecated
            def foo(): pass

            def bar():
                foo()

            foo()'''

        self.checkDeprecatedUses(
            code,
            [('foo', '<>', 8, 4), ('foo', '<>', 10, 0)])

    def test_import_sub_alias(self):
        code = '''
            import decorator.sub as dp

            @dp.deprecated
            def foo(): pass

            def bar():
                foo()

            foo()'''

        self.checkDeprecatedUses(
            code,
            [('foo', '<>', 8, 4), ('foo', '<>', 10, 0)])

    def test_import_from(self):
        code = '''
            from decorator.sub import deprecated

            @deprecated
            def foo(): pass

            def bar():
                foo()

            foo()'''

        self.checkDeprecatedUses(
            code,
            [('foo', '<>', 8, 4), ('foo', '<>', 10, 0)])

    def test_import_from_alias(self):
        code = '''
            from decorator.sub import deprecated as dp

            @dp
            def foo(): pass

            def bar():
                foo()

            foo()'''

        self.checkDeprecatedUses(
            code,
            [('foo', '<>', 8, 4), ('foo', '<>', 10, 0)])
