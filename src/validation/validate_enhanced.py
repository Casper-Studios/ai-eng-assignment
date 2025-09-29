"""
Validate Enhanced Dataset

Simple script to validate the enhanced dataset created by the
enhanced extraction pipeline.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from validation.recipe_validation_suite import RecipeValidationSuite


def main():
    """Main function to validate enhanced dataset."""
    print("Validating Enhanced Dataset")
    print("Testing recipes with improvements applied")
    print("=" * 60)

    # Check if enhanced data exists
    enhanced_dir = Path("data/enhanced")
    if not enhanced_dir.exists():
        print(f"❌ Enhanced data directory not found: {enhanced_dir}")
        print("Please run enhanced_extraction_pipeline.py first")
        return

    # Initialize validator with enhanced data
    validator = RecipeValidationSuite(data_dir=str(enhanced_dir))

    # Run validation
    results = validator.run_comprehensive_validation()

    # Show comparison
    print(f"\n📈 IMPROVEMENT COMPARISON")
    print("=" * 40)
    print(f"Original success rate: 50.0% (3/6)")
    print(f"Enhanced success rate: {results['success_rate']:.1%} ({results['successful_recipes']}/{results['total_recipes']})")
    print(f"Improvement: {results['success_rate'] - 0.5:+.1%}")
    print(f"Meets 80% target: {'✅ YES' if results['success_rate'] >= 0.8 else '❌ NO'}")

    if results['success_rate'] >= 0.8:
        print("\n🎉 VALIDATION PASSED!")
        print("Recipe coverage now meets the 80% success rate requirement from PRD.")
        print("Ready to proceed with accuracy validation and quality assurance.")
    else:
        print("\n⚠️ Still below 80% target. Additional improvements needed.")


if __name__ == "__main__":
    main()