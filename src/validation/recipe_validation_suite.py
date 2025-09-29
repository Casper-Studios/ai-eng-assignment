"""
Recipe Validation Suite

This module provides comprehensive recipe validation to identify why only 2/6 recipes
are being processed successfully and test the remaining 4 recipes mentioned in the PRD.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import time
from datetime import datetime


class RecipeTestResult:
    """Result of testing a single recipe."""

    def __init__(self, recipe_id: str, title: str):
        self.recipe_id = recipe_id
        self.title = title
        self.success = False
        self.error_message = None
        self.error_type = None
        self.reviews_with_modifications = 0
        self.total_reviews = 0
        self.processing_time = 0.0
        self.modifications_extracted = 0
        self.enhancement_created = False
        self.failure_stage = None  # "data_loading", "review_parsing", "extraction", "modification", "generation"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "recipe_id": self.recipe_id,
            "title": self.title,
            "success": self.success,
            "error_message": self.error_message,
            "error_type": self.error_type,
            "reviews_with_modifications": self.reviews_with_modifications,
            "total_reviews": self.total_reviews,
            "processing_time": self.processing_time,
            "modifications_extracted": self.modifications_extracted,
            "enhancement_created": self.enhancement_created,
            "failure_stage": self.failure_stage
        }


class RecipeValidationSuite:
    """Comprehensive recipe testing and validation suite."""

    def __init__(self, data_dir: str = "data", output_dir: str = "validation_results"):
        """
        Initialize the validation suite.

        Args:
            data_dir: Directory containing recipe JSON files
            output_dir: Directory to save validation results
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Expected recipes from PRD
        self.expected_recipes = [
            "best-chocolate-chip-cookies",  # ✅ working
            "creamy-sweet-potato-with-ginger-soup",  # ✅ working
            "spicy-apple-cake",  # ❓ to test
            "nikujaga-japanese-style-meat-and-potatoes",  # ❓ to test
            "spiced-purple-plum-jam",  # ❓ to test
            "mango-teriyaki-marinade"  # ❓ to test
        ]

    def discover_recipe_files(self) -> List[Path]:
        """Discover all recipe JSON files in the data directory."""
        recipe_files = list(self.data_dir.glob("enhanced_*.json"))
        print(f"Found {len(recipe_files)} recipe files:")
        for recipe_file in recipe_files:
            print(f"  - {recipe_file.name}")
        return recipe_files

    def analyze_recipe_data(self, recipe_file: Path) -> RecipeTestResult:
        """
        Analyze a recipe file to understand its structure and potential issues.

        Args:
            recipe_file: Path to recipe JSON file

        Returns:
            RecipeTestResult with analysis results
        """
        print(f"\n🔍 Analyzing {recipe_file.name}")

        # Extract recipe ID and title from filename
        filename = recipe_file.stem
        parts = filename.split('_', 2)
        recipe_id = parts[1] if len(parts) > 1 else "unknown"
        title_part = parts[2] if len(parts) > 2 else "unknown"

        result = RecipeTestResult(recipe_id, title_part)

        try:
            # Load recipe data
            with open(recipe_file, 'r', encoding='utf-8') as f:
                recipe_data = json.load(f)

            print(f"  ✅ File loaded successfully")

            # Analyze basic structure
            title = recipe_data.get('title', 'No title')
            ingredients = recipe_data.get('ingredients', [])
            instructions = recipe_data.get('instructions', [])
            reviews = recipe_data.get('reviews', [])

            result.title = title
            result.total_reviews = len(reviews)

            print(f"  📝 Title: {title}")
            print(f"  🥄 Ingredients: {len(ingredients)}")
            print(f"  📋 Instructions: {len(instructions)}")
            print(f"  💬 Reviews: {len(reviews)}")

            # Check for basic required fields
            if not ingredients:
                result.error_message = "No ingredients found"
                result.error_type = "missing_ingredients"
                result.failure_stage = "data_loading"
                print(f"  ❌ No ingredients found")
                return result

            if not instructions:
                result.error_message = "No instructions found"
                result.error_type = "missing_instructions"
                result.failure_stage = "data_loading"
                print(f"  ❌ No instructions found")
                return result

            # Analyze reviews for modifications
            reviews_with_mods = 0
            review_issues = []

            for i, review in enumerate(reviews):
                if not isinstance(review, dict):
                    review_issues.append(f"Review {i+1}: Not a dictionary")
                    continue

                if not review.get('text'):
                    review_issues.append(f"Review {i+1}: No text field")
                    continue

                # Check for modification flag
                has_modification = review.get('has_modification', False)
                if has_modification:
                    reviews_with_mods += 1

            result.reviews_with_modifications = reviews_with_mods

            print(f"  🔧 Reviews with modifications: {reviews_with_mods}")

            if review_issues:
                print(f"  ⚠️  Review issues found:")
                for issue in review_issues[:3]:  # Show first 3 issues
                    print(f"     - {issue}")

            if reviews_with_mods == 0:
                result.error_message = "No reviews marked with modifications"
                result.error_type = "no_modifications"
                result.failure_stage = "review_parsing"
                print(f"  ❌ No reviews with modifications found")
                return result

            # If we get here, basic structure looks good
            result.success = True
            print(f"  ✅ Recipe structure is valid")

        except json.JSONDecodeError as e:
            result.error_message = f"Invalid JSON: {e}"
            result.error_type = "json_error"
            result.failure_stage = "data_loading"
            print(f"  ❌ JSON decode error: {e}")

        except FileNotFoundError:
            result.error_message = "File not found"
            result.error_type = "file_not_found"
            result.failure_stage = "data_loading"
            print(f"  ❌ File not found")

        except Exception as e:
            result.error_message = f"Unexpected error: {e}"
            result.error_type = "unexpected_error"
            result.failure_stage = "data_loading"
            print(f"  ❌ Unexpected error: {e}")

        return result

    def test_recipe_processing_simulation(self, recipe_file: Path) -> RecipeTestResult:
        """
        Simulate recipe processing to identify potential issues without API calls.

        Args:
            recipe_file: Path to recipe JSON file

        Returns:
            RecipeTestResult with simulation results
        """
        result = self.analyze_recipe_data(recipe_file)

        if not result.success:
            return result

        print(f"  🧪 Simulating pipeline processing...")

        try:
            # Load the data again for processing simulation
            with open(recipe_file, 'r', encoding='utf-8') as f:
                recipe_data = json.load(f)

            # Simulate review selection
            reviews = recipe_data.get('reviews', [])
            modification_reviews = [r for r in reviews if r.get('has_modification', False)]

            if not modification_reviews:
                result.error_message = "No modification reviews available for selection"
                result.error_type = "no_modification_reviews"
                result.failure_stage = "extraction"
                result.success = False
                return result

            # Simulate random review selection
            import random
            selected_review = random.choice(modification_reviews)
            review_text = selected_review.get('text', '')

            print(f"  📝 Selected review: {review_text[:80]}...")

            # Check review quality
            if len(review_text.strip()) < 10:
                result.error_message = "Selected review too short"
                result.error_type = "poor_review_quality"
                result.failure_stage = "extraction"
                result.success = False
                return result

            # Simulate extraction (without API call)
            # Look for modification indicators
            modification_indicators = [
                'added', 'used', 'substituted', 'replaced', 'changed',
                'increased', 'decreased', 'doubled', 'halved', 'omitted',
                'instead of', 'rather than', 'in place of'
            ]

            text_lower = review_text.lower()
            found_indicators = [ind for ind in modification_indicators if ind in text_lower]

            if not found_indicators:
                result.error_message = "Review doesn't contain clear modification indicators"
                result.error_type = "unclear_modifications"
                result.failure_stage = "extraction"
                result.success = False
                print(f"  ❌ No clear modification indicators found")
                return result

            print(f"  ✅ Found modification indicators: {found_indicators[:3]}")

            # Simulate successful processing
            result.modifications_extracted = len(found_indicators)
            result.enhancement_created = True
            result.success = True

            print(f"  ✅ Processing simulation successful")

        except Exception as e:
            result.error_message = f"Processing simulation failed: {e}"
            result.error_type = "simulation_error"
            result.failure_stage = "extraction"
            result.success = False
            print(f"  ❌ Processing simulation failed: {e}")

        return result

    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """
        Run comprehensive validation on all recipe files.

        Returns:
            Validation results summary
        """
        print("🚀 Starting Comprehensive Recipe Validation")
        print("=" * 60)

        recipe_files = self.discover_recipe_files()
        results = []

        # Test each recipe file
        for recipe_file in recipe_files:
            start_time = time.time()
            result = self.test_recipe_processing_simulation(recipe_file)
            result.processing_time = time.time() - start_time
            results.append(result)

        # Generate summary
        total_recipes = len(results)
        successful_recipes = sum(1 for r in results if r.success)
        failed_recipes = total_recipes - successful_recipes

        # Analyze failure patterns
        failure_stages = {}
        error_types = {}

        for result in results:
            if not result.success:
                stage = result.failure_stage or "unknown"
                error_type = result.error_type or "unknown"

                failure_stages[stage] = failure_stages.get(stage, 0) + 1
                error_types[error_type] = error_types.get(error_type, 0) + 1

        # Create summary
        summary = {
            "validation_timestamp": datetime.now().isoformat(),
            "total_recipes": total_recipes,
            "successful_recipes": successful_recipes,
            "failed_recipes": failed_recipes,
            "success_rate": successful_recipes / total_recipes if total_recipes > 0 else 0,
            "target_success_rate": 0.8,  # 80% from PRD
            "meets_target": (successful_recipes / total_recipes) >= 0.8 if total_recipes > 0 else False,
            "failure_analysis": {
                "failure_stages": failure_stages,
                "error_types": error_types
            },
            "recipe_results": [r.to_dict() for r in results]
        }

        # Print summary
        print("\n📊 VALIDATION RESULTS SUMMARY")
        print("=" * 60)
        print(f"Total Recipes: {total_recipes}")
        print(f"Successful: {successful_recipes} ({successful_recipes/total_recipes:.1%})")
        print(f"Failed: {failed_recipes}")
        print(f"Success Rate: {successful_recipes/total_recipes:.1%}")
        print(f"Target: 80% (PRD requirement)")
        print(f"Meets Target: {'✅ YES' if summary['meets_target'] else '❌ NO'}")

        print(f"\n🔍 FAILURE ANALYSIS")
        print("-" * 30)
        print("Failure Stages:")
        for stage, count in failure_stages.items():
            print(f"  {stage}: {count}")

        print("Error Types:")
        for error_type, count in error_types.items():
            print(f"  {error_type}: {count}")

        # Show specific failures
        print(f"\n❌ FAILED RECIPES")
        print("-" * 30)
        for result in results:
            if not result.success:
                print(f"{result.title}: {result.error_message}")

        # Show successful recipes
        print(f"\n✅ SUCCESSFUL RECIPES")
        print("-" * 30)
        for result in results:
            if result.success:
                print(f"{result.title} ({result.reviews_with_modifications} modification reviews)")

        # Save results
        self.save_validation_results(summary)

        return summary

    def save_validation_results(self, summary: Dict[str, Any]):
        """Save validation results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"recipe_validation_results_{timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Results saved to: {output_file}")

    def generate_improvement_recommendations(self, summary: Dict[str, Any]) -> List[str]:
        """Generate specific recommendations based on validation results."""
        recommendations = []

        failure_stages = summary.get("failure_analysis", {}).get("failure_stages", {})
        error_types = summary.get("failure_analysis", {}).get("error_types", {})

        if "data_loading" in failure_stages:
            recommendations.append("Fix data structure issues in recipe JSON files")

        if "review_parsing" in failure_stages or "no_modifications" in error_types:
            recommendations.append("Improve review modification detection and flagging")

        if "extraction" in failure_stages:
            recommendations.append("Enhance modification extraction prompts and methods")

        if summary.get("success_rate", 0) < 0.8:
            recommendations.append("Overall success rate below 80% target - comprehensive pipeline review needed")

        if not recommendations:
            recommendations.append("Validation passed - pipeline meets quality standards")

        return recommendations


def main():
    """Main function to run recipe validation."""
    print("Recipe Validation Suite")
    print("Identifying why only 2/6 recipes are working")

    # Initialize validation suite
    validator = RecipeValidationSuite()

    # Run comprehensive validation
    summary = validator.run_comprehensive_validation()

    # Generate recommendations
    recommendations = validator.generate_improvement_recommendations(summary)

    print(f"\n💡 IMPROVEMENT RECOMMENDATIONS")
    print("-" * 40)
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")

    print(f"\n🎯 NEXT STEPS")
    print("-" * 20)
    if summary.get("meets_target", False):
        print("✅ Recipe validation passed! Pipeline meets 80% success rate target.")
        print("   Continue with accuracy validation and quality assurance.")
    else:
        print("❌ Recipe validation failed. Address the issues above before proceeding.")
        print("   Focus on improving data quality and extraction methods.")


if __name__ == "__main__":
    main()