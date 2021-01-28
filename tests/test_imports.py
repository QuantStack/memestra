from unittest import TestCase, mock
from textwrap import dedent
from io import StringIO
import memestra

import os
import sys

TESTS_PATHS = [os.path.abspath(os.path.join(os.path.dirname(__file__), 'misc'))]

class TestImports(TestCase):

    def checkDeprecatedUses(self, code, expected_output):
        sio = StringIO(dedent(code))
        output = memestra.memestra(sio, ('decoratortest', 'deprecated'), None,
                                   search_paths=TESTS_PATHS)
        self.assertEqual(output, expected_output)

    def test_import_from(self):
        code = '''
            from some_module import foo, bar, foobar
            foobar()

            def foobar():
                foo()
                bar()

            foo()'''

        self.checkDeprecatedUses(
            code,
            [('foo', '<>', 6, 4, None),
             ('foo', '<>', 9, 0, None),
             ('foobar', '<>', 3, 0, "because it's too old")])

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
                                   search_paths=TESTS_PATHS, recursive=True)
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
            [('foo', '<>', 2, 0, None),
             ('foo', '<>', 5, 4, None),
             ('foo', '<>', 7, 0, None)])

    def test_import_from1(self):
        code = '''
            from some_rec_module import bar

            def foobar():
                bar()

            bar()'''

        self.checkDeprecatedUses(
            code,
            [])

    def test_import_from2(self):
        code = '''
            from some_rec_module import foobar

            foobar()'''

        self.checkDeprecatedUses(
            code,
            [('foobar', '<>', 2, 0, None), ('foobar', '<>', 4, 0, None)])

    def test_forwarding_symbol0(self):
        code = '''
            from module_forwarding_symbol import Test
            t = Test()'''

        self.checkDeprecatedUses(
            code,
            [('Test', '<>', 2, 0, None), ('Test', '<>', 3, 4, None)])

    def test_forwarding_symbol1(self):
        code = '''
            import module_forwarding_symbol
            t = module_forwarding_symbol.Test()'''

        self.checkDeprecatedUses(
            code,
            [('module_forwarding_symbol.Test', '<>', 3, 4, None)])

    def test_forwarding_symbol2(self):
        code = '''
            from module_forwarding_symbol import Testosterone
            t = Testosterone()'''

        self.checkDeprecatedUses(
            code,
            [('Testosterone', '<>', 2, 0, None),
             ('Testosterone', '<>', 3, 4, None)])

    def test_forwarding_all_symbols1(self):
        code = '''
            from module_forwarding_all_symbols import Test
            t = Test()'''

        self.checkDeprecatedUses(
            code,
            [('Test', '<>', 2, 0, None),
             ('Test', '<>', 3, 4, None)])

    def test_forwarding_all_symbols2(self):
        code = '''
            from module_forwarding_all_symbols import *
            t = Test()'''

        self.checkDeprecatedUses(
            code,
            [('Test', '<>', 3, 4, None)])

    def test_importing_non_existing_file(self):
        code = '''
            from phantom import void, empty
            void()
            empty()'''

        self.checkDeprecatedUses(
            code,
            [('empty', '<>', 2, 0, None),
             ('empty', '<>', 4, 0, None)])


class TestImportPkg(TestCase):

    def checkDeprecatedUses(self, code, expected_output):
        sio = StringIO(dedent(code))
        output = memestra.memestra(sio, ('decoratortest', 'deprecated'), None,
                                   search_paths=TESTS_PATHS, recursive=True)
        self.assertEqual(output, expected_output)

    def test_import_pkg(self):
        code = '''
            import pkg

            def foobar():
                pkg.test()'''

        self.checkDeprecatedUses(
            code,
            [('pkg.test', '<>', 5, 4, None)])

    def test_import_pkg_level(self):
        code = '''
            from pkg.sub.other import other

            def foobar():
                other()'''

        self.checkDeprecatedUses(
            code,
            [('other', '<>', 2, 0, None), ('other', '<>', 5, 4, None)])

    def test_import_pkg_level_star(self):
        code = '''
            from ipy import foo

            b = foo()'''

        self.checkDeprecatedUses(
            code,
            [('foo', '<>', 2, 0, 'why'), ('foo', '<>', 4, 4, 'why')])

    def test_import_pkg_level_star2(self):
        code = '''
            from ipy import *
            a = useless()
            b = foo()'''

        self.checkDeprecatedUses(
            code,
            [('foo', '<>', 4, 4, 'why')])

    def test_shared_cache(self):
        # We have a fake description for gast in tests/share/memestra
        # Setup the shared cache to use it.
        with mock.patch('sys.prefix', os.path.dirname(__file__)):
            self.checkDeprecatedUses(
                'from gast import parse',
                [('parse', '<>', 1, 0, None)])

    def test_shared_cache_sub(self):
        # We have a fake description for gast in tests/share/memestra
        # Setup the shared cache to use it.
        with mock.patch('sys.prefix', os.path.dirname(__file__)):
            self.checkDeprecatedUses(
                'from gast.astn import AstToGAst',
                [('AstToGAst', '<>', 1, 0, 'because')])
