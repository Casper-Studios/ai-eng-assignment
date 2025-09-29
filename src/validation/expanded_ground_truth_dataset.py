"""
Expanded Ground Truth Dataset for Recipe Enhancement Validation

This module creates a comprehensive dataset of 50+ test cases
to improve accuracy validation as required by the PRD.
"""

from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class ModificationExample:
    """A single modification example with ground truth."""
    text: str
    expected_modifications: int
    modification_types: List[str]
    difficulty: str
    has_clear_modification: bool
    notes: str = ""

class ExpandedGroundTruthDataset:
    """Comprehensive ground truth dataset for validation."""

    def __init__(self):
        """Initialize with 50+ diverse test cases."""
        self.test_cases = self._create_comprehensive_dataset()

    def _create_comprehensive_dataset(self) -> List[ModificationExample]:
        """Create comprehensive test dataset with 50+ cases."""

        test_cases = [
            # SIMPLE MODIFICATIONS (1 modification each)
            ModificationExample(
                text="I added an extra egg yolk for chewier texture",
                expected_modifications=1,
                modification_types=["addition"],
                difficulty="simple",
                has_clear_modification=True,
                notes="Clear single addition"
            ),
            ModificationExample(
                text="I used brown sugar instead of white sugar",
                expected_modifications=1,
                modification_types=["substitution"],
                difficulty="simple",
                has_clear_modification=True,
                notes="Clear substitution"
            ),
            ModificationExample(
                text="I omitted the nuts from the recipe",
                expected_modifications=1,
                modification_types=["omission"],
                difficulty="simple",
                has_clear_modification=True,
                notes="Clear omission"
            ),
            ModificationExample(
                text="I doubled the chocolate chips",
                expected_modifications=1,
                modification_types=["quantity_change"],
                difficulty="simple",
                has_clear_modification=True,
                notes="Clear quantity change"
            ),
            ModificationExample(
                text="I baked them at 375°F instead of 350°F",
                expected_modifications=1,
                modification_types=["temperature_change"],
                difficulty="simple",
                has_clear_modification=True,
                notes="Temperature modification"
            ),

            # MEDIUM COMPLEXITY (2 modifications each)
            ModificationExample(
                text="I added an egg and halved the sugar",
                expected_modifications=2,
                modification_types=["addition", "quantity_change"],
                difficulty="medium",
                has_clear_modification=True,
                notes="Two clear modifications"
            ),
            ModificationExample(
                text="I used butter instead of oil and added vanilla",
                expected_modifications=2,
                modification_types=["substitution", "addition"],
                difficulty="medium",
                has_clear_modification=True,
                notes="Substitution plus addition"
            ),
            ModificationExample(
                text="I omitted nuts and doubled the chocolate chips",
                expected_modifications=2,
                modification_types=["omission", "quantity_change"],
                difficulty="medium",
                has_clear_modification=True,
                notes="Omission plus quantity change"
            ),
            ModificationExample(
                text="I reduced the salt by half and increased the baking time",
                expected_modifications=2,
                modification_types=["quantity_change", "time_change"],
                difficulty="medium",
                has_clear_modification=True,
                notes="Two quantity/time changes"
            ),
            ModificationExample(
                text="I substituted honey for sugar and added cinnamon",
                expected_modifications=2,
                modification_types=["substitution", "addition"],
                difficulty="medium",
                has_clear_modification=True,
                notes="Sweet substitution plus spice"
            ),

            # COMPLEX MODIFICATIONS (3+ modifications each)
            ModificationExample(
                text="I used 1 cup brown sugar instead of white, added an extra egg, and baked at 375°F",
                expected_modifications=3,
                modification_types=["substitution", "addition", "temperature_change"],
                difficulty="complex",
                has_clear_modification=True,
                notes="PRD test case - three distinct changes"
            ),
            ModificationExample(
                text="I omitted nuts, doubled the chocolate chips, and added vanilla extract",
                expected_modifications=3,
                modification_types=["omission", "quantity_change", "addition"],
                difficulty="complex",
                has_clear_modification=True,
                notes="PRD test case - three distinct changes"
            ),
            ModificationExample(
                text="I substituted honey for sugar, used whole wheat flour instead of all-purpose, and added chopped almonds",
                expected_modifications=3,
                modification_types=["substitution", "substitution", "addition"],
                difficulty="complex",
                has_clear_modification=True,
                notes="Multiple substitutions plus addition"
            ),
            ModificationExample(
                text="I used half the salt, doubled the vanilla, increased the flour by 1/4 cup, and baked for 2 minutes longer",
                expected_modifications=4,
                modification_types=["quantity_change", "quantity_change", "quantity_change", "time_change"],
                difficulty="complex",
                has_clear_modification=True,
                notes="Four distinct quantity/time changes"
            ),

            # SUBTLE MODIFICATIONS (require careful parsing)
            ModificationExample(
                text="I pressed them down slightly before baking",
                expected_modifications=1,
                modification_types=["technique_change"],
                difficulty="subtle",
                has_clear_modification=True,
                notes="Technique modification - subtle but clear"
            ),
            ModificationExample(
                text="I refrigerated the batter for an hour before baking",
                expected_modifications=1,
                modification_types=["technique_change"],
                difficulty="subtle",
                has_clear_modification=True,
                notes="Timing/technique modification"
            ),
            ModificationExample(
                text="I used room temperature eggs instead of cold ones",
                expected_modifications=1,
                modification_types=["technique_change"],
                difficulty="subtle",
                has_clear_modification=True,
                notes="Ingredient preparation change"
            ),
            ModificationExample(
                text="I sifted the flour before adding it",
                expected_modifications=1,
                modification_types=["technique_change"],
                difficulty="subtle",
                has_clear_modification=True,
                notes="Preparation technique"
            ),

            # NO MODIFICATIONS (control cases)
            ModificationExample(
                text="Great recipe! I followed it exactly.",
                expected_modifications=0,
                modification_types=[],
                difficulty="simple",
                has_clear_modification=False,
                notes="No modifications - positive review"
            ),
            ModificationExample(
                text="These turned out perfect! No changes needed.",
                expected_modifications=0,
                modification_types=[],
                difficulty="simple",
                has_clear_modification=False,
                notes="No modifications - satisfied customer"
            ),
            ModificationExample(
                text="Followed the recipe as written and loved the results.",
                expected_modifications=0,
                modification_types=[],
                difficulty="simple",
                has_clear_modification=False,
                notes="No modifications - followed exactly"
            ),

            # EDGE CASES
            ModificationExample(
                text="I would add more chocolate chips next time",
                expected_modifications=0,
                modification_types=[],
                difficulty="tricky",
                has_clear_modification=False,
                notes="Future intention, not actual modification"
            ),
            ModificationExample(
                text="My oven runs hot so I baked at 325°F instead",
                expected_modifications=1,
                modification_types=["temperature_change"],
                difficulty="medium",
                has_clear_modification=True,
                notes="Equipment-based modification"
            ),
            ModificationExample(
                text="I didn't have brown sugar so I used all white sugar",
                expected_modifications=1,
                modification_types=["substitution"],
                difficulty="medium",
                has_clear_modification=True,
                notes="Ingredient availability substitution"
            ),

            # QUANTITY-BASED MODIFICATIONS
            ModificationExample(
                text="I tripled the recipe for a party",
                expected_modifications=1,
                modification_types=["scaling"],
                difficulty="medium",
                has_clear_modification=True,
                notes="Recipe scaling modification"
            ),
            ModificationExample(
                text="I made a half batch since it's just me",
                expected_modifications=1,
                modification_types=["scaling"],
                difficulty="medium",
                has_clear_modification=True,
                notes="Recipe scaling down"
            ),

            # SPICE AND FLAVOR MODIFICATIONS
            ModificationExample(
                text="I added a pinch of sea salt on top",
                expected_modifications=1,
                modification_types=["addition"],
                difficulty="simple",
                has_clear_modification=True,
                notes="Finishing salt addition"
            ),
            ModificationExample(
                text="I sprinkled cinnamon and nutmeg into the batter",
                expected_modifications=1,
                modification_types=["addition"],
                difficulty="medium",
                has_clear_modification=True,
                notes="Multiple spices as one modification"
            ),
            ModificationExample(
                text="I added lemon zest and replaced vanilla with almond extract",
                expected_modifications=2,
                modification_types=["addition", "substitution"],
                difficulty="medium",
                has_clear_modification=True,
                notes="Flavor addition plus extract substitution"
            ),

            # TEXTURE MODIFICATIONS
            ModificationExample(
                text="I chilled the dough for 30 minutes to prevent spreading",
                expected_modifications=1,
                modification_types=["technique_change"],
                difficulty="medium",
                has_clear_modification=True,
                notes="Dough handling technique"
            ),
            ModificationExample(
                text="I rolled them in sugar before baking for extra crunch",
                expected_modifications=1,
                modification_types=["technique_change"],
                difficulty="medium",
                has_clear_modification=True,
                notes="Surface treatment technique"
            ),

            # BAKING TECHNIQUE MODIFICATIONS
            ModificationExample(
                text="I used parchment paper instead of greasing the pan",
                expected_modifications=1,
                modification_types=["technique_change"],
                difficulty="medium",
                has_clear_modification=True,
                notes="Pan preparation change"
            ),
            ModificationExample(
                text="I rotated the pans halfway through baking",
                expected_modifications=1,
                modification_types=["technique_change"],
                difficulty="medium",
                has_clear_modification=True,
                notes="Baking technique modification"
            ),

            # HEALTH-CONSCIOUS MODIFICATIONS
            ModificationExample(
                text="I used coconut oil instead of butter for dairy-free version",
                expected_modifications=1,
                modification_types=["substitution"],
                difficulty="medium",
                has_clear_modification=True,
                notes="Dietary restriction substitution"
            ),
            ModificationExample(
                text="I replaced half the flour with almond flour and used stevia instead of sugar",
                expected_modifications=2,
                modification_types=["substitution", "substitution"],
                difficulty="complex",
                has_clear_modification=True,
                notes="Health-conscious double substitution"
            ),

            # INGREDIENT AVAILABILITY MODIFICATIONS
            ModificationExample(
                text="I was out of chocolate chips so I chopped up a dark chocolate bar",
                expected_modifications=1,
                modification_types=["substitution"],
                difficulty="medium",
                has_clear_modification=True,
                notes="Ingredient form substitution"
            ),
            ModificationExample(
                text="No vanilla extract on hand, so I used maple syrup instead",
                expected_modifications=1,
                modification_types=["substitution"],
                difficulty="medium",
                has_clear_modification=True,
                notes="Flavoring substitution"
            ),

            # SEASONAL/CREATIVE MODIFICATIONS
            ModificationExample(
                text="I added dried cranberries and orange zest for a holiday twist",
                expected_modifications=1,
                modification_types=["addition"],
                difficulty="medium",
                has_clear_modification=True,
                notes="Multiple seasonal additions as one modification"
            ),
            ModificationExample(
                text="I mixed in crushed pretzels and caramel chips for sweet and salty",
                expected_modifications=1,
                modification_types=["addition"],
                difficulty="medium",
                has_clear_modification=True,
                notes="Multiple mix-ins as one modification"
            ),

            # SIZE AND SHAPE MODIFICATIONS
            ModificationExample(
                text="I made them smaller and baked for 8 minutes instead of 10",
                expected_modifications=2,
                modification_types=["size_change", "time_change"],
                difficulty="medium",
                has_clear_modification=True,
                notes="Size and time adjustment"
            ),
            ModificationExample(
                text="I used a cookie scoop for uniform size",
                expected_modifications=1,
                modification_types=["technique_change"],
                difficulty="simple",
                has_clear_modification=True,
                notes="Shaping technique"
            ),

            # STORAGE AND SERVING MODIFICATIONS
            ModificationExample(
                text="I let them cool completely then stored in an airtight container",
                expected_modifications=0,
                modification_types=[],
                difficulty="simple",
                has_clear_modification=False,
                notes="Storage instruction, not recipe modification"
            ),
            ModificationExample(
                text="I served them warm with ice cream",
                expected_modifications=0,
                modification_types=[],
                difficulty="simple",
                has_clear_modification=False,
                notes="Serving suggestion, not recipe modification"
            ),

            # AMBIGUOUS CASES
            ModificationExample(
                text="I think these could use more chocolate",
                expected_modifications=0,
                modification_types=[],
                difficulty="tricky",
                has_clear_modification=False,
                notes="Opinion, not actual modification"
            ),
            ModificationExample(
                text="Next time I'll try adding nuts",
                expected_modifications=0,
                modification_types=[],
                difficulty="tricky",
                has_clear_modification=False,
                notes="Future intention, not current modification"
            ),

            # MULTI-STEP PROCESS MODIFICATIONS
            ModificationExample(
                text="I creamed the butter and sugars longer, then added eggs one at a time, then gradually mixed in dry ingredients",
                expected_modifications=3,
                modification_types=["technique_change", "technique_change", "technique_change"],
                difficulty="complex",
                has_clear_modification=True,
                notes="Multiple technique improvements"
            ),

            # EQUIPMENT-BASED MODIFICATIONS
            ModificationExample(
                text="I used a stand mixer instead of hand mixing",
                expected_modifications=1,
                modification_types=["technique_change"],
                difficulty="simple",
                has_clear_modification=True,
                notes="Equipment change"
            ),
            ModificationExample(
                text="I baked on a silicone mat instead of directly on the pan",
                expected_modifications=1,
                modification_types=["technique_change"],
                difficulty="simple",
                has_clear_modification=True,
                notes="Baking surface change"
            ),

            # COMBINATION MODIFICATIONS WITH RATIONALE
            ModificationExample(
                text="For chewier cookies, I added an extra egg yolk and baked at a lower temperature",
                expected_modifications=2,
                modification_types=["addition", "temperature_change"],
                difficulty="medium",
                has_clear_modification=True,
                notes="Goal-oriented dual modification"
            ),
            ModificationExample(
                text="To make them less sweet, I reduced sugar by 1/4 cup and added a pinch more salt",
                expected_modifications=2,
                modification_types=["quantity_change", "quantity_change"],
                difficulty="medium",
                has_clear_modification=True,
                notes="Taste-balancing modifications"
            ),

            # PRECISE MEASUREMENT MODIFICATIONS
            ModificationExample(
                text="I weighed my flour (360g instead of 3 cups) for more accuracy",
                expected_modifications=1,
                modification_types=["technique_change"],
                difficulty="medium",
                has_clear_modification=True,
                notes="Measurement method change"
            ),

            # ALTITUDE/CLIMATE ADJUSTMENTS
            ModificationExample(
                text="At high altitude, I reduced baking soda and increased liquid",
                expected_modifications=2,
                modification_types=["quantity_change", "quantity_change"],
                difficulty="medium",
                has_clear_modification=True,
                notes="Altitude adjustment modifications"
            ),

            # DIETARY MODIFICATIONS
            ModificationExample(
                text="I made them gluten-free using a 1:1 flour substitute and added xanthan gum",
                expected_modifications=2,
                modification_types=["substitution", "addition"],
                difficulty="complex",
                has_clear_modification=True,
                notes="Gluten-free conversion"
            ),
            ModificationExample(
                text="For vegan version, I used flax eggs and vegan butter",
                expected_modifications=2,
                modification_types=["substitution", "substitution"],
                difficulty="complex",
                has_clear_modification=True,
                notes="Vegan conversion"
            ),

            # PROFESSIONAL TECHNIQUE MODIFICATIONS
            ModificationExample(
                text="I browned the butter first for deeper flavor",
                expected_modifications=1,
                modification_types=["technique_change"],
                difficulty="medium",
                has_clear_modification=True,
                notes="Professional technique enhancement"
            ),
            ModificationExample(
                text="I let the dough rest overnight in the fridge for better flavor development",
                expected_modifications=1,
                modification_types=["technique_change"],
                difficulty="medium",
                has_clear_modification=True,
                notes="Flavor development technique"
            )
        ]

        return test_cases

    def get_test_cases(self) -> List[ModificationExample]:
        """Get all test cases."""
        return self.test_cases

    def get_test_cases_by_difficulty(self, difficulty: str) -> List[ModificationExample]:
        """Get test cases by difficulty level."""
        return [case for case in self.test_cases if case.difficulty == difficulty]

    def get_modification_cases_only(self) -> List[ModificationExample]:
        """Get only cases that have modifications."""
        return [case for case in self.test_cases if case.has_clear_modification]

    def get_no_modification_cases(self) -> List[ModificationExample]:
        """Get only cases with no modifications."""
        return [case for case in self.test_cases if not case.has_clear_modification]

    def generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation statistics."""

        total_cases = len(self.test_cases)
        modification_cases = len(self.get_modification_cases_only())
        no_modification_cases = len(self.get_no_modification_cases())

        difficulty_breakdown = {}
        for difficulty in ["simple", "medium", "complex", "subtle", "tricky"]:
            cases = self.get_test_cases_by_difficulty(difficulty)
            difficulty_breakdown[difficulty] = len(cases)

        return {
            "total_test_cases": total_cases,
            "modification_cases": modification_cases,
            "no_modification_cases": no_modification_cases,
            "difficulty_breakdown": difficulty_breakdown,
            "target_accuracy": 0.95,  # PRD requirement
            "dataset_quality": "comprehensive",
            "coverage": {
                "simple_modifications": True,
                "complex_modifications": True,
                "subtle_modifications": True,
                "edge_cases": True,
                "dietary_modifications": True,
                "technique_modifications": True,
                "equipment_modifications": True,
                "no_modification_controls": True
            }
        }

def main():
    """Test the expanded ground truth dataset."""

    dataset = ExpandedGroundTruthDataset()
    report = dataset.generate_validation_report()

    print("🧪 Expanded Ground Truth Dataset")
    print("=" * 50)
    print(f"Total test cases: {report['total_test_cases']}")
    print(f"Cases with modifications: {report['modification_cases']}")
    print(f"Cases without modifications: {report['no_modification_cases']}")
    print(f"Target coverage: 50+ cases ✅")
    print("\nDifficulty breakdown:")
    for difficulty, count in report['difficulty_breakdown'].items():
        print(f"  {difficulty}: {count} cases")

    print("\n✅ Dataset meets PRD requirements for comprehensive testing")

    return dataset

if __name__ == "__main__":
    main()