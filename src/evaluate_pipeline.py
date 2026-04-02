#!/usr/bin/env python3
"""
Pipeline Evaluation Script

Evaluates the complete LLM analysis pipeline by:
- Loading recipes with multiple reviews
- Extracting modifications from reviews
- Applying modifications to recipes
- Generating enhanced recipes
- Printing detailed output and metrics
- Saving enhanced recipes to data/enhanced/

Usage:
    python evaluate_pipeline.py
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from loguru import logger

from llm_pipeline.models import Recipe, Review
from llm_pipeline.pipeline import LLMAnalysisPipeline
from llm_pipeline.recipe_modifier import RecipeModifier
from llm_pipeline.tweak_extractor import TweakExtractor
from llm_pipeline.enhanced_recipe_generator import EnhancedRecipeGenerator


# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO", format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>")


class PipelineEvaluator:
    """Evaluates the complete pipeline with detailed output and metrics."""

    def __init__(self, data_dir: str = "../data", output_dir: str = "../data/enhanced"):
        """Initialize the evaluator."""
        load_dotenv()

        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize pipeline components
        self.tweak_extractor = TweakExtractor()
        self.recipe_modifier = RecipeModifier()
        self.enhanced_generator = EnhancedRecipeGenerator()

        # Metrics tracking
        self.metrics = {
            "total_recipes": 0,
            "total_modifications_extracted": 0,
            "total_edits_applied": 0,
            "total_reviews_processed": 0,
        }

        logger.info("Pipeline Evaluator initialized")

    def load_recipe_json(self, file_path: Path) -> Dict[str, Any]:
        """Load recipe from JSON file."""
        with open(file_path, "r") as f:
            return json.load(f)

    def load_recipes(self, limit: int = 3) -> List[Path]:
        """Load limited number of recipe files for evaluation."""
        recipe_files = sorted(self.data_dir.glob("recipe_*.json"))
        logger.info(f"Found {len(recipe_files)} recipe files")
        return recipe_files[:limit]

    def evaluate_recipe(self, recipe_file: Path) -> bool:
        """Evaluate pipeline on a single recipe."""
        logger.info(f"\n{'='*80}")
        logger.info(f"Processing: {recipe_file.name}")
        logger.info(f"{'='*80}")

        try:
            # Load recipe data
            recipe_data = self.load_recipe_json(recipe_file)
            
            # Parse recipe and reviews
            recipe = Recipe(
                recipe_id=recipe_data.get("recipe_id"),
                title=recipe_data.get("title"),
                ingredients=recipe_data.get("ingredients", []),
                instructions=recipe_data.get("instructions", []),
                description=recipe_data.get("description"),
                servings=recipe_data.get("servings"),
            )

            reviews = []
            for review_data in recipe_data.get("reviews", []):
                review = Review(
                    text=review_data.get("text"),
                    rating=review_data.get("rating"),
                    username=review_data.get("username"),
                    has_modification=review_data.get("has_modification", False),
                )
                reviews.append(review)

            logger.info(f"Recipe: {recipe.title}")
            logger.info(f"Loaded {len(reviews)} reviews ({sum(1 for r in reviews if r.has_modification)} with modifications)")

            # Print original recipe
            logger.info("\n--- ORIGINAL RECIPE ---")
            logger.info(f"Ingredients ({len(recipe.ingredients)}):")
            for ing in recipe.ingredients[:3]:
                logger.info(f"  • {ing}")
            if len(recipe.ingredients) > 3:
                logger.info(f"  ... and {len(recipe.ingredients) - 3} more")

            logger.info(f"Instructions ({len(recipe.instructions)}):")
            for inst in recipe.instructions[:2]:
                logger.info(f"  • {inst[:60]}...")
            if len(recipe.instructions) > 2:
                logger.info(f"  ... and {len(recipe.instructions) - 2} more")

            # Extract modifications
            logger.info("\n--- EXTRACTING MODIFICATIONS ---")
            modifications_with_reviews = self.tweak_extractor.extract_multiple_modifications(
                reviews, recipe, limit=3
            )
            self.metrics["total_modifications_extracted"] += len(modifications_with_reviews)
            self.metrics["total_reviews_processed"] += len(reviews)

            if not modifications_with_reviews:
                logger.warning("No modifications extracted")
                return False

            logger.info(f"Extracted {len(modifications_with_reviews)} modification(s)")

            # Print extracted modifications
            for idx, (modification, source_review) in enumerate(modifications_with_reviews, 1):
                logger.info(f"\n  Modification {idx}: {modification.modification_type}")
                logger.info(f"  Reasoning: {modification.reasoning}")
                logger.info(f"  Edits: {len(modification.edits)}")
                for edit in modification.edits[:2]:
                    logger.info(f"    - {edit.operation} on {edit.target}: '{edit.find[:40]}...'")
                if len(modification.edits) > 2:
                    logger.info(f"    ... and {len(modification.edits) - 2} more")

            # Apply modifications
            logger.info("\n--- APPLYING MODIFICATIONS ---")
            extracted_modifications = [
                modification for modification, _ in modifications_with_reviews
            ]
            modified_recipe, change_records_batch = (
                self.recipe_modifier.apply_modifications_batch(
                    recipe, extracted_modifications
                )
            )

            total_changes_applied = sum(
                len(change_records) for change_records in change_records_batch
            )
            self.metrics["total_edits_applied"] += total_changes_applied

            logger.info(
                f"Applied {len(change_records_batch)} modification batch(es)"
            )

            if change_records_batch:
                for idx, change_records in enumerate(change_records_batch, 1):
                    logger.info(f"\n  Applied modification {idx}:")
                    logger.info(f"    Changes made: {len(change_records)}")
                    for change in change_records[:2]:
                        logger.info(f"      • {change.operation} {change.type}")
                        logger.info(f"        from: {change.from_text[:40]}...")
                        logger.info(f"        to: {change.to_text[:40]}...")
                    if len(change_records) > 2:
                        logger.info(
                            f"      ... and {len(change_records) - 2} more changes"
                        )

            # Generate enhanced recipe
            logger.info("\n--- GENERATING ENHANCED RECIPE ---")
            enhanced = self.enhanced_generator.generate_enhanced_recipe_batch(
                recipe,
                modified_recipe,
                modifications_with_reviews,
                change_records_batch,
            )

            logger.info(f"Generated enhanced recipe: {enhanced.title}")
            logger.info(f"  Modifications applied: {len(enhanced.modifications_applied)}")
            logger.info(f"  Total changes: {enhanced.enhancement_summary.total_changes}")
            logger.info(f"  Change types: {enhanced.enhancement_summary.change_types}")
            logger.info(f"  Expected impact: {enhanced.enhancement_summary.expected_impact}")

            # Print enhanced recipe summary
            logger.info("\n--- ENHANCED RECIPE SUMMARY ---")
            logger.info(f"Ingredients ({len(enhanced.ingredients)}):")
            for ing in enhanced.ingredients[:3]:
                logger.info(f"  • {ing}")
            if len(enhanced.ingredients) > 3:
                logger.info(f"  ... and {len(enhanced.ingredients) - 3} more")

            logger.info(f"Instructions ({len(enhanced.instructions)}):")
            for inst in enhanced.instructions[:2]:
                logger.info(f"  • {inst[:60]}...")
            if len(enhanced.instructions) > 2:
                logger.info(f"  ... and {len(enhanced.instructions) - 2} more")

            # Save enhanced recipe
            output_path = self.output_dir / f"enhanced_{recipe.recipe_id}_{recipe.title[:30].replace(' ', '_')}.json"
            with open(output_path, "w") as f:
                json.dump(enhanced.model_dump(), f, indent=2)
            logger.info(f"\nSaved to: {output_path}")

            self.metrics["total_recipes"] += 1
            return True

        except Exception as e:
            logger.error(f"Error processing recipe: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run_evaluation(self, limit: int = 3):
        """Run evaluation on multiple recipes."""
        logger.info(f"\n{'='*80}")
        logger.info("PIPELINE EVALUATION START")
        logger.info(f"{'='*80}\n")

        # Check for API key
        if not os.getenv("OPENAI_API_KEY"):
            logger.warning("OPENAI_API_KEY not set - extraction will be skipped")

        # Load and process recipes
        recipe_files = self.load_recipes(limit=limit)
        successful = 0

        for recipe_file in recipe_files:
            if self.evaluate_recipe(recipe_file):
                successful += 1

        # Print summary metrics
        logger.info(f"\n{'='*80}")
        logger.info("EVALUATION SUMMARY METRICS")
        logger.info(f"{'='*80}")
        logger.info(f"Recipes processed: {self.metrics['total_recipes']}/{len(recipe_files)} successful")
        logger.info(f"Total reviews processed: {self.metrics['total_reviews_processed']}")
        logger.info(f"Total modifications extracted: {self.metrics['total_modifications_extracted']}")
        logger.info(f"Total edits applied: {self.metrics['total_edits_applied']}")

        if self.metrics["total_recipes"] > 0:
            avg_mods = self.metrics["total_modifications_extracted"] / self.metrics["total_recipes"]
            avg_edits = self.metrics["total_edits_applied"] / self.metrics["total_recipes"]
            logger.info(f"Avg modifications per recipe: {avg_mods:.1f}")
            logger.info(f"Avg edits per recipe: {avg_edits:.1f}")

        logger.info(f"Enhanced recipes saved to: {self.output_dir}")
        logger.info(f"{'='*80}\n")

        return successful == len(recipe_files)


def main():
    """Main entry point."""
    evaluator = PipelineEvaluator()
    success = evaluator.run_evaluation(limit=3)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
