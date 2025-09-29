"""
Simple Multi-Modification Extraction Test
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent))

def test_multi_modification_examples():
    """Test multi-modification extraction with simple examples."""

    print("🧪 Testing Multi-Modification Extraction")
    print("=" * 50)

    # Test cases from the PRD
    test_cases = [
        {
            "review": "I used 1 cup brown sugar instead of white, added an extra egg, and baked at 375°F",
            "expected_modifications": 3,
            "description": "Three clear modifications"
        },
        {
            "review": "I omitted nuts, doubled the chocolate chips, and added vanilla extract",
            "expected_modifications": 3,
            "description": "Omission, quantity change, and addition"
        },
        {
            "review": "I added an egg and halved the sugar",
            "expected_modifications": 2,
            "description": "Simple addition and quantity change"
        },
        {
            "review": "Great recipe! I followed it exactly.",
            "expected_modifications": 0,
            "description": "No modifications"
        },
        {
            "review": "I substituted honey for sugar, used whole wheat flour instead of all-purpose, and added cinnamon and nutmeg for extra spice",
            "expected_modifications": 3,
            "description": "Complex substitutions and additions"
        }
    ]

    def count_modifications_heuristic(text):
        """Simple heuristic to count modifications."""
        import re

        text_lower = text.lower()

        # Count action words
        action_words = ['added', 'used', 'substituted', 'omitted', 'doubled', 'halved', 'increased', 'decreased', 'changed']
        action_count = sum(1 for word in action_words if word in text_lower)

        # Count conjunctions that might indicate multiple actions
        conjunctions = len(re.findall(r'\band\b|\,\s*and\b', text_lower))

        # Estimate modifications
        if action_count == 0:
            return 0

        # Base count is action words, plus conjunctions suggest multiple modifications
        estimated = max(action_count, 1 + conjunctions)

        return estimated

    total_tests = len(test_cases)
    correct_estimates = 0

    for i, case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {case['description']}")
        print(f"Review: \"{case['review'][:60]}{'...' if len(case['review']) > 60 else ''}\"")
        print(f"Expected modifications: {case['expected_modifications']}")

        estimated = count_modifications_heuristic(case['review'])
        print(f"Estimated modifications: {estimated}")

        # Check if estimate is close (within 1)
        is_correct = abs(estimated - case['expected_modifications']) <= 1

        if is_correct:
            correct_estimates += 1
            print("✅ PASS - Estimate within acceptable range")
        else:
            print("❌ FAIL - Estimate too far from expected")

    accuracy = correct_estimates / total_tests
    print(f"\n📊 RESULTS")
    print("=" * 30)
    print(f"Total test cases: {total_tests}")
    print(f"Correct estimates: {correct_estimates}")
    print(f"Accuracy: {accuracy:.1%}")
    print(f"Target: 95% (PRD requirement)")
    print(f"Meets target: {'✅ YES' if accuracy >= 0.95 else '❌ NO'}")

    if accuracy >= 0.95:
        print("\n🎉 Multi-modification detection meets PRD requirements!")
    else:
        print("\n⚠️ Multi-modification detection needs improvement.")
        print("Recommendations:")
        print("- Enhance action word detection")
        print("- Improve conjunction parsing")
        print("- Add more sophisticated NLP analysis")

    return accuracy

def test_real_recipe_reviews():
    """Test with real reviews from the dataset."""

    print(f"\n🔍 Testing Real Recipe Reviews")
    print("=" * 40)

    # Load a real recipe file
    try:
        import json
        recipe_file = Path("../../data/enhanced/recipe_10813_best-chocolate-chip-cookies.json")

        if recipe_file.exists():
            with open(recipe_file, 'r') as f:
                recipe_data = json.load(f)

            reviews = recipe_data.get('reviews', [])
            modification_reviews = [r for r in reviews if r.get('has_modification', False)]

            print(f"Found {len(modification_reviews)} modification reviews")

            for i, review in enumerate(modification_reviews[:3]):  # Test first 3
                text = review.get('text', '')
                print(f"\n📝 Real Review {i+1}:")
                print(f"Text: \"{text[:80]}{'...' if len(text) > 80 else ''}\"")

                # Simple analysis
                import re
                action_words = ['added', 'used', 'substituted', 'omitted', 'doubled', 'halved']
                found_actions = [word for word in action_words if word in text.lower()]

                print(f"Action words found: {found_actions}")
                print(f"Estimated modifications: {len(found_actions) if found_actions else 1}")

        else:
            print("No enhanced recipe files found. Run enhanced pipeline first.")

    except Exception as e:
        print(f"Error loading real data: {e}")

if __name__ == "__main__":
    test_multi_modification_examples()
    test_real_recipe_reviews()