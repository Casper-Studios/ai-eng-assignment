#!/usr/bin/env python3
"""
Evaluate Enhanced Recipes Against Source Reviews

This script analyzes the enhanced recipes in src/data/enhanced/ to:
1. Compare applied modifications to their source reviews
2. Check if quality filtering is working correctly
3. Identify any missing modifications or inconsistencies
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List


def load_enhanced_recipe(file_path: str) -> Dict[str, Any]:
    """Load enhanced recipe from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_source_recipe(recipe_id: str, data_dir: str) -> Dict[str, Any]:
    """Find the original source recipe file."""
    # Remove '_enhanced' suffix if present
    original_id = recipe_id.replace('_enhanced', '')

    # Search for the source file in multiple locations
    search_paths = [
        Path(data_dir),
        Path('data'),
        Path('src/data'),
    ]

    for search_path in search_paths:
        for pattern in [f"recipe_{original_id}*.json", f"{original_id}*.json"]:
            matches = list(search_path.glob(pattern))
            if matches:
                with open(matches[0], 'r', encoding='utf-8') as f:
                    return json.load(f)

    return None


def analyze_modification_accuracy(
    source_review: Dict[str, Any],
    applied_modification: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Analyze if the applied modification accurately reflects the source review.

    Returns dict with:
    - is_accurate: bool
    - issues: list of str
    - missing_changes: list of str
    - extra_changes: list of str
    """
    issues = []
    missing_changes = []
    extra_changes = []

    review_text = source_review.get('text', '').lower()
    changes_made = applied_modification.get('changes_made', [])

    # Check for common patterns in reviews
    patterns = {
        'sugar reduction': ['less sugar', 'reduce sugar', 'half sugar', 'decrease sugar'],
        'sugar increase': ['more sugar', 'extra sugar', 'additional sugar'],
        'flour reduction': ['less flour', 'reduce flour', 'half flour'],
        'spice increase': ['more spice', 'extra spice', 'cayenne', 'cinnamon', 'nutmeg'],
        'egg yolk': ['egg yolk', 'yolk'],
        'ginger fresh': ['fresh ginger', 'grated ginger'],
        'milk substitution': ['2% milk', 'skim milk', 'whole milk', 'heavy cream'],
        'broth adjustment': ['more broth', 'less broth', 'extra broth'],
    }

    # Check what changes were mentioned in the review
    mentioned_changes = []
    for category, keywords in patterns.items():
        if any(keyword in review_text for keyword in keywords):
            mentioned_changes.append(category)

    # Check what changes were actually applied
    applied_changes = []
    for change in changes_made:
        change_text = change.get('to_text', '').lower()
        for category, keywords in patterns.items():
            if any(keyword in change_text for keyword in keywords):
                applied_changes.append(category)

    # Compare mentioned vs applied
    for mentioned in mentioned_changes:
        if mentioned not in applied_changes:
            missing_changes.append(mentioned)

    for applied in applied_changes:
        if applied not in mentioned_changes:
            extra_changes.append(applied)

    # Check for operation consistency
    for change in changes_made:
        from_text = change.get('from_text', '')
        to_text = change.get('to_text', '')
        operation = change.get('operation', '')

        if operation == 'replace' and not from_text:
            issues.append(f"Replace operation missing from_text: {to_text}")

        if operation == 'add' and from_text:
            issues.append(f"Add operation has from_text (should be empty): {from_text}")

    is_accurate = len(missing_changes) == 0 and len(extra_changes) == 0 and len(issues) == 0

    return {
        'is_accurate': is_accurate,
        'issues': issues,
        'missing_changes': missing_changes,
        'extra_changes': extra_changes,
        'mentioned_changes': mentioned_changes,
        'applied_changes': applied_changes
    }


def evaluate_quality_filtering(
    modifications: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Evaluate if quality filtering is working correctly.
    """
    ratings = []
    quality_scores = []

    for mod in modifications:
        source_review = mod.get('source_review', {})
        rating = source_review.get('rating')
        if rating:
            ratings.append(rating)

        # We can't directly see quality scores in the output, but we can infer
        # from the rating and text length
        text = source_review.get('text', '')
        if text:
            # Rough quality estimate
            has_specifics = any(char.isdigit() for char in text)
            is_long = len(text) > 100
            quality_estimate = (rating or 0) / 5.0
            if has_specifics:
                quality_estimate += 0.1
            if is_long:
                quality_estimate += 0.05
            quality_scores.append(min(quality_estimate, 1.0))

    return {
        'rating_distribution': {
            'min': min(ratings) if ratings else 0,
            'max': max(ratings) if ratings else 0,
            'avg': sum(ratings) / len(ratings) if ratings else 0
        },
        'estimated_quality_scores': {
            'min': min(quality_scores) if quality_scores else 0,
            'max': max(quality_scores) if quality_scores else 0,
            'avg': sum(quality_scores) / len(quality_scores) if quality_scores else 0
        },
        'all_high_rated': all(r >= 4 for r in ratings),
        'total_modifications': len(modifications)
    }


def check_completeness(
    enhanced_recipe: Dict[str, Any],
    source_recipe: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Check if all important modifications from high-rated reviews were applied.
    """
    source_reviews = source_recipe.get('reviews', [])

    # Find high-rated reviews with modifications
    high_quality_reviews = [
        r for r in source_reviews
        if r.get('rating', 0) >= 4 and r.get('has_modification', False)
    ]

    applied_count = len(enhanced_recipe.get('modifications_applied', []))

    return {
        'total_high_quality_reviews': len(high_quality_reviews),
        'modifications_applied': applied_count,
        'coverage_ratio': applied_count / len(high_quality_reviews) if high_quality_reviews else 0,
        'missing_modifications': len(high_quality_reviews) - applied_count
    }


def evaluate_enhanced_recipe(file_path: str) -> Dict[str, Any]:
    """Comprehensive evaluation of a single enhanced recipe."""
    print(f"\n{'='*80}")
    print(f"Evaluating: {Path(file_path).name}")
    print(f"{'='*80}")

    # Load enhanced recipe
    enhanced = load_enhanced_recipe(file_path)

    recipe_id = enhanced.get('recipe_id', 'unknown')
    title = enhanced.get('title', 'Unknown')
    modifications = enhanced.get('modifications_applied', [])

    print(f"\nRecipe ID: {recipe_id}")
    print(f"Title: {title}")
    print(f"Total modifications applied: {len(modifications)}")

    # Try to find source recipe
    source_recipe = find_source_recipe(recipe_id, 'data')

    evaluation_results = {
        'recipe_id': recipe_id,
        'title': title,
        'modifications_count': len(modifications),
        'modification_analysis': [],
        'quality_filtering': evaluate_quality_filtering(modifications),
        'completeness': None,
        'issues': []
    }

    # Analyze each modification
    print(f"\n{'─'*80}")
    print("Modification Analysis:")
    print(f"{'─'*80}")

    for i, mod in enumerate(modifications, 1):
        source_review = mod.get('source_review', {})
        print(f"\n{i}. Rating: {source_review.get('rating', 'N/A')}★")
        print(f"   Review: {source_review.get('text', 'No text')[:100]}...")

        analysis = analyze_modification_accuracy(source_review, mod)
        evaluation_results['modification_analysis'].append(analysis)

        if analysis['is_accurate']:
            print("   ✓ Accurately applied")
        else:
            print("   ✗ Issues found:")
            if analysis['missing_changes']:
                print(f"     Missing: {', '.join(analysis['missing_changes'])}")
            if analysis['extra_changes']:
                print(f"     Extra: {', '.join(analysis['extra_changes'])}")
            if analysis['issues']:
                print(f"     Technical: {', '.join(analysis['issues'])}")

    # Quality filtering analysis
    print(f"\n{'─'*80}")
    print("Quality Filtering Analysis:")
    print(f"{'─'*80}")

    quality = evaluation_results['quality_filtering']
    print(f"Rating distribution: min={quality['rating_distribution']['min']:.1f}, "
          f"max={quality['rating_distribution']['max']:.1f}, "
          f"avg={quality['rating_distribution']['avg']:.1f}")
    print(f"All high-rated (≥4★): {quality['all_high_rated']}")

    if not quality['all_high_rated']:
        evaluation_results['issues'].append(
            "Low-rated reviews may have been included in modifications"
        )

    # Completeness check if we have source data
    if source_recipe:
        completeness = check_completeness(enhanced, source_recipe)
        evaluation_results['completeness'] = completeness

        print(f"\n{'─'*80}")
        print("Completeness Analysis:")
        print(f"{'─'*80}")
        print(f"High-quality source reviews: {completeness['total_high_quality_reviews']}")
        print(f"Modifications applied: {completeness['modifications_applied']}")
        print(f"Coverage ratio: {completeness['coverage_ratio']:.1%}")

        if completeness['missing_modifications'] > 0:
            evaluation_results['issues'].append(
                f"{completeness['missing_modifications']} high-quality modifications may be missing"
            )

    # Summary
    print(f"\n{'─'*80}")
    print("Summary:")
    print(f"{'─'*80}")

    accurate_count = sum(1 for a in evaluation_results['modification_analysis'] if a['is_accurate'])
    print(f"Accurate modifications: {accurate_count}/{len(modifications)}")

    if evaluation_results['issues']:
        print(f"\n⚠ Issues found:")
        for issue in evaluation_results['issues']:
            print(f"  • {issue}")
    else:
        print(f"\n✓ No major issues detected")

    return evaluation_results


def main():
    """Evaluate all enhanced recipes."""
    print("="*80)
    print("Enhanced Recipe Evaluation")
    print("="*80)

    # Check multiple possible locations
    enhanced_dirs = [Path('data/enhanced'), Path('src/data/enhanced')]
    enhanced_dir = None
    enhanced_files = []

    for dir_path in enhanced_dirs:
        if dir_path.exists():
            enhanced_dir = dir_path
            enhanced_files = list(enhanced_dir.glob('enhanced_*.json'))
            if enhanced_files:
                break

    if not enhanced_files:
        print("No enhanced recipes found in data/enhanced/ or src/data/enhanced/")
        return 1

    print(f"\nFound {len(enhanced_files)} enhanced recipes to evaluate\n")

    all_results = []

    for file_path in sorted(enhanced_files):
        if file_path.name == 'pipeline_summary_report.json':
            continue

        try:
            result = evaluate_enhanced_recipe(str(file_path))
            all_results.append(result)
        except Exception as e:
            print(f"\n✗ Error evaluating {file_path.name}: {e}")
            import traceback
            traceback.print_exc()

    # Overall summary
    print(f"\n{'='*80}")
    print("Overall Summary")
    print(f"{'='*80}")

    total_recipes = len(all_results)
    total_modifications = sum(r['modifications_count'] for r in all_results)
    total_accurate = sum(
        sum(1 for a in r['modification_analysis'] if a['is_accurate'])
        for r in all_results
    )
    total_issues = sum(len(r['issues']) for r in all_results)

    print(f"\nRecipes evaluated: {total_recipes}")
    print(f"Total modifications: {total_modifications}")
    print(f"Accurate modifications: {total_accurate}/{total_modifications} "
          f"({total_accurate/total_modifications*100:.1f}%)")
    print(f"Total issues found: {total_issues}")

    # Check for patterns
    print(f"\n{'─'*80}")
    print("Key Findings:")
    print(f"{'─'*80}")

    all_high_quality = all(r['quality_filtering']['all_high_rated'] for r in all_results)
    if all_high_quality:
        print("✓ Quality filtering is working correctly (all modifications from ≥4★ reviews)")
    else:
        print("⚠ Some low-rated reviews may have been included")

    accuracy_rate = total_accurate / total_modifications if total_modifications > 0 else 0
    if accuracy_rate >= 0.90:
        print(f"✓ High modification accuracy ({accuracy_rate*100:.1f}%)")
    elif accuracy_rate >= 0.75:
        print(f"○ Good modification accuracy ({accuracy_rate*100:.1f}%)")
    else:
        print(f"⚠ Lower modification accuracy ({accuracy_rate*100:.1f}%) - review changes")

    if total_issues == 0:
        print("✓ No major issues detected across all recipes")
    else:
        print(f"⚠ Found {total_issues} issues across all recipes")

    return 0


if __name__ == '__main__':
    sys.exit(main())
