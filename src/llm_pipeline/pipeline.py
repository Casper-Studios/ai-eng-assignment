"""
LLM Analysis Pipeline - Main Orchestrator

This module coordinates the complete 3-step pipeline:
1. Extract modifications from reviews
2. Apply modifications to recipes
3. Generate enhanced recipes with attribution

Processes recipe data from scraped JSON files and outputs enhanced recipes.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

from .env_loader import load_project_env
from .enhanced_recipe_generator import EnhancedRecipeGenerator
from .models import EnhancedRecipe, Recipe, Review
from .recipe_modifier import RecipeModifier
from .tweak_extractor import TweakExtractor


class LLMAnalysisPipeline:
    """Complete pipeline for analyzing recipes and generating enhanced versions."""

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        output_dir: str = "data/enhanced",
        pipeline_version: str = "1.0.0",
        tweak_extractor: Optional[TweakExtractor] = None,
        recipe_modifier: Optional[RecipeModifier] = None,
        enhanced_generator: Optional[EnhancedRecipeGenerator] = None,
    ):
        """
        Initialize the complete LLM Analysis Pipeline.

        Args:
            openai_api_key: OpenAI API key (loads from env if not provided)
            output_dir: Directory to save enhanced recipes
            pipeline_version: Version identifier for tracking
        """
        # Load environment variables
        load_project_env()

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize pipeline components
        self.tweak_extractor = tweak_extractor or TweakExtractor(api_key=openai_api_key)
        self.recipe_modifier = recipe_modifier or RecipeModifier()
        self.enhanced_generator = enhanced_generator or EnhancedRecipeGenerator(
            pipeline_version=pipeline_version
        )

        logger.info(f"Initialized LLM Analysis Pipeline v{pipeline_version}")
        logger.info(f"Output directory: {self.output_dir}")

    def load_recipe_data(self, file_path: str) -> Dict[str, Any]:
        """
        Load recipe data from JSON file.

        Args:
            file_path: Path to recipe JSON file

        Returns:
            Recipe data dictionary
        """
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def parse_recipe_data(self, recipe_data: Dict[str, Any]) -> Recipe:
        """
        Parse raw recipe data into Recipe object.

        Args:
            recipe_data: Raw recipe data from JSON

        Returns:
            Recipe object
        """
        return Recipe(
            recipe_id=recipe_data.get("recipe_id", "unknown"),
            title=recipe_data.get("title", "Unknown Recipe"),
            ingredients=recipe_data.get("ingredients", []),
            instructions=recipe_data.get("instructions", []),
            description=recipe_data.get("description"),
            servings=recipe_data.get("servings"),
            rating=recipe_data.get("rating"),
        )

    def parse_reviews_data(self, recipe_data: Dict[str, Any]) -> List[Review]:
        """
        Parse raw review data into Review objects.

        Args:
            recipe_data: Raw recipe data containing reviews

        Returns:
            List of Review objects
        """
        def normalize_review_text(text: str) -> str:
            return " ".join(text.split()).strip().lower()

        combined_reviews: dict[str, Review] = {}

        for review_data in recipe_data.get("featured_tweaks", []):
            if not review_data.get("text"):
                continue

            review = Review(
                text=review_data["text"],
                rating=review_data.get("rating"),
                username=review_data.get("username"),
                has_modification=review_data.get("has_modification", True),
                is_featured=True,
            )
            combined_reviews[normalize_review_text(review.text)] = review

        for review_data in recipe_data.get("reviews", []):
            if not review_data.get("text"):
                continue

            normalized_text = normalize_review_text(review_data["text"])
            existing_review = combined_reviews.get(normalized_text)

            if existing_review:
                existing_review.rating = existing_review.rating or review_data.get("rating")
                existing_review.username = existing_review.username or review_data.get("username")
                existing_review.has_modification = (
                    existing_review.has_modification
                    or review_data.get("has_modification", False)
                )
                continue

            combined_reviews[normalized_text] = Review(
                text=review_data["text"],
                rating=review_data.get("rating"),
                username=review_data.get("username"),
                has_modification=review_data.get("has_modification", False),
                is_featured=False,
            )

        return sorted(
            combined_reviews.values(),
            key=lambda review: (
                not review.is_featured,
                -(review.rating or 0),
            ),
        )

    def process_single_recipe(
        self,
        recipe_file: str,
        save_output: bool = True,
        max_reviews: Optional[int] = None,
    ) -> Optional[EnhancedRecipe]:
        """
        Process a single recipe through the complete pipeline.

        Args:
            recipe_file: Path to recipe JSON file
            save_output: Whether to save the enhanced recipe

        Returns:
            EnhancedRecipe if successful, None otherwise
        """
        try:
            logger.info(f"Processing recipe file: {recipe_file}")

            # Step 0: Load and parse data
            recipe_data = self.load_recipe_data(recipe_file)
            recipe = self.parse_recipe_data(recipe_data)
            reviews = self.parse_reviews_data(recipe_data)

            logger.info(f"Loaded recipe: {recipe.title}")
            logger.info(
                f"Found {len(reviews)} reviews, {len([r for r in reviews if r.has_modification])} with modifications"
            )

            if not any(r.has_modification for r in reviews):
                logger.warning("No reviews with modifications found")
                return None

            candidate_reviews = [r for r in reviews if r.has_modification]

            # Step 1: Extract modifications from prioritized reviews.
            logger.info(
                f"Step 1: Extracting modifications from {len(candidate_reviews)} prioritized reviews..."
            )
            extracted_modifications = self.tweak_extractor.extract_modifications(
                candidate_reviews, recipe, max_reviews=max_reviews
            )

            if not extracted_modifications:
                logger.warning("No modifications could be extracted")
                return None

            logger.info(
                f"Successfully extracted {len(extracted_modifications)} candidate modifications"
            )

            # Step 2: Apply successful modifications sequentially.
            logger.info("Step 2: Applying extracted modifications to recipe...")
            modified_recipe = recipe
            successful_modifications: list[
                tuple[Any, Review, List[Any]]
            ] = []

            for modification, source_review in extracted_modifications:
                modified_recipe, change_records = self.recipe_modifier.apply_modification(
                    modified_recipe, modification
                )

                if change_records:
                    successful_modifications.append(
                        (modification, source_review, change_records)
                    )
                    logger.info(
                        f"Applied {modification.modification_type}: {len(change_records)} changes made"
                    )
                else:
                    logger.warning(
                        f"Skipped attribution for {modification.modification_type}: no concrete changes were applied"
                    )

            if not successful_modifications:
                logger.warning("No extracted modifications produced concrete recipe changes")
                return None

            # Step 3: Generate enhanced recipe with attribution
            logger.info("Step 3: Generating enhanced recipe with attribution...")

            enhanced_recipe = self.enhanced_generator.generate_enhanced_recipe_from_modifications(
                recipe, modified_recipe, successful_modifications
            )

            logger.info(f"Generated enhanced recipe: {enhanced_recipe.title}")

            # Save output
            if save_output:
                output_filename = f"enhanced_{recipe.recipe_id}_{recipe.title.lower().replace(' ', '-')[:30]}.json"
                output_path = self.output_dir / output_filename
                self.enhanced_generator.save_enhanced_recipe(
                    enhanced_recipe, str(output_path)
                )

            return enhanced_recipe

        except Exception as e:
            logger.error(f"Failed to process recipe {recipe_file}: {e}")
            import traceback

            traceback.print_exc()
            return None

    def process_recipe_directory(
        self,
        data_dir: str = "data",
        max_reviews_per_recipe: Optional[int] = None,
        max_recipes: Optional[int] = None,
    ) -> List[EnhancedRecipe]:
        """
        Process all recipe files in a directory.

        Args:
            data_dir: Directory containing recipe JSON files
            max_reviews_per_recipe: Optional cap on extracted reviews per recipe
            max_recipes: Optional cap on number of recipe files to process

        Returns:
            List of successfully processed EnhancedRecipe objects
        """
        data_path = Path(data_dir)
        recipe_files = sorted(data_path.glob("recipe_*.json"))

        if max_recipes is not None:
            recipe_files = recipe_files[:max_recipes]

        logger.info(f"Found {len(recipe_files)} recipe files to process")

        enhanced_recipes = []
        for recipe_file in recipe_files:
            logger.info(f"\n{'=' * 60}")
            enhanced_recipe = self.process_single_recipe(
                str(recipe_file),
                max_reviews=max_reviews_per_recipe,
            )

            if enhanced_recipe:
                enhanced_recipes.append(enhanced_recipe)
                logger.info(f"✓ Successfully processed: {enhanced_recipe.title}")
            else:
                logger.warning(f"✗ Failed to process: {recipe_file.name}")

        logger.info(f"\n{'=' * 60}")
        logger.info(
            f"Pipeline complete: {len(enhanced_recipes)}/{len(recipe_files)} recipes successfully enhanced"
        )

        return enhanced_recipes

    def generate_summary_report(
        self, enhanced_recipes: List[EnhancedRecipe]
    ) -> Dict[str, Any]:
        """
        Generate a summary report of pipeline results.

        Args:
            enhanced_recipes: List of enhanced recipes

        Returns:
            Summary report dictionary
        """
        if not enhanced_recipes:
            return {"status": "no_recipes_processed"}

        total_modifications = sum(
            len(recipe.modifications_applied) for recipe in enhanced_recipes
        )
        total_changes = sum(
            recipe.enhancement_summary.total_changes for recipe in enhanced_recipes
        )

        change_type_counts = {}
        for recipe in enhanced_recipes:
            for change_type in recipe.enhancement_summary.change_types:
                change_type_counts[change_type] = (
                    change_type_counts.get(change_type, 0) + 1
                )

        report = {
            "pipeline_summary": {
                "recipes_processed": len(enhanced_recipes),
                "total_modifications_applied": total_modifications,
                "total_changes_made": total_changes,
                "change_type_distribution": change_type_counts,
            },
            "enhanced_recipes": [
                {
                    "recipe_id": recipe.recipe_id,
                    "title": recipe.title,
                    "modifications_count": len(recipe.modifications_applied),
                    "changes_count": recipe.enhancement_summary.total_changes,
                    "change_types": recipe.enhancement_summary.change_types,
                }
                for recipe in enhanced_recipes
            ],
        }

        return report

    def save_summary_report(
        self, enhanced_recipes: List[EnhancedRecipe], output_path: Optional[str] = None
    ) -> str:
        """
        Save pipeline summary report to JSON file.

        Args:
            enhanced_recipes: List of enhanced recipes
            output_path: Path to save report (auto-generated if None)

        Returns:
            Path to saved report
        """
        if output_path is None:
            output_path = str(self.output_dir / "pipeline_summary_report.json")

        report = self.generate_summary_report(enhanced_recipes)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved pipeline summary report to: {output_path}")
        return output_path
