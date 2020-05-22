from unittest import TestCase
from memestra import nbmemestra

class NotebookTest(TestCase):

    def test_nb_demo(self):
        output = nbmemestra.nbmemestra("tests/misc/memestra_nb_demo.ipynb", ('decoratortest', 'deprecated'), "tests/misc/memestra_nb_demo.ipynb")
        expected_output = [('some_module.foo', 'Cell[0]', 2, 0),
                           ('some_module.foo', 'Cell[0]', 3, 0),
                           ('some_module.foo', 'Cell[2]', 1, 0)]
        self.assertEqual(output, expected_output)
