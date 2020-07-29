import os
from unittest import TestCase
from memestra import nbmemestra, preprocessor
import nbformat
from traitlets.config import Config
from nbconvert import RSTExporter


this_dir = os.path.dirname(os.path.abspath(__file__))
TESTS_NB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'misc', 'memestra_nb_demo.ipynb'))
import sys
sys.path.insert(0, os.path.join(this_dir, 'misc'))

class NotebookTest(TestCase):

    def test_nb_demo(self):
        output = nbmemestra.nbmemestra(TESTS_NB_FILE,
                                       ('decoratortest', 'deprecated'),
                                       TESTS_NB_FILE)
        expected_output = [('some_module.foo', 'Cell[0]', 2, 0),
                           ('some_module.foo', 'Cell[0]', 3, 0),
                           ('some_module.foo', 'Cell[2]', 2, 4)]
        self.assertEqual(output, expected_output)

    def test_nbconvert_demo(self):
        self.maxDiff = None
        with open(TESTS_NB_FILE) as f:
            notebook = nbformat.read(f, as_version=4)

        c = Config()
        c.MemestraDeprecationChecker.decorator = ('decoratortest', 'deprecated')
        c.RSTExporter.preprocessors = [preprocessor.MemestraDeprecationChecker]

        deprecation_checker = RSTExporter(config=c)

        # the RST exporter behaves differently on windows and on linux
        # there can be some lines with only whitespaces
        # so we ignore differences that only consist of empty lines
        rst = deprecation_checker.from_notebook_node(notebook)[0]
        lines = rst.split('\n')
        lines = [l.rstrip() for l in lines]
        rst = '\n'.join(lines)

        with open(os.path.join(this_dir, 'misc', 'memestra_nb_demo.rst')) as f:
            rst_true = f.read()

        self.assertEqual(rst, rst_true)
