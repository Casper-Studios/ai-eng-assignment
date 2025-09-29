"""
Simple Multi-Modification Test

A simplified test that works without external dependencies to validate
the multi-modification extraction system.
"""

import os
import sys
import json
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from validation.multi_modification_extractor import MultiModificationExtractor
from validation.test_dataset import TestDatasetBuilder
from llm_pipeline.models import Review, Recipe


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def print_subheader(title):
    """Print a formatted subheader."""
    print("\n" + "-" * 40)
    print(title)
    print("-" * 40)


def test_multi_modification_extraction():
    """Test multi-modification extraction with simple test cases."""

    print_header("Multi-Modification Extraction Test")

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment")
        print("Please set your OpenAI API key and try again")
        return False

    print("✅ OpenAI API key found")

    # Initialize extractor
    try:
        extractor = MultiModificationExtractor()
        print("✅ MultiModificationExtractor initialized")
    except Exception as e:
        print(f"❌ Failed to initialize extractor: {e}")
        return False

    # Get test dataset
    dataset_builder = TestDatasetBuilder()
    test_cases = dataset_builder.build_multi_modification_test_dataset()

    print(f"✅ Test dataset loaded: {len(test_cases)} test cases")

    # Run a few sample tests
    sample_tests = test_cases[:5]  # Test first 5 cases

    results = []

    for i, test_case in enumerate(sample_tests, 1):
        print_subheader(f"Test Case {i}: {test_case.id}")
        print(f"Review: {test_case.review_text[:100]}...")
        print(f"Expected modifications: {test_case.expected_count}")

        # Create review and recipe objects
        review = Review(text=test_case.review_text, has_modification=True)
        recipe = Recipe(
            recipe_id=test_case.id,
            title=test_case.recipe_data.get("title", "Test Recipe"),
            ingredients=test_case.recipe_data.get("ingredients", []),
            instructions=test_case.recipe_data.get("instructions", [])
        )

        try:
            # Extract modifications
            modifications, llm_reported_count = extractor.extract_all_modifications(review, recipe)

            extracted_count = len(modifications)
            print(f"LLM reported: {llm_reported_count} modifications")
            print(f"Actually extracted: {extracted_count} modifications")

            # Show extracted modifications
            if modifications:
                print("Extracted modifications:")
                for j, mod in enumerate(modifications, 1):
                    print(f"  {j}. Type: {mod.modification_type}")
                    print(f"     Reasoning: {mod.reasoning[:50]}...")
                    print(f"     Edits: {len(mod.edits)}")
            else:
                print("No modifications extracted")

            # Assess result
            completeness = min(extracted_count / test_case.expected_count, 1.0) if test_case.expected_count > 0 else 1.0
            passed = completeness >= 0.8 and extracted_count > 0

            print(f"Completeness: {completeness:.2f} ({completeness:.1%})")
            print(f"Result: {'✅ PASS' if passed else '❌ FAIL'}")

            results.append({
                'test_id': test_case.id,
                'expected': test_case.expected_count,
                'extracted': extracted_count,
                'completeness': completeness,
                'passed': passed
            })

        except Exception as e:
            print(f"❌ Error during extraction: {e}")
            results.append({
                'test_id': test_case.id,
                'expected': test_case.expected_count,
                'extracted': 0,
                'completeness': 0.0,
                'passed': False,
                'error': str(e)
            })

    # Summary
    print_header("Test Results Summary")
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r.get('passed', False))
    avg_completeness = sum(r.get('completeness', 0) for r in results) / total_tests if total_tests > 0 else 0

    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Pass rate: {passed_tests/total_tests:.1%}")
    print(f"Average completeness: {avg_completeness:.1%}")

    # Save results
    output_dir = Path("validation_results")
    output_dir.mkdir(exist_ok=True)

    results_file = output_dir / "simple_test_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'pass_rate': passed_tests/total_tests if total_tests > 0 else 0,
                'average_completeness': avg_completeness
            },
            'results': results
        }, f, indent=2)

    print(f"Results saved to: {results_file}")

    return passed_tests > 0


def test_heuristic_counting():
    """Test the heuristic modification counting."""

    print_header("Heuristic Modification Counting Test")

    extractor = MultiModificationExtractor()

    test_reviews = [
        ("I added an egg and doubled the vanilla", 2),
        ("I used brown sugar instead of white, added nuts, and baked at 350°F", 3),
        ("I halved the sugar", 1),
        ("Perfect recipe as written", 1),
        ("I substituted almond flour for regular flour, used coconut oil instead of butter, and replaced eggs with flax eggs", 3)
    ]

    print("Testing heuristic modification counting:")

    for review_text, expected in test_reviews:
        estimated = extractor.count_discrete_modifications_heuristic(review_text)
        print(f"\nReview: {review_text}")
        print(f"Expected: {expected}, Estimated: {estimated}")
        print(f"Accuracy: {'✅' if estimated == expected else '❌'}")


if __name__ == "__main__":
    print("Starting Multi-Modification Validation Tests")

    # Test heuristic counting first
    test_heuristic_counting()

    # Test actual extraction
    success = test_multi_modification_extraction()

    if success:
        print("\n🎉 Multi-modification testing completed successfully!")
    else:
        print("\n❌ Multi-modification testing failed!")
        sys.exit(1)