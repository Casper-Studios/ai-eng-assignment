import json
import tempfile
import unittest
from pathlib import Path

from llm_pipeline.models import ModificationEdit, ModificationObject
from llm_pipeline.pipeline import LLMAnalysisPipeline


class StubTweakExtractor:
    def extract_modifications(self, reviews, recipe, max_reviews=None):
        results = []
        for review in reviews:
            if "egg yolk" in review.text:
                results.append(
                    (
                        ModificationObject(
                            modification_type="addition",
                            reasoning="Extra yolk improves chewiness",
                            edits=[
                                ModificationEdit(
                                    target="ingredients",
                                    operation="add_after",
                                    find="2 eggs",
                                    add="1 egg yolk",
                                )
                            ],
                        ),
                        review,
                    )
                )
            if "cream of tartar" in review.text:
                results.append(
                    (
                        ModificationObject(
                            modification_type="addition",
                            reasoning="Cream of tartar helps cookies hold shape",
                            edits=[
                                ModificationEdit(
                                    target="ingredients",
                                    operation="remove",
                                    find="2 teaspoons hot water",
                                ),
                                ModificationEdit(
                                    target="ingredients",
                                    operation="add_after",
                                    find="0.5 teaspoon salt",
                                    add="1 teaspoon cream of tartar",
                                ),
                            ],
                        ),
                        review,
                    )
                )
        return results


class PipelineTests(unittest.TestCase):
    def test_parse_reviews_data_deduplicates_and_prioritizes_featured_tweaks(self):
        pipeline = LLMAnalysisPipeline(tweak_extractor=StubTweakExtractor())
        recipe_data = {
            "featured_tweaks": [
                {
                    "text": "Use more brown sugar",
                    "rating": 5,
                    "has_modification": True,
                }
            ],
            "reviews": [
                {
                    "text": "Use more brown sugar",
                    "rating": 5,
                    "has_modification": True,
                },
                {
                    "text": "Great recipe",
                    "rating": 5,
                    "has_modification": False,
                },
            ],
        }

        reviews = pipeline.parse_reviews_data(recipe_data)

        self.assertEqual(len(reviews), 2)
        self.assertTrue(reviews[0].is_featured)
        self.assertEqual(reviews[0].text, "Use more brown sugar")

    def test_process_single_recipe_applies_multiple_modifications(self):
        recipe_data = {
            "recipe_id": "10813",
            "title": "Best Chocolate Chip Cookies",
            "ingredients": [
                "1 cup butter, softened",
                "2 eggs",
                "2 teaspoons hot water",
                "0.5 teaspoon salt",
            ],
            "instructions": [
                "Mix everything together.",
                "Bake in the preheated oven until edges are nicely browned, about 10 minutes.",
            ],
            "featured_tweaks": [
                {
                    "text": "I added an additional egg yolk to help keep the cookie chewy.",
                    "rating": 5,
                    "has_modification": True,
                },
                {
                    "text": "I added a teaspoon of cream of tartar to the batter and omitted the water.",
                    "rating": 5,
                    "has_modification": True,
                },
            ],
            "reviews": [],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            recipe_path = Path(temp_dir) / "recipe_10813_best-chocolate-chip-cookies.json"
            recipe_path.write_text(json.dumps(recipe_data), encoding="utf-8")

            pipeline = LLMAnalysisPipeline(
                output_dir=temp_dir,
                tweak_extractor=StubTweakExtractor(),
            )

            enhanced_recipe = pipeline.process_single_recipe(str(recipe_path), save_output=False)

        self.assertIsNotNone(enhanced_recipe)
        self.assertEqual(len(enhanced_recipe.modifications_applied), 2)
        self.assertIn("1 egg yolk", enhanced_recipe.ingredients)
        self.assertIn("1 teaspoon cream of tartar", enhanced_recipe.ingredients)
        self.assertNotIn("2 teaspoons hot water", enhanced_recipe.ingredients)


if __name__ == "__main__":
    unittest.main()