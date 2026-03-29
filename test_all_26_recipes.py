#!/usr/bin/env python3
"""
Test the improved pipeline on all 26 recipes (6 existing + 20 new).
Evaluate extraction completeness and quality.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from llm_pipeline.pipeline import LLMAnalysisPipeline


def main():
    """Test pipeline on all recipes."""

    print("=" * 80)
    print("Testing Improved Pipeline on All 26 Recipes")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Initialize pipeline
    pipeline = LLMAnalysisPipeline(
        output_dir="data/enhanced_test_26",
        pipeline_version="1.3.0-test"
    )

    print(f"Model: {pipeline.tweak_extractor.model}")
    print(f"Temperature: 0.3, Max Tokens: 1500")
    print(f"Pattern Validation: Enabled")
    print()

    # Get all recipe files
    data_dir = Path("data")
    recipe_files = sorted(data_dir.glob("recipe_*.json"))

    print(f"Found {len(recipe_files)} recipe files")
    print()

    results = {
        'successful': [],
        'failed': [],
        'total_recipes': 0,
        'total_changes': 0,
        'total_reviews_processed': 0,
        'cuisines': {}
    }

    for i, recipe_file in enumerate(recipe_files, 1):
        print(f"[{i}/{len(recipe_files)}] {recipe_file.name}")

        try:
            with open(recipe_file, 'r') as f:
                recipe_data = json.load(f)

            title = recipe_data.get('title', 'Unknown')
            cuisine = recipe_data.get('cuisine', 'Unknown')

            print(f"  Title: {title}")
            print(f"  Cuisine: {cuisine}")

            # Process with pipeline
            enhanced = pipeline.process_single_recipe(str(recipe_file), save_output=True)

            if enhanced:
                changes_count = enhanced.enhancement_summary.total_changes
                review_count = len(enhanced.modifications_applied)

                results['successful'].append({
                    'file': recipe_file.name,
                    'title': title,
                    'cuisine': cuisine,
                    'changes': changes_count,
                    'reviews': review_count
                })

                results['total_changes'] += changes_count
                results['total_reviews_processed'] += review_count
                results['cuisines'][cuisine] = results['cuisines'].get(cuisine, 0) + 1

                print(f"  ✓ {changes_count} changes from {review_count} reviews")
            else:
                print(f"  ✗ No enhancements generated")
                results['failed'].append(recipe_file.name)

        except Exception as e:
            print(f"  ✗ Error: {e}")
            results['failed'].append(recipe_file.name)

        print()

    # Summary
    print("=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    print()

    print(f"Total Recipes: {len(recipe_files)}")
    print(f"✓ Successful: {len(results['successful'])}")
    print(f"✗ Failed: {len(results['failed'])}")
    print()

    if results['successful']:
        avg_changes = results['total_changes'] / len(results['successful'])
        avg_reviews = results['total_reviews_processed'] / len(results['successful'])

        print(f"Total Changes Applied: {results['total_changes']}")
        print(f"Average Changes per Recipe: {avg_changes:.1f}")
        print()
        print(f"Total Reviews Processed: {results['total_reviews_processed']}")
        print(f"Average Reviews per Recipe: {avg_reviews:.1f}")
        print()

        print("Cuisine Coverage:")
        for cuisine, count in sorted(results['cuisines'].items()):
            print(f"  • {cuisine}: {count}")

    print()
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
