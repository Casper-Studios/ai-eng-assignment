import os
import unittest
from unittest.mock import patch

from llm_pipeline.tweak_extractor import TweakExtractor


class TweakExtractorConfigTests(unittest.TestCase):
    def test_prefers_gemini_when_gemini_key_is_present(self):
        with patch.dict(
            os.environ,
            {"GEMINI_API_KEY": "gemini-test-key"},
            clear=True,
        ), patch("llm_pipeline.tweak_extractor.load_project_env"):
            extractor = TweakExtractor()

        self.assertEqual(extractor.provider, "gemini")
        self.assertEqual(extractor.model, "gemini-3.5-flash")
        self.assertEqual(
            extractor.base_url,
            "https://generativelanguage.googleapis.com/v1beta/openai/",
        )

    def test_uses_openai_when_provider_is_explicit(self):
        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "openai-test-key", "LLM_PROVIDER": "openai"},
            clear=True,
        ), patch("llm_pipeline.tweak_extractor.load_project_env"):
            extractor = TweakExtractor()

        self.assertEqual(extractor.provider, "openai")
        self.assertEqual(extractor.model, "gpt-4o-mini")
        self.assertIsNone(extractor.base_url)

    def test_raises_clear_error_when_no_key_is_present(self):
        with patch.dict(os.environ, {}, clear=True), patch(
            "llm_pipeline.tweak_extractor.load_project_env"
        ):
            with self.assertRaises(ValueError):
                TweakExtractor()


if __name__ == "__main__":
    unittest.main()