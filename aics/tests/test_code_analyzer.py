
import unittest
from features.code_analysis import CodeAnalyzer

class TestCodeAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = CodeAnalyzer()

    def test_analyze_python(self):
        test_code = """
import math

def factorial(n):
    return math.factorial(n)

class Calculator:
    def add(self, a, b):
        return a + b
"""
        analysis = self.analyzer.analyze_python(test_code)
        self.assertEqual(analysis['functions'], ['factorial'])
        self.assertEqual(analysis['classes'], ['Calculator'])
        self.assertEqual(analysis['imports'], ['math'])

if __name__ == '__main__':
    unittest.main()
