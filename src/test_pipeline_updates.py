#!/usr/bin/env python3
"""
Test script to validate the updated pipeline logic for multiple modifications.

This script now supports processing real recipes and generating enhanced output files.

Usage:
    python test_pipeline_updates.py single    # Test single chocolate chip cookie recipe
    python test_pipeline_updates.py all       # Test all recipes in data directory
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from llm_pipeline.pipeline import LLMAnalysisPipeline
from llm_pipeline.models import (
    Review, Recipe, ModificationObject, ModificationEdit,
    ChangeRecord, SourceReview, ModificationApplied
)
from llm_pipeline.recipe_modifier import RecipeModifier
from llm_pipeline.enhanced_recipe_generator import EnhancedRecipeGenerator
from llm_pipeline.tweak_extractor import TweakExtractor
from loguru import logger

# Load environment variables from .env file
load_dotenv()


def create_test_modifications():
    """Create test modification objects."""
    mod1 = ModificationObject(
        modification_type="quantity_adjustment",
        reasoning="Reduces sugar for healthier cookies",
        edits=[
            ModificationEdit(
                target="ingredients",
                operation="replace",
                find="1 cup white sugar",
                replace="0.5 cup white sugar"
            )
        ]
    )

    mod2 = ModificationObject(
        modification_type="ingredient_substitution",
        reasoning="Adds more chocolate for better flavor",
        edits=[
            ModificationEdit(
                target="ingredients",
                operation="replace",
                find="2 cups semisweet chocolate chips",
                replace="3 cups semisweet chocolate chips"
            )
        ]
    )

    mod3 = ModificationObject(
        modification_type="quantity_adjustment",
        reasoning="Enhances flavor profile",
        edits=[
            ModificationEdit(
                target="ingredients",
                operation="replace",
                find="0.5 teaspoon salt",
                replace="1 teaspoon salt"
            )
        ]
    )

    return [mod1, mod2, mod3]


def create_test_reviews():
    """Create test reviews with high ratings."""
    return [
        Review(
            text="I reduced the sugar by half and they were perfect!",
            rating=5,
            username="baker_jane",
            has_modification=True
        ),
        Review(
            text="Added extra chocolate chips, delicious!",
            rating=4,
            username="choco_lover",
            has_modification=True
        ),
        Review(
            text="I used 1 tsp of salt instead of 0.5 tsp",
            rating=4,
            username="salty_dog",
            has_modification=True
        ),
    ]


def create_test_recipe():
    """Create a simple test recipe."""
    return Recipe(
        recipe_id="test_123",
        title="Test Cookies",
        ingredients=[
            "1 cup butter, softened",
            "1 cup white sugar",
            "1 cup packed brown sugar",
            "2 eggs",
            "2 teaspoons vanilla extract",
            "1 teaspoon baking soda",
            "0.5 teaspoon salt",
            "3 cups all-purpose flour",
            "2 cups semisweet chocolate chips",
        ],
        instructions=[
            "Preheat oven to 350 degrees F",
            "Mix ingredients together",
            "Bake for 10 minutes",
        ],
    )


def test_multiple_modifications_application():
    """Test that multiple modifications can be applied correctly."""
    from loguru import logger

    logger.info("=" * 60)
    logger.info("Testing Multiple Modifications Application")
    logger.info("=" * 60)

    # Create test data
    recipe = create_test_recipe()
    modifications = create_test_modifications()

    logger.info(f"\nOriginal Recipe: {recipe.title}")
    logger.info(f"Ingredients: {len(recipe.ingredients)}")
    logger.info(f"Instructions: {len(recipe.instructions)}")

    logger.info(f"\nApplying {len(modifications)} modifications...")

    # Initialize recipe modifier
    modifier = RecipeModifier()

    # Apply all modifications
    modified_recipe, all_change_records = modifier.apply_modifications_batch(
        recipe, modifications
    )

    logger.info(f"\nModified Recipe: {modified_recipe.title}")
    logger.info(f"Ingredients: {len(modified_recipe.ingredients)}")
    logger.info(f"Instructions: {len(modified_recipe.instructions)}")

    # Validate changes
    total_changes = sum(len(records) for records in all_change_records)
    logger.info(f"\nTotal changes made: {total_changes}")

    for i, change_records in enumerate(all_change_records, 1):
        logger.info(f"  Modification {i}: {len(change_records)} changes")
        for change in change_records:
            logger.info(f"    - {change.operation}: {change.from_text[:40]}... → {change.to_text[:40]}...")

    # Verify specific changes
    ingredients_str = " ".join(modified_recipe.ingredients)
    if "0.5 cup white sugar" in ingredients_str:
        logger.success("✓ Sugar reduction applied correctly")
    else:
        logger.error("✗ Sugar reduction NOT applied")
        return False

    if "3 cups semisweet chocolate chips" in ingredients_str:
        logger.success("✓ Chocolate increase applied correctly")
    else:
        logger.error("✗ Chocolate increase NOT applied")
        return False

    if "1 teaspoon salt" in ingredients_str:
        logger.success("✓ Salt increase applied correctly")
    else:
        logger.error("✗ Salt increase NOT applied")
        return False

    logger.info("=" * 60)
    return True


def test_enhanced_recipe_generation():
    """Test that enhanced recipe can be generated from multiple modifications."""
    from loguru import logger

    logger.info("\n" + "=" * 60)
    logger.info("Testing Enhanced Recipe Generation")
    logger.info("=" * 60)

    # Create test data
    original_recipe = create_test_recipe()
    modifications = create_test_modifications()
    reviews = create_test_reviews()

    # Apply modifications
    modifier = RecipeModifier()
    modified_recipe, all_change_records = modifier.apply_modifications_batch(
        original_recipe, modifications
    )

    # Create extractions (tuples of modification and source review)
    all_extractions = list(zip(modifications, reviews))

    # Generate enhanced recipe
    generator = EnhancedRecipeGenerator()
    enhanced_recipe = generator.generate_enhanced_recipe_from_multiple(
        original_recipe, modified_recipe, all_extractions, all_change_records
    )

    logger.info(f"\nEnhanced Recipe: {enhanced_recipe.title}")
    logger.info(f"Recipe ID: {enhanced_recipe.recipe_id}")
    logger.info(f"Original Recipe ID: {enhanced_recipe.original_recipe_id}")

    # Validate modifications applied
    logger.info(f"\nModifications Applied: {len(enhanced_recipe.modifications_applied)}")
    for i, mod_applied in enumerate(enhanced_recipe.modifications_applied, 1):
        logger.info(
            f"  {i}. {mod_applied.modification_type} - "
            f"{mod_applied.source_review.reviewer} ({mod_applied.source_review.rating}★) - "
            f"{len(mod_applied.changes_made)} changes"
        )
        logger.info(f"     Reasoning: {mod_applied.reasoning}")

    # Validate enhancement summary
    logger.info(f"\nEnhancement Summary:")
    logger.info(f"  Total Changes: {enhanced_recipe.enhancement_summary.total_changes}")
    logger.info(f"  Change Types: {enhanced_recipe.enhancement_summary.change_types}")
    logger.info(f"  Expected Impact: {enhanced_recipe.enhancement_summary.expected_impact}")

    # Verify counts
    if len(enhanced_recipe.modifications_applied) == 3:
        logger.success("✓ All 3 modifications recorded")
    else:
        logger.error(f"✗ Expected 3 modifications, got {len(enhanced_recipe.modifications_applied)}")
        return False

    if enhanced_recipe.enhancement_summary.total_changes == 3:
        logger.success("✓ Total changes count is correct")
    else:
        logger.error(f"✗ Expected 3 total changes, got {enhanced_recipe.enhancement_summary.total_changes}")
        return False

    if len(enhanced_recipe.enhancement_summary.change_types) == 2:
        logger.success("✓ Change types recorded correctly (quantity_adjustment, ingredient_substitution)")
    else:
        logger.error(f"✗ Expected 2 change types, got {len(enhanced_recipe.enhancement_summary.change_types)}")
        return False

    logger.info("=" * 60)
    return True


def test_method_exists():
    """Test that the new method exists and has correct signature."""
    from loguru import logger
    import inspect

    logger.info("\n" + "=" * 60)
    logger.info("Testing Method Signature")
    logger.info("=" * 60)

    generator = EnhancedRecipeGenerator()

    # Check if method exists
    if not hasattr(generator, 'generate_enhanced_recipe_from_multiple'):
        logger.error("✗ Method 'generate_enhanced_recipe_from_multiple' not found!")
        return False

    logger.success("✓ Method 'generate_enhanced_recipe_from_multiple' exists")

    # Check signature
    sig = inspect.signature(generator.generate_enhanced_recipe_from_multiple)
    params = list(sig.parameters.keys())

    logger.info(f"Parameters: {params}")

    expected_params = [
        'original_recipe', 'modified_recipe', 'all_extractions', 'all_change_records'
    ]
    if all(param in params for param in expected_params):
        logger.success("✓ Method has all expected parameters")
    else:
        logger.error(f"✗ Missing parameters. Expected: {expected_params}")
        return False

    logger.info("=" * 60)
    return True


def test_single_recipe():
    """Test the pipeline with the chocolate chip cookie recipe."""

    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable not set")
        logger.info("Please set your OpenAI API key in .env file")
        return False

    # Initialize pipeline
    try:
        pipeline = LLMAnalysisPipeline()
        logger.info("Pipeline initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        return False

    # Test with chocolate chip cookie recipe
    recipe_file = "../data/recipe_10813_best-chocolate-chip-cookies.json"
    if not Path(recipe_file).exists():
        logger.error(f"Recipe file not found: {recipe_file}")
        return False

    logger.info(f"Testing with recipe file: {recipe_file}")

    try:
        # Process the recipe
        enhanced_recipe = pipeline.process_single_recipe(
            recipe_file=recipe_file,
            save_output=True
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

    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable not set")
        logger.info("Please set your OpenAI API key in .env file")
        return False

    # Initialize pipeline
    try:
        pipeline = LLMAnalysisPipeline()
        logger.info("Pipeline initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        return False

    try:
        # Process all recipes
        enhanced_recipes = pipeline.process_recipe_directory(
            data_dir="../data"
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


def run_validation_tests():
    """Run the validation tests with mock data."""
    logger.info("Starting Validation Tests for Multiple Modifications")
    logger.info("=" * 60)

    # Test 1: Method signature
    if not test_method_exists():
        logger.error("✗ Method signature test failed")
        return False

    # Test 2: Multiple modifications application
    if not test_multiple_modifications_application():
        logger.error("✗ Multiple modifications application test failed")
        return False

    # Test 3: Enhanced recipe generation
    if not test_enhanced_recipe_generation():
        logger.error("✗ Enhanced recipe generation test failed")
        return False

    logger.success("\n✓✓✓ All validation tests passed! ✓✓✓\n")
    logger.info("The pipeline now supports:")
    logger.info("  1. Extracting all high-quality modifications (rating >= 4)")
    logger.info("  2. Applying multiple modifications in batch")
    logger.info("  3. Generating enhanced recipes with full attribution")

    return True


def main():
    """Main test function with mode selection."""

    # Parse command line argument
    if len(sys.argv) < 2:
        logger.error("Usage: python test_pipeline_updates.py [single|all|validate]")
        logger.info("  single   - Test single chocolate chip cookie recipe (generates output)")
        logger.info("  all      - Test all recipes in data directory (generates output)")
        logger.info("  validate - Run validation tests with mock data (no API calls)")
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

    elif mode == "validate":
        logger.info("Starting Validation Tests (Mock Data)")
        logger.info("=" * 60)
        success = run_validation_tests()

        logger.info("=" * 60)
        if success:
            logger.success("Validation tests passed! ✓")
        else:
            logger.error("Validation tests failed! ✗")
            sys.exit(1)

    else:
        logger.error(f"Unknown mode: {mode}")
        logger.error("Usage: python test_pipeline_updates.py [single|all|validate]")
        sys.exit(1)

    return 0


if __name__ == "__main__":
    sys.exit(main())
