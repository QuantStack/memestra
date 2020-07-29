from unittest import TestCase
from textwrap import dedent
from io import StringIO

import memestra

import os
import sys
TESTS_FAKE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'misc', 'test.py'))

class TestBasic(TestCase):

    def checkDeprecatedUses(self, code, expected_output):
        sio = StringIO(dedent(code))
        output = memestra.memestra(sio, ('deprecated', 'deprecated'), 'reason',
                                    file_path=TESTS_FAKE_FILE)
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
