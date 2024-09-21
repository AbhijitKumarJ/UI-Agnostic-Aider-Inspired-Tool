# tests/test_ai_integration.py

import unittest
from unittest.mock import patch
from core.feature_registry import FeatureRegistry
from features.ai_integration import AIIntegration

class TestAIIntegration(unittest.TestCase):
    @patch('providers.get_provider')
    def test_generate_code(self, mock_get_provider):
        mock_provider = mock_get_provider.return_value
        mock_provider.generate_code.return_value = "Generated Code"
        mock_provider.default_model = "default_model"

        ai_integration = AIIntegration('mock_provider', None)
        result = ai_integration.generate_code("Test prompt")
        
        self.assertEqual(result, "Generated Code")
        mock_provider.generate_code.assert_called_once_with('default_model', "Test prompt")

    @patch('providers.get_provider')
    def test_explain_code(self, mock_get_provider):
        mock_provider = mock_get_provider.return_value
        mock_provider.generate_code.return_value = "Code Explanation"
        mock_provider.default_model = "default_model"

        ai_integration = AIIntegration('mock_provider', None)
        result = ai_integration.explain_code("def test(): pass")
        
        self.assertEqual(result, "Code Explanation")
        mock_provider.generate_code.assert_called_once_with('default_model', "Explain the following code:\n\ndef test(): pass")

if __name__ == '__main__':
    unittest.main()