from unittest import TestCase
from memestra.docparse import docparse

def sample_function():
    """
    I'm a deprecated function
    """

class sample_class:
    'deprecated too'

class TestDocparse(TestCase):

    def test_docparse(self):
        deprecated = docparse(__file__, r'.*deprecated.*')
        self.assertEqual(deprecated, ['sample_function', 'sample_class'])
