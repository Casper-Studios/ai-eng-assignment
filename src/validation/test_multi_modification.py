"""
Test Script for Multi-Modification Extraction Validation

This script tests the enhanced multi-modification extraction system against
carefully curated ground truth data to validate completeness and accuracy.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger
from dotenv import load_dotenv

from validation.multi_modification_extractor import MultiModificationExtractor
from validation.modification_validator import ModificationValidator
from validation.test_dataset import TestDatasetBuilder


def setup_logging():
    """Configure logging for the test."""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}"
    )
    logger.add(
        "validation_results/test_multi_modification.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} | {message}",
        rotation="10 MB"
    )


def run_multi_modification_tests():
    """Run comprehensive multi-modification extraction tests."""

    logger.info("🚀 Starting Multi-Modification Extraction Validation")
    logger.info("=" * 60)

    # Load environment
    load_dotenv()

    # Initialize components
    extractor = MultiModificationExtractor()
    validator = ModificationValidator()
    dataset_builder = TestDatasetBuilder()

    # Get test dataset
    test_dataset = dataset_builder.get_complete_test_dataset()
    dataset_stats = dataset_builder.get_dataset_statistics()

    logger.info(f"📊 Test Dataset Statistics:")
    logger.info(f"   Total test cases: {dataset_stats['total_test_cases']}")
    logger.info(f"   Total expected modifications: {dataset_stats['total_expected_modifications']}")
    logger.info(f"   Average mods per case: {dataset_stats['average_modifications_per_case']:.1f}")
    logger.info(f"   Difficulty distribution: {dataset_stats['difficulty_distribution']}")
    logger.info(f"   Modification count distribution: {dataset_stats['modification_count_distribution']}")
    logger.info("")

    # Run individual test cases
    logger.info("🔍 Running Individual Test Cases")
    logger.info("-" * 40)

    results = []
    total_completeness = 0.0
    total_quality = 0.0

    for i, test_case in enumerate(test_dataset, 1):
        logger.info(f"Test {i:2d}/{len(test_dataset)}: {test_case.id}")
        logger.info(f"         Review: {test_case.review_text[:80]}...")
        logger.info(f"         Expected: {test_case.expected_count} modifications")

        try:
            # Test the multi-modification extractor
            result = test_single_case(extractor, validator, test_case)
            results.append(result)

            total_completeness += result.get('completeness_score', 0)
            total_quality += result.get('quality_score', 0)

            # Log result
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            logger.info(f"         Result: {status} (Completeness: {result.get('completeness_score', 0):.2f}, Quality: {result.get('quality_score', 0):.2f})")

            if result.get('notes'):
                for note in result['notes'][:2]:  # Show first 2 notes
                    logger.info(f"         Note: {note}")

        except Exception as e:
            logger.error(f"         ERROR: {e}")
            results.append({
                'test_id': test_case.id,
                'passed': False,
                'error': str(e),
                'completeness_score': 0.0,
                'quality_score': 0.0
            })

        logger.info("")

    # Calculate overall metrics
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r.get('passed', False))
    avg_completeness = total_completeness / total_tests if total_tests > 0 else 0
    avg_quality = total_quality / total_tests if total_tests > 0 else 0

    # Generate summary report
    logger.info("📈 FINAL RESULTS SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total Tests Run: {total_tests}")
    logger.info(f"Tests Passed: {passed_tests} ({passed_tests/total_tests:.1%})")
    logger.info(f"Tests Failed: {total_tests - passed_tests}")
    logger.info(f"Average Completeness Score: {avg_completeness:.3f} ({avg_completeness:.1%})")
    logger.info(f"Average Quality Score: {avg_quality:.3f} ({avg_quality:.1%})")
    logger.info("")

    # Success criteria check (from PRD)
    completeness_target = 0.95  # 95% completeness target
    quality_target = 0.80       # 80% quality target
    pass_rate_target = 0.90     # 90% pass rate target

    logger.info("🎯 SUCCESS CRITERIA ASSESSMENT")
    logger.info("-" * 40)

    criteria_met = 0
    total_criteria = 3

    if avg_completeness >= completeness_target:
        logger.info(f"✅ Completeness: {avg_completeness:.1%} >= {completeness_target:.1%} (TARGET MET)")
        criteria_met += 1
    else:
        logger.info(f"❌ Completeness: {avg_completeness:.1%} < {completeness_target:.1%} (TARGET MISSED)")

    if avg_quality >= quality_target:
        logger.info(f"✅ Quality: {avg_quality:.1%} >= {quality_target:.1%} (TARGET MET)")
        criteria_met += 1
    else:
        logger.info(f"❌ Quality: {avg_quality:.1%} < {quality_target:.1%} (TARGET MISSED)")

    pass_rate = passed_tests / total_tests if total_tests > 0 else 0
    if pass_rate >= pass_rate_target:
        logger.info(f"✅ Pass Rate: {pass_rate:.1%} >= {pass_rate_target:.1%} (TARGET MET)")
        criteria_met += 1
    else:
        logger.info(f"❌ Pass Rate: {pass_rate:.1%} < {pass_rate_target:.1%} (TARGET MISSED)")

    logger.info("")
    logger.info(f"OVERALL: {criteria_met}/{total_criteria} success criteria met")

    if criteria_met == total_criteria:
        logger.info("🎉 ALL SUCCESS CRITERIA MET! Multi-modification extraction is validated.")
    else:
        logger.info("⚠️  Some success criteria not met. Further improvements needed.")

    # Save detailed results
    save_test_results(results, dataset_stats, {
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'pass_rate': pass_rate,
        'avg_completeness': avg_completeness,
        'avg_quality': avg_quality,
        'criteria_met': criteria_met,
        'total_criteria': total_criteria
    })

    return results


def test_single_case(extractor, validator, test_case) -> Dict[str, Any]:
    """Test a single case and return detailed results."""

    from llm_pipeline.models import Review, Recipe

    # Create review and recipe objects
    review = Review(text=test_case.review_text, has_modification=True)
    recipe = Recipe(
        recipe_id=test_case.id,
        title=test_case.recipe_data.get("title", "Test Recipe"),
        ingredients=test_case.recipe_data.get("ingredients", []),
        instructions=test_case.recipe_data.get("instructions", [])
    )

    # Extract modifications
    modifications, llm_reported_count = extractor.extract_all_modifications(review, recipe)

    # Validate completeness
    completeness_result = validator.validate_completeness(
        test_case.review_text,
        modifications,
        test_case.expected_count,
        test_case.expected_modifications
    )

    # Validate quality
    quality_result = validator.validate_extraction_quality(modifications, recipe)

    # Compare against expected
    if test_case.expected_modifications:
        accuracy_score = validator.compare_extracted_vs_expected(
            test_case.expected_modifications,
            modifications
        )
    else:
        accuracy_score = 1.0 if len(modifications) == 0 else 0.0

    # Determine overall pass/fail
    completeness_pass = completeness_result.score >= 0.8
    quality_pass = quality_result.score >= 0.7
    accuracy_pass = accuracy_score >= 0.7

    overall_pass = completeness_pass and quality_pass and accuracy_pass

    # Collect notes
    notes = []
    notes.extend(completeness_result.notes)
    notes.extend(quality_result.notes)

    if test_case.expected_count > 0 and len(modifications) == 0:
        notes.append("No modifications extracted despite expected modifications")
    elif len(modifications) > test_case.expected_count * 1.5:
        notes.append("Significantly more modifications extracted than expected")

    return {
        'test_id': test_case.id,
        'difficulty': test_case.difficulty_level,
        'expected_count': test_case.expected_count,
        'extracted_count': len(modifications),
        'llm_reported_count': llm_reported_count,
        'completeness_score': completeness_result.score,
        'quality_score': quality_result.score,
        'accuracy_score': accuracy_score,
        'completeness_pass': completeness_pass,
        'quality_pass': quality_pass,
        'accuracy_pass': accuracy_pass,
        'passed': overall_pass,
        'extracted_types': [mod.modification_type for mod in modifications],
        'notes': notes,
        'review_text': test_case.review_text,
        'modifications_detail': [
            {
                'type': mod.modification_type,
                'reasoning': mod.reasoning,
                'edits_count': len(mod.edits)
            }
            for mod in modifications
        ]
    }


def save_test_results(results, dataset_stats, summary):
    """Save test results to JSON files."""

    output_dir = Path("validation_results")
    output_dir.mkdir(exist_ok=True)

    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save detailed results
    detailed_file = output_dir / f"multi_modification_test_results_{timestamp}.json"
    with open(detailed_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'dataset_statistics': dataset_stats,
            'summary': summary,
            'detailed_results': results
        }, f, indent=2, ensure_ascii=False)

    # Save summary report
    summary_file = output_dir / f"multi_modification_summary_{timestamp}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'summary': summary,
            'dataset_stats': dataset_stats
        }, f, indent=2, ensure_ascii=False)

    logger.info(f"💾 Results saved to {detailed_file}")
    logger.info(f"💾 Summary saved to {summary_file}")


if __name__ == "__main__":
    # Ensure output directory exists
    Path("validation_results").mkdir(exist_ok=True)

    # Setup logging
    setup_logging()

    # Run the tests
    try:
        results = run_multi_modification_tests()
        logger.info("✅ Multi-modification validation test completed successfully")
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)