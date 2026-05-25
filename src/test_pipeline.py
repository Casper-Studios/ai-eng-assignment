#!/usr/bin/env python3
"""
LLM Analysis Pipeline Test Script

This script tests the complete 3-step pipeline with support for both single recipe
testing and full recipe directory validation.

Usage:
    python test_pipeline.py single    # Test single chocolate chip cookie recipe
    python test_pipeline.py all       # Test all recipes in data directory
"""

import os
import sys
from pathlib import Path

from llm_pipeline.pipeline import LLMAnalysisPipeline
from llm_pipeline.env_loader import load_project_env
from loguru import logger

# Load environment variables from supported project locations.
load_project_env()

REPO_ROOT = Path(__file__).resolve().parents[1]


def has_llm_api_key() -> bool:
    """Check whether any supported LLM provider has credentials configured."""
    return bool(os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY"))


def test_single_recipe():
    """Test the pipeline with the chocolate chip cookie recipe."""

    # Check for supported LLM API key
    if not has_llm_api_key():
        logger.error("No supported LLM API key configured")
        logger.info(
            "Set GEMINI_API_KEY for Google AI Studio or OPENAI_API_KEY in your .env file"
        )
        return False

    # Initialize pipeline
    try:
        pipeline = LLMAnalysisPipeline()
        logger.info("Pipeline initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        return False

    # Test with chocolate chip cookie recipe
    recipe_file = REPO_ROOT / "data" / "recipe_10813_best-chocolate-chip-cookies.json"
    if not recipe_file.exists():
        logger.error(f"Recipe file not found: {recipe_file}")
        return False

    logger.info(f"Testing with recipe file: {recipe_file}")

    try:
        max_reviews = int(os.getenv("SINGLE_RECIPE_MAX_REVIEWS", "1"))

        # Process the recipe
        enhanced_recipe = pipeline.process_single_recipe(
            recipe_file=recipe_file,
            save_output=True,
            max_reviews=max_reviews,
        )

        if enhanced_recipe:
            logger.success("✓ Single recipe test successful!")
            logger.info(f"Enhanced recipe: {enhanced_recipe.title}")
            logger.info(f"Modifications applied: {len(enhanced_recipe.modifications_applied)}")
            logger.info(f"Total changes: {enhanced_recipe.enhancement_summary.total_changes}")
            logger.info(f"Expected impact: {enhanced_recipe.enhancement_summary.expected_impact}")
            return True
        else:
            logger.error("✗ Single recipe test failed - no enhanced recipe generated")
            return False

    except Exception as e:
        logger.error(f"Single recipe test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_all_recipes():
    """Test the pipeline with all scraped recipes."""

    # Check for supported LLM API key
    if not has_llm_api_key():
        logger.error("No supported LLM API key configured")
        logger.info(
            "Set GEMINI_API_KEY for Google AI Studio or OPENAI_API_KEY in your .env file"
        )
        return False

    # Initialize pipeline
    try:
        pipeline = LLMAnalysisPipeline()
        logger.info("Pipeline initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        return False

    try:
        max_recipes = os.getenv("ALL_RECIPES_MAX_FILES")
        max_reviews_per_recipe = os.getenv("ALL_RECIPES_MAX_REVIEWS", "1")

        # Process all recipes
        enhanced_recipes = pipeline.process_recipe_directory(
            data_dir=str(REPO_ROOT / "data"),
            max_reviews_per_recipe=int(max_reviews_per_recipe),
            max_recipes=int(max_recipes) if max_recipes else None,
        )

        # Generate summary report
        report_path = pipeline.save_summary_report(enhanced_recipes)

        logger.info(f"\n{'=' * 60}")
        logger.success("✓ All recipes test complete!")
        logger.info(f"Enhanced recipes: {len(enhanced_recipes)}")
        logger.info(f"Summary report saved to: {report_path}")

        return len(enhanced_recipes) > 0

    except Exception as e:
        logger.error(f"All recipes test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function with mode selection."""

    # Parse command line argument
    if len(sys.argv) < 2:
        logger.error("Usage: python test_pipeline.py [single|all]")
        logger.info("  single - Test single chocolate chip cookie recipe")
        logger.info("  all    - Test all recipes in data directory")
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == "single":
        logger.info("Starting LLM Analysis Pipeline - Single Recipe Test")
        logger.info("=" * 60)
        success = test_single_recipe()

        logger.info("=" * 60)
        if success:
            logger.success("Single recipe test passed! ✓")
            logger.info("Check the 'data/enhanced/' directory for the enhanced recipe.")
        else:
            logger.error("Single recipe test failed! ✗")
            sys.exit(1)

    elif mode == "all":
        logger.info("Starting LLM Analysis Pipeline - All Recipes Validation")
        logger.info("=" * 60)
        success = test_all_recipes()

        logger.info("=" * 60)
        if success:
            logger.success("All recipes validation passed! ✓")
            logger.info("Check the 'data/enhanced/' directory for all enhanced recipes.")
            logger.info("Check 'data/enhanced/pipeline_summary_report.json' for detailed results.")
        else:
            logger.error("All recipes validation failed! ✗")
            sys.exit(1)

    else:
        logger.error(f"Unknown mode: {mode}")
        logger.error("Usage: python test_pipeline.py [single|all]")
        sys.exit(1)


if __name__ == "__main__":
    main()