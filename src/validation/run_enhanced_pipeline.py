"""
Simplified Enhanced Pipeline Runner

Run the enhanced extraction pipeline without the import issues.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from validation.enhanced_extraction_pipeline import EnhancedExtractionPipeline
from validation.recipe_validation_suite import RecipeValidationSuite


def main():
    """Run enhanced extraction pipeline and validation."""
    print("🚀 Running Enhanced Extraction Pipeline")
    print("=" * 60)

    # Initialize enhanced pipeline
    pipeline = EnhancedExtractionPipeline()

    # Create enhanced dataset
    enhancement_results = pipeline.create_enhanced_dataset()

    # Validate enhanced dataset manually
    print(f"\n🔍 Validating Enhanced Dataset")
    print("=" * 40)

    # Initialize validator with enhanced data directory (from root)
    validator = RecipeValidationSuite(data_dir="../../data/enhanced")

    # Run validation
    validation_results = validator.run_comprehensive_validation()

    print(f"\n🎯 FINAL ASSESSMENT")
    print("=" * 30)

    original_success_rate = 0.333  # 2/6 from actual analysis
    enhanced_success_rate = validation_results.get("success_rate", 0)

    print(f"Original success rate: {original_success_rate:.1%}")
    print(f"Enhanced success rate: {enhanced_success_rate:.1%}")
    print(f"Improvement: {enhanced_success_rate - original_success_rate:+.1%}")
    print(f"Meets 80% target: {'✅ YES' if enhanced_success_rate >= 0.8 else '❌ NO'}")

    if enhanced_success_rate >= 0.8:
        print("\n🎉 SUCCESS! Enhanced pipeline meets the 80% success rate requirement.")
        print("   This demonstrates the potential of the validation framework improvements.")
    else:
        print("\n⚠️  Still below target. Additional improvements needed.")

    return enhancement_results, validation_results


if __name__ == "__main__":
    main()