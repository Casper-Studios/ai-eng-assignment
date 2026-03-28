#!/usr/bin/env python3
"""
Re-run pipeline on the 4 enhanced recipes with improved prompt.
Compare new extractions to previous results to measure improvement.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from llm_pipeline.pipeline import LLMAnalysisPipeline


def backup_existing_enhanced_recipes():
    """Backup current enhanced recipes before re-running."""
    enhanced_dir = Path("data/enhanced")
    backup_dir = Path("data/enhanced_backup")

    if not enhanced_dir.exists():
        print("No existing enhanced recipes found")
        return

    backup_dir.mkdir(exist_ok=True)

    import shutil
    for file in enhanced_dir.glob("enhanced_*.json"):
        if file.name != "pipeline_summary_report.json":
            dest = backup_dir / file.name
            shutil.copy2(file, dest)
            print(f"Backed up: {file.name}")

    print(f"\n✓ Backed up existing recipes to {backup_dir}")


def get_recipe_ids():
    """Get the 4 recipe IDs that were previously enhanced."""
    return [
        "recipe_10813_best-chocolate-chip-cookies.json",
        "recipe_144299_nikujaga-japanese-style-meat-and-potatoes-.json",
        "recipe_19117_spicy-apple-cake.json",
        "recipe_77935_creamy-sweet-potato-with-ginger-soup.json",
    ]


def compare_extractions(old_file, new_file):
    """Compare old and new extractions to measure improvement."""
    with open(old_file, 'r') as f:
        old_data = json.load(f)
    with open(new_file, 'r') as f:
        new_data = json.load(f)

    old_mods = old_data.get('modifications_applied', [])
    new_mods = new_data.get('modifications_applied', [])

    comparison = {
        'recipe_id': old_data.get('recipe_id'),
        'title': old_data.get('title'),
        'old_modification_count': len(old_mods),
        'new_modification_count': len(new_mods),
        'improvements': []
    }

    # Compare each modification
    for old_mod in old_mods:
        old_review_text = old_mod['source_review']['text']
        old_changes = len(old_mod['changes_made'])

        # Find matching review in new data
        matching_new = None
        for new_mod in new_mods:
            if new_mod['source_review']['text'] == old_review_text:
                matching_new = new_mod
                break

        if matching_new:
            new_changes = len(matching_new['changes_made'])
            if new_changes > old_changes:
                comparison['improvements'].append({
                    'review': old_review_text[:80] + "...",
                    'old_changes': old_changes,
                    'new_changes': new_changes,
                    'improvement': new_changes - old_changes
                })

    return comparison


def main():
    """Re-run pipeline and compare results."""
    print("="*80)
    print("Re-running Pipeline with Improved Multi-Change Prompt")
    print("="*80)

    # Backup existing enhanced recipes
    print("\nStep 1: Backing up existing enhanced recipes...")
    backup_existing_enhanced_recipes()

    # Initialize pipeline
    print("\nStep 2: Initializing pipeline...")
    pipeline = LLMAnalysisPipeline(output_dir="data/enhanced_new")

    # Get recipe files
    recipe_ids = get_recipe_ids()
    recipe_files = [f"data/{rid}" for rid in recipe_ids]

    print(f"\nStep 3: Processing {len(recipe_files)} recipes...")
    print("="*80)

    # Process each recipe
    results = []
    for i, recipe_file in enumerate(recipe_files, 1):
        print(f"\n[{i}/{len(recipe_files)}] Processing: {Path(recipe_file).name}")

        if not Path(recipe_file).exists():
            print(f"  ⚠️  File not found: {recipe_file}")
            continue

        try:
            enhanced_recipe = pipeline.process_single_recipe(recipe_file, save_output=True)
            if enhanced_recipe:
                results.append(enhanced_recipe)
                print(f"  ✓ Successfully processed: {enhanced_recipe.title}")
                print(f"    Modifications applied: {len(enhanced_recipe.modifications_applied)}")
            else:
                print(f"  ✗ Failed to process")
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*80)
    print(f"Pipeline Complete: {len(results)}/{len(recipe_files)} recipes processed")
    print("="*80)

    # Compare old vs new
    print("\nStep 4: Comparing old vs new extractions...")
    print("="*80)

    comparisons = []
    for recipe_id in recipe_ids:
        old_file = f"data/enhanced/enhanced_{recipe_id.replace('recipe_', '')}"
        new_file = f"data/enhanced_new/enhanced_{recipe_id.replace('recipe_', '')}"

        if Path(old_file).exists() and Path(new_file).exists():
            comparison = compare_extractions(old_file, new_file)
            comparisons.append(comparison)

            print(f"\n{comparison['title']}")
            print(f"  Old modifications: {comparison['old_modification_count']}")
            print(f"  New modifications: {comparison['new_modification_count']}")

            if comparison['improvements']:
                print(f"  ✓ Improvements found:")
                for imp in comparison['improvements']:
                    print(f"    • {imp['review']}")
                    print(f"      {imp['old_changes']} → {imp['new_changes']} changes (+{imp['improvement']})")
            else:
                print(f"  ○ No change in modification count")

    # Summary statistics
    print("\n" + "="*80)
    print("Overall Summary")
    print("="*80)

    total_old_mods = sum(c['old_modification_count'] for c in comparisons)
    total_new_mods = sum(c['new_modification_count'] for c in comparisons)
    total_improvements = sum(len(c['improvements']) for c in comparisons)
    total_added_changes = sum(
        sum(imp['improvement'] for imp in c['improvements'])
        for c in comparisons
    )

    print(f"\nTotal modifications (old): {total_old_mods}")
    print(f"Total modifications (new): {total_new_mods}")
    print(f"Net increase: {total_new_mods - total_old_mods} modifications")

    if total_improvements > 0:
        print(f"\n✓ {total_improvements} reviews with improved extraction")
        print(f"✓ {total_added_changes} additional changes captured")
        print(f"\nImprovement rate: {total_added_changes / total_old_mods * 100:.1f}% increase in changes captured")

    # Quality check
    print("\n" + "="*80)
    print("Quality Check: Are all modifications still from high-rated reviews?")
    print("="*80)

    all_high_quality = True
    for comparison in comparisons:
        new_file = f"data/enhanced_new/enhanced_{comparison['recipe_id']}.json"
        with open(new_file, 'r') as f:
            new_data = json.load(f)

        for mod in new_data.get('modifications_applied', []):
            rating = mod['source_review'].get('rating')
            if rating and rating < 4:
                all_high_quality = False
                print(f"  ⚠️  Low-rated review found: {rating}★ in {comparison['title']}")

    if all_high_quality:
        print("  ✓ All modifications from ≥4★ reviews")

    return 0


if __name__ == "__main__":
    sys.exit(main())
