import os
from unittest import TestCase
from memestra import nbmemestra, preprocessor
import nbformat
from traitlets.config import Config
from nbconvert import RSTExporter


class NotebookTest(TestCase):

    def test_nb_demo(self):
        output = nbmemestra.nbmemestra(os.path.join('tests', 'misc', 'memestra_nb_demo.ipynb'), ('decoratortest', 'deprecated'))
        expected_output = [('some_module.foo', 'Cell[0]', 2, 0),
                           ('some_module.foo', 'Cell[0]', 3, 0),
                           ('some_module.foo', 'Cell[2]', 2, 4)]
        self.assertEqual(output, expected_output)

    def test_nbconvert_demo(self):
        with open(os.path.join('tests', 'misc', 'memestra_nb_demo.ipynb')) as f:
            notebook = nbformat.read(f, as_version=4)

        c = Config()
        c.MemestraDeprecationChecker.decorator = ('decoratortest', 'deprecated')
        c.RSTExporter.preprocessors = [preprocessor.MemestraDeprecationChecker]

        deprecation_checker = RSTExporter(config=c)

        rst = deprecation_checker.from_notebook_node(notebook)[0]

        with open(os.path.join('tests', 'misc', 'memestra_nb_demo.rst')) as f:
            rst_true = f.read()

        self.assertEqual(rst, rst_true)
