from unittest import TestCase, mock
from textwrap import dedent
import tempfile
import contextlib
from io import StringIO

import memestra

import os
import sys

TESTS_PATHS = [os.path.abspath(os.path.join(os.path.dirname(__file__), 'misc'))]

class TestBasic(TestCase):

    def checkDeprecatedUses(self, code, expected_output):
        sio = StringIO(dedent(code))
        output = memestra.memestra(sio, ('deprecated', 'deprecated'), 'reason',
                                   search_paths=TESTS_PATHS)
        self.assertEqual(output, expected_output)


    def test_default_kwarg(self):
        code = '''
            import deprecated

            @deprecated.deprecated(reason='use another function')
            def foo(): pass

            foo()'''

        self.checkDeprecatedUses(
            code,
            [('foo', '<>', 7, 0, 'use another function')])

    def test_no_keyword(self):
        code = '''
            import deprecated

            @deprecated.deprecated('use another function')
            def foo(): pass

            foo()'''

        self.checkDeprecatedUses(code,
            [('foo', '<>', 7, 0, 'use another function')])

    def test_multiple_args(self):
        code = '''
            import deprecated

            @deprecated.deprecated(unrelated='unrelated content',
                type='magical', reason='another reason')
            def foo(): pass

            foo()'''

        self.checkDeprecatedUses(
            code,
            [('foo', '<>', 8, 0, 'another reason')])


class TestCLI(TestCase):

    def test_default_kwarg(self):
        fid, tmppy = tempfile.mkstemp(suffix='.py')
        code = '''
            import deprecated

            @deprecated.deprecated(reason='use another function')
            def foo(): pass

            foo()'''

        ref = 'foo used at {}:7:1 - use another function\n'.format(tmppy)
        os.write(fid, dedent(code).encode())
        os.close(fid)
        test_args = ['memestra', tmppy]
        with mock.patch.object(sys, 'argv', test_args):
            from memestra.memestra import run
            with StringIO() as buf:
                with contextlib.redirect_stdout(buf):
                    run()
                self.assertEqual(buf.getvalue(), ref)
