from unittest import TestCase
from textwrap import dedent
from io import StringIO
import memestra

class TestBasic(TestCase):

    def checkDeprecatedUses(self, code, expected_output):
        sio = StringIO(dedent(code))
        output = memestra.memestra(sio, ('decoratortest', 'deprecated'))
        self.assertEqual(output, expected_output)


    def test_import(self):
        code = '''
            import decoratortest

            @decoratortest.deprecated
            def foo(): pass

            def bar():
                foo()

            foo()'''

        self.checkDeprecatedUses(
            code,
            [('foo', '<>', 8, 4), ('foo', '<>', 10, 0)])

    def test_import_alias(self):
        code = '''
            import decoratortest as dec

            @dec.deprecated
            def foo(): pass

            def bar():
                foo()

            foo()'''

        self.checkDeprecatedUses(
            code,
            [('foo', '<>', 8, 4), ('foo', '<>', 10, 0)])

    def test_import_from(self):
        code = '''
            from decoratortest import deprecated

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
            from decoratortest import deprecated as dp

            @dp
            def foo(): pass

            def bar():
                foo()

            foo()'''

        self.checkDeprecatedUses(
            code,
            [('foo', '<>', 8, 4), ('foo', '<>', 10, 0)])

    def test_call_from_deprecated(self):
        code = '''
            from decoratortest import deprecated as dp

            @dp
            def foo(): pass

            @dp
            def bar():
                foo()

            foo()'''

        self.checkDeprecatedUses(
            code,
            [('foo', '<>', 11, 0),])


class TestClassBasic(TestCase):

    def checkDeprecatedUses(self, code, expected_output):
        sio = StringIO(dedent(code))
        output = memestra.memestra(sio, ('decoratortest', 'deprecated'))
        self.assertEqual(output, expected_output)


    def test_import(self):
        code = '''
            import decoratortest

            @decoratortest.deprecated
            class foo: pass

            def bar():
                foo()

            foo()'''

        self.checkDeprecatedUses(
            code,
            [('foo', '<>', 8, 4), ('foo', '<>', 10, 0)])

    def test_import_alias(self):
        code = '''
            import decoratortest as dec

            @dec.deprecated
            class foo: pass

            def bar():
                foo()

            foo()'''

        self.checkDeprecatedUses(
            code,
            [('foo', '<>', 8, 4), ('foo', '<>', 10, 0)])

    def test_import_from(self):
        code = '''
            from decoratortest import deprecated

            @deprecated
            class foo: pass

            def bar():
                foo()

            foo()'''

        self.checkDeprecatedUses(
            code,
            [('foo', '<>', 8, 4), ('foo', '<>', 10, 0)])

    def test_import_from_alias(self):
        code = '''
            from decoratortest import deprecated as dp

            @dp
            class foo(object): pass

            def bar():
                foo()

            foo()'''

        self.checkDeprecatedUses(
            code,
            [('foo', '<>', 8, 4), ('foo', '<>', 10, 0)])

    def test_instance_from_deprecated(self):
        code = '''
            from decoratortest import deprecated as dp

            @dp
            class foo(object): pass

            @dp
            def bar():
                foo()

            foo()'''

        self.checkDeprecatedUses(
            code,
            [('foo', '<>', 11, 0),])

    def test_use_in_inheritance(self):
        code = '''
            from decoratortest import deprecated as dp

            @dp
            class foo(object): pass

            class bar(foo): pass
            '''

        self.checkDeprecatedUses(
            code,
            [('foo', '<>', 7, 10)])

    def test_instance_from_deprecated_class(self):
        code = '''
            from decoratortest import deprecated as dp

            @dp
            class foo(object): pass

            @dp
            class bar(object):
                foo()

            foo()'''

        self.checkDeprecatedUses(
            code,
            [('foo', '<>', 11, 0),])
