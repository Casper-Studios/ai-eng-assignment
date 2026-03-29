#!/usr/bin/env python3
"""
Detailed comparison of old vs new extractions to identify specific improvements.
"""

import json
import sys
from pathlib import Path


def load_json(file_path):
    """Load JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)


def extract_changes_from_review(modification):
    """Extract all changes mentioned in a modification."""
    changes = []
    for change in modification.get('changes_made', []):
        changes.append({
            'type': change.get('type'),
            'from': change.get('from_text', ''),
            'to': change.get('to_text', ''),
            'operation': change.get('operation')
        })
    return changes


def compare_reviews(old_mod, new_mod):
    """Compare old and new modification for the same review."""
    old_changes = extract_changes_from_review(old_mod)
    new_changes = extract_changes_from_review(new_mod)

    comparison = {
        'review_text': old_mod['source_review']['text'][:100] + '...',
        'rating': old_mod['source_review']['rating'],
        'old_count': len(old_changes),
        'new_count': len(new_changes),
        'old_changes': old_changes,
        'new_changes': new_changes,
        'added': [],
        'removed': [],
        'modified': []
    }

    # Find added changes
    for new_change in new_changes:
        found = False
        for old_change in old_changes:
            if (new_change['to'] == old_change['to'] and
                new_change['operation'] == old_change['operation']):
                found = True
                break
        if not found:
            comparison['added'].append(new_change)

    # Find removed changes
    for old_change in old_changes:
        found = False
        for new_change in new_changes:
            if (old_change['to'] == new_change['to'] and
                old_change['operation'] == new_change['operation']):
                found = True
                break
        if not found:
            comparison['removed'].append(old_change)

    return comparison


def main():
    """Run detailed comparison."""
    print("="*80)
    print("Detailed Old vs New Extraction Comparison")
    print("="*80)

    # Compare chocolate chip cookies
    old_file = "data/enhanced_backup/enhanced_10813_best-chocolate-chip-cookies.json"
    new_file = "data/enhanced_new/enhanced_10813_best-chocolate-chip-cookies.json"

    if not Path(old_file).exists() or not Path(new_file).exists():
        print("Files not found. Run rerun_pipeline_comparison.py first.")
        return 1

    old_data = load_json(old_file)
    new_data = load_json(new_file)

    print(f"\nRecipe: {old_data['title']}")
    print(f"Old modifications: {len(old_data['modifications_applied'])}")
    print(f"New modifications: {len(new_data['modifications_applied'])}")

    # Match reviews by text
    for old_mod in old_data['modifications_applied']:
        review_text = old_mod['source_review']['text']

        # Find matching new mod
        matching_new = None
        for new_mod in new_data['modifications_applied']:
            if new_mod['source_review']['text'] == review_text:
                matching_new = new_mod
                break

        if matching_new:
            comparison = compare_reviews(old_mod, matching_new)

            print(f"\n{'─'*80}")
            print(f"Review ({comparison['rating']}★): {comparison['review_text']}")
            print(f"{'─'*80}")
            print(f"Old: {comparison['old_count']} changes | New: {comparison['new_count']} changes")

            if comparison['added']:
                print(f"\n✓ NEW changes captured ({len(comparison['added'])}):")
                for change in comparison['added']:
                    print(f"  • {change['operation']}: {change['from'][:50]}... → {change['to'][:50]}...")

            if comparison['removed']:
                print(f"\n✗ REMOVED changes ({len(comparison['removed'])}):")
                for change in comparison['removed']:
                    print(f"  • {change['operation']}: {change['from'][:50]}... → {change['to'][:50]}...")

            if not comparison['added'] and not comparison['removed']:
                print("\n○ No change in extraction")

    # Check for cinnamon specifically
    print(f"\n{'='*80}")
    print("Specific Check: Cinnamon Addition")
    print(f"{'='*80}")

    review_text = "I just made these and 😍😋!!!! Changes- used a whole cup of white sugar and 1/2 c of brown (because it's what I had) and 1/2 c less flour after reading some other reviews, and added a tiny dash of cinnamon."

    print(f"\nReview: {review_text}")
    print(f"\nExpected: 'dash of cinnamon' should be captured as an addition")

    # Check old extraction
    for mod in old_data['modifications_applied']:
        if review_text in mod['source_review']['text']:
            print(f"\nOld extraction:")
            for change in mod['changes_made']:
                print(f"  • {change['to_text']}")

    # Check new extraction
    for mod in new_data['modifications_applied']:
        if review_text in mod['source_review']['text']:
            print(f"\nNew extraction:")
            for change in mod['changes_made']:
                print(f"  • {change['to_text']}")

    has_cinnamon_old = any('cinnamon' in change['to_text'].lower()
                          for mod in old_data['modifications_applied']
                          if review_text in mod['source_review']['text']
                          for change in mod['changes_made'])

    has_cinnamon_new = any('cinnamon' in change['to_text'].lower()
                          for mod in new_data['modifications_applied']
                          if review_text in mod['source_review']['text']
                          for change in mod['changes_made'])

    print(f"\nCinnamon captured - Old: {has_cinnamon_old} | New: {has_cinnamon_new}")

    if not has_cinnamon_new:
        print("\n⚠️  Cinnamon still not captured - the improved prompt alone may not be enough")
        print("   Consider: even more explicit prompt or higher temperature for creativity")

    return 0


if __name__ == "__main__":
    sys.exit(main())
