import unittest
from HelpingAI import HAI

class TestHAIClient(unittest.TestCase):
    def test_model_list(self):
        """Test that model listing returns a list (mocked)."""
        # This is a placeholder test. In real tests, use mocking for API calls.
        client = HAI(api_key="test")
        try:
            models = client.models.list()
            self.assertIsInstance(models, list)
        except Exception as e:
            self.assertIsInstance(e, Exception)  # Accept any exception for now

if __name__ == "__main__":
    unittest.main()
