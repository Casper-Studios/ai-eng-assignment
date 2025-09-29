"""
Comprehensive Test Dataset for Multi-Modification Validation

This module provides carefully curated test cases with manually annotated
multi-modification reviews to validate the extraction pipeline's completeness
and accuracy.
"""

from typing import List, Dict, Any
from .modification_validator import GroundTruthEntry


class TestDatasetBuilder:
    """Builds comprehensive test datasets for validation."""

    def build_multi_modification_test_dataset(self) -> List[GroundTruthEntry]:
        """
        Build a comprehensive test dataset with manually annotated multi-modification reviews.

        Returns:
            List of GroundTruthEntry objects with known ground truth
        """
        test_cases = []

        # Test Case 1: Simple 2-modification case (chocolate chip cookies)
        test_cases.append(GroundTruthEntry(
            id="test_001_double_mod",
            review_text="I added an extra egg and doubled the vanilla extract. The cookies turned out much more moist and flavorful!",
            recipe_data={
                "title": "Classic Chocolate Chip Cookies",
                "ingredients": [
                    "2 1/4 cups all-purpose flour",
                    "1 tsp baking soda",
                    "1 tsp salt",
                    "1 cup butter, softened",
                    "3/4 cup granulated sugar",
                    "3/4 cup brown sugar",
                    "2 large eggs",
                    "2 tsp vanilla extract",
                    "2 cups chocolate chips"
                ],
                "instructions": [
                    "Preheat oven to 375°F",
                    "Mix flour, baking soda, and salt in bowl",
                    "Cream butter and sugars",
                    "Beat in eggs and vanilla",
                    "Stir in flour mixture",
                    "Add chocolate chips",
                    "Bake for 9-11 minutes"
                ]
            },
            expected_modifications=[
                {
                    "type": "addition",
                    "reasoning": "adding extra egg for moisture",
                    "target": "ingredients",
                    "description": "add one more egg"
                },
                {
                    "type": "quantity_adjustment",
                    "reasoning": "doubling vanilla for more flavor",
                    "target": "ingredients",
                    "description": "double the vanilla extract amount"
                }
            ],
            expected_count=2,
            difficulty_level="simple",
            notes="Clear 'and' conjunction separating two distinct modifications"
        ))

        # Test Case 2: Complex 3-modification case
        test_cases.append(GroundTruthEntry(
            id="test_002_triple_mod",
            review_text="I used brown sugar instead of white sugar, added 1/2 cup chopped walnuts, and baked at 350°F instead of 375°F. Perfect results!",
            recipe_data={
                "title": "Sugar Cookies",
                "ingredients": [
                    "2 3/4 cups all-purpose flour",
                    "1 tsp baking soda",
                    "1/2 tsp salt",
                    "1 1/4 cups white granulated sugar",
                    "1 cup butter",
                    "1 egg",
                    "1 tsp vanilla"
                ],
                "instructions": [
                    "Preheat oven to 375°F",
                    "Mix dry ingredients",
                    "Cream butter and sugar",
                    "Add egg and vanilla",
                    "Combine wet and dry",
                    "Roll into balls",
                    "Bake 8-10 minutes"
                ]
            },
            expected_modifications=[
                {
                    "type": "ingredient_substitution",
                    "reasoning": "substitute brown sugar for white sugar",
                    "target": "ingredients",
                    "description": "replace white sugar with brown sugar"
                },
                {
                    "type": "addition",
                    "reasoning": "add walnuts for texture",
                    "target": "ingredients",
                    "description": "add 1/2 cup chopped walnuts"
                },
                {
                    "type": "technique_change",
                    "reasoning": "lower temperature for different texture",
                    "target": "instructions",
                    "description": "change oven temperature from 375°F to 350°F"
                }
            ],
            expected_count=3,
            difficulty_level="complex",
            notes="Three distinct modifications with different types: substitution, addition, temperature change"
        ))

        # Test Case 3: Quantity adjustments with multiple items
        test_cases.append(GroundTruthEntry(
            id="test_003_multi_quantity",
            review_text="I halved the sugar and doubled the chocolate chips. Also increased the salt by 1/4 teaspoon for better flavor balance.",
            recipe_data={
                "title": "Chocolate Brownies",
                "ingredients": [
                    "1 cup sugar",
                    "1/2 cup butter",
                    "2 eggs",
                    "1/3 cup cocoa powder",
                    "1/2 cup flour",
                    "1/4 tsp salt",
                    "1/2 cup chocolate chips"
                ],
                "instructions": [
                    "Preheat oven to 350°F",
                    "Melt butter",
                    "Mix in sugar and eggs",
                    "Add dry ingredients",
                    "Fold in chocolate chips",
                    "Bake 25-30 minutes"
                ]
            },
            expected_modifications=[
                {
                    "type": "quantity_adjustment",
                    "reasoning": "reduce sugar content",
                    "target": "ingredients",
                    "description": "halve the sugar amount"
                },
                {
                    "type": "quantity_adjustment",
                    "reasoning": "increase chocolate for more flavor",
                    "target": "ingredients",
                    "description": "double the chocolate chips"
                },
                {
                    "type": "quantity_adjustment",
                    "reasoning": "increase salt for flavor balance",
                    "target": "ingredients",
                    "description": "add 1/4 teaspoon more salt"
                }
            ],
            expected_count=3,
            difficulty_level="medium",
            notes="Multiple quantity adjustments with 'also' indicating additional modification"
        ))

        # Test Case 4: Substitution chain
        test_cases.append(GroundTruthEntry(
            id="test_004_substitution_chain",
            review_text="I substituted almond flour for regular flour, used coconut oil instead of butter, and replaced eggs with flax eggs to make it vegan.",
            recipe_data={
                "title": "Banana Bread",
                "ingredients": [
                    "2 cups all-purpose flour",
                    "1/2 cup butter",
                    "2 eggs",
                    "3 ripe bananas",
                    "1/2 cup sugar",
                    "1 tsp baking powder"
                ],
                "instructions": [
                    "Preheat oven to 350°F",
                    "Mash bananas",
                    "Cream butter and sugar",
                    "Add eggs and bananas",
                    "Mix in flour and baking powder",
                    "Bake 60 minutes"
                ]
            },
            expected_modifications=[
                {
                    "type": "ingredient_substitution",
                    "reasoning": "substitute almond flour for wheat flour",
                    "target": "ingredients",
                    "description": "replace all-purpose flour with almond flour"
                },
                {
                    "type": "ingredient_substitution",
                    "reasoning": "use plant-based fat instead of dairy",
                    "target": "ingredients",
                    "description": "replace butter with coconut oil"
                },
                {
                    "type": "ingredient_substitution",
                    "reasoning": "make recipe vegan by replacing eggs",
                    "target": "ingredients",
                    "description": "replace eggs with flax eggs"
                }
            ],
            expected_count=3,
            difficulty_level="complex",
            notes="Multiple substitutions for dietary adaptation - all ingredient_substitution type"
        ))

        # Test Case 5: Technique modifications
        test_cases.append(GroundTruthEntry(
            id="test_005_technique_mods",
            review_text="I chilled the dough for 2 hours before baking, then baked at 325°F for 15 minutes instead of the original time and temperature.",
            recipe_data={
                "title": "Sugar Cookies",
                "ingredients": [
                    "2 cups flour",
                    "1 cup sugar",
                    "1/2 cup butter",
                    "1 egg",
                    "1 tsp vanilla"
                ],
                "instructions": [
                    "Mix ingredients",
                    "Roll dough",
                    "Cut shapes",
                    "Bake at 375°F for 8-10 minutes"
                ]
            },
            expected_modifications=[
                {
                    "type": "technique_change",
                    "reasoning": "chill dough for better texture",
                    "target": "instructions",
                    "description": "add step to chill dough for 2 hours"
                },
                {
                    "type": "technique_change",
                    "reasoning": "adjust temperature and time for different result",
                    "target": "instructions",
                    "description": "change baking to 325°F for 15 minutes"
                }
            ],
            expected_count=2,
            difficulty_level="medium",
            notes="Technique modifications affecting process rather than ingredients"
        ))

        # Test Case 6: Mixed additions and removals
        test_cases.append(GroundTruthEntry(
            id="test_006_add_remove_mix",
            review_text="I omitted the nuts because of allergies, added 1/4 cup dried cranberries for sweetness, and included a pinch of cinnamon.",
            recipe_data={
                "title": "Oatmeal Cookies",
                "ingredients": [
                    "1 cup flour",
                    "1 cup oats",
                    "1/2 cup sugar",
                    "1/2 cup butter",
                    "1 egg",
                    "1/2 cup chopped walnuts"
                ],
                "instructions": [
                    "Mix dry ingredients",
                    "Cream butter and sugar",
                    "Combine all ingredients",
                    "Bake at 350°F for 12 minutes"
                ]
            },
            expected_modifications=[
                {
                    "type": "removal",
                    "reasoning": "remove nuts due to allergies",
                    "target": "ingredients",
                    "description": "remove chopped walnuts"
                },
                {
                    "type": "addition",
                    "reasoning": "add dried fruit for sweetness",
                    "target": "ingredients",
                    "description": "add 1/4 cup dried cranberries"
                },
                {
                    "type": "addition",
                    "reasoning": "add spice for flavor enhancement",
                    "target": "ingredients",
                    "description": "add pinch of cinnamon"
                }
            ],
            expected_count=3,
            difficulty_level="medium",
            notes="Combination of removal and additions - different modification types"
        ))

        # Test Case 7: Subtle multi-modification (challenging)
        test_cases.append(GroundTruthEntry(
            id="test_007_subtle_multi",
            review_text="The original recipe was too sweet so I reduced sugar by 1/4 cup. I also found it needed more structure so I added an extra tablespoon of flour.",
            recipe_data={
                "title": "Cake",
                "ingredients": [
                    "2 cups flour",
                    "1.5 cups sugar",
                    "1/2 cup oil",
                    "2 eggs",
                    "1 cup milk"
                ],
                "instructions": [
                    "Mix dry ingredients",
                    "Combine wet ingredients",
                    "Mix together",
                    "Bake at 350°F"
                ]
            },
            expected_modifications=[
                {
                    "type": "quantity_adjustment",
                    "reasoning": "reduce sweetness level",
                    "target": "ingredients",
                    "description": "reduce sugar by 1/4 cup"
                },
                {
                    "type": "quantity_adjustment",
                    "reasoning": "improve cake structure",
                    "target": "ingredients",
                    "description": "add 1 tablespoon more flour"
                }
            ],
            expected_count=2,
            difficulty_level="medium",
            notes="Two modifications in separate sentences - tests parsing across sentence boundaries"
        ))

        # Test Case 8: Single modification (control case)
        test_cases.append(GroundTruthEntry(
            id="test_008_single_mod",
            review_text="I added 1/2 cup of mini chocolate chips to make them more chocolatey. Turned out great!",
            recipe_data={
                "title": "Vanilla Cookies",
                "ingredients": [
                    "2 cups flour",
                    "1 cup sugar",
                    "1/2 cup butter",
                    "1 egg"
                ],
                "instructions": [
                    "Mix ingredients",
                    "Form cookies",
                    "Bake 10 minutes"
                ]
            },
            expected_modifications=[
                {
                    "type": "addition",
                    "reasoning": "add chocolate for flavor",
                    "target": "ingredients",
                    "description": "add 1/2 cup mini chocolate chips"
                }
            ],
            expected_count=1,
            difficulty_level="simple",
            notes="Control case with single clear modification"
        ))

        # Test Case 9: Complex substitution with quantity change
        test_cases.append(GroundTruthEntry(
            id="test_009_complex_sub",
            review_text="Instead of 2 cups white flour I used 1.5 cups whole wheat flour and 0.5 cups almond flour. Also replaced white sugar with 3/4 cup coconut sugar.",
            recipe_data={
                "title": "Healthy Muffins",
                "ingredients": [
                    "2 cups all-purpose flour",
                    "1 cup white sugar",
                    "1/2 cup oil",
                    "2 eggs",
                    "1 cup milk"
                ],
                "instructions": [
                    "Mix dry ingredients",
                    "Combine wet ingredients",
                    "Mix together",
                    "Bake at 375°F"
                ]
            },
            expected_modifications=[
                {
                    "type": "ingredient_substitution",
                    "reasoning": "substitute healthier flour blend",
                    "target": "ingredients",
                    "description": "replace 2 cups white flour with 1.5 cups whole wheat + 0.5 cups almond flour"
                },
                {
                    "type": "ingredient_substitution",
                    "reasoning": "use less processed sugar alternative",
                    "target": "ingredients",
                    "description": "replace white sugar with 3/4 cup coconut sugar"
                }
            ],
            expected_count=2,
            difficulty_level="complex",
            notes="Complex substitution involving multiple ingredients and quantity changes"
        ))

        # Test Case 10: Four modifications (stress test)
        test_cases.append(GroundTruthEntry(
            id="test_010_quad_mod",
            review_text="I made several changes: used butter instead of oil, added 1/2 tsp cinnamon, increased vanilla to 1 tablespoon, and baked at 325°F instead of 350°F for a more tender result.",
            recipe_data={
                "title": "Coffee Cake",
                "ingredients": [
                    "2 cups flour",
                    "1 cup sugar",
                    "1/2 cup vegetable oil",
                    "2 eggs",
                    "1 tsp vanilla",
                    "1 cup coffee"
                ],
                "instructions": [
                    "Mix dry ingredients",
                    "Combine wet ingredients",
                    "Mix together",
                    "Bake at 350°F for 45 minutes"
                ]
            },
            expected_modifications=[
                {
                    "type": "ingredient_substitution",
                    "reasoning": "substitute butter for oil",
                    "target": "ingredients",
                    "description": "replace vegetable oil with butter"
                },
                {
                    "type": "addition",
                    "reasoning": "add spice for flavor",
                    "target": "ingredients",
                    "description": "add 1/2 tsp cinnamon"
                },
                {
                    "type": "quantity_adjustment",
                    "reasoning": "increase vanilla flavor",
                    "target": "ingredients",
                    "description": "increase vanilla to 1 tablespoon"
                },
                {
                    "type": "technique_change",
                    "reasoning": "lower temperature for tenderness",
                    "target": "instructions",
                    "description": "change baking temperature to 325°F"
                }
            ],
            expected_count=4,
            difficulty_level="complex",
            notes="Four distinct modifications testing extraction limits - uses colon and commas"
        ))

        return test_cases

    def build_edge_case_test_dataset(self) -> List[GroundTruthEntry]:
        """
        Build edge case test dataset for challenging scenarios.

        Returns:
            List of edge case GroundTruthEntry objects
        """
        edge_cases = []

        # Edge Case 1: Ambiguous modification count
        edge_cases.append(GroundTruthEntry(
            id="edge_001_ambiguous",
            review_text="I changed the butter to coconut oil and the sugar to honey which made it healthier.",
            recipe_data={
                "title": "Basic Cookies",
                "ingredients": ["1 cup butter", "1 cup sugar", "2 cups flour"],
                "instructions": ["Mix and bake"]
            },
            expected_modifications=[
                {
                    "type": "ingredient_substitution",
                    "reasoning": "healthier fat substitute",
                    "target": "ingredients",
                    "description": "replace butter with coconut oil"
                },
                {
                    "type": "ingredient_substitution",
                    "reasoning": "healthier sweetener substitute",
                    "target": "ingredients",
                    "description": "replace sugar with honey"
                }
            ],
            expected_count=2,
            difficulty_level="medium",
            notes="Two substitutions in single clause - may be parsed as one"
        ))

        # Edge Case 2: No clear modifications despite review
        edge_cases.append(GroundTruthEntry(
            id="edge_002_no_mods",
            review_text="This recipe was perfect as written! I followed it exactly and everyone loved it. Will definitely make again.",
            recipe_data={
                "title": "Perfect Recipe",
                "ingredients": ["flour", "sugar", "eggs"],
                "instructions": ["Mix and bake"]
            },
            expected_modifications=[],
            expected_count=0,
            difficulty_level="simple",
            notes="Control case - review with no actual modifications"
        ))

        # Edge Case 3: Vague modifications
        edge_cases.append(GroundTruthEntry(
            id="edge_003_vague",
            review_text="I made a few adjustments to suit my taste and added some extra ingredients I had on hand.",
            recipe_data={
                "title": "Basic Recipe",
                "ingredients": ["flour", "sugar", "butter"],
                "instructions": ["Mix and bake"]
            },
            expected_modifications=[],
            expected_count=0,
            difficulty_level="complex",
            notes="Vague modifications without specific details - should extract 0"
        ))

        return edge_cases

    def get_complete_test_dataset(self) -> List[GroundTruthEntry]:
        """
        Get the complete test dataset including all test cases and edge cases.

        Returns:
            Complete list of all test cases
        """
        main_dataset = self.build_multi_modification_test_dataset()
        edge_cases = self.build_edge_case_test_dataset()

        return main_dataset + edge_cases

    def get_dataset_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the test dataset.

        Returns:
            Dictionary with dataset statistics
        """
        dataset = self.get_complete_test_dataset()

        difficulty_counts = {}
        modification_counts = {}
        total_expected_mods = 0

        for entry in dataset:
            # Count by difficulty
            difficulty = entry.difficulty_level
            difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1

            # Count by modification count
            count = entry.expected_count
            modification_counts[count] = modification_counts.get(count, 0) + 1
            total_expected_mods += count

        return {
            "total_test_cases": len(dataset),
            "total_expected_modifications": total_expected_mods,
            "average_modifications_per_case": total_expected_mods / len(dataset) if dataset else 0,
            "difficulty_distribution": difficulty_counts,
            "modification_count_distribution": modification_counts,
            "coverage": {
                "single_modifications": modification_counts.get(1, 0),
                "double_modifications": modification_counts.get(2, 0),
                "triple_modifications": modification_counts.get(3, 0),
                "quad_plus_modifications": sum(v for k, v in modification_counts.items() if k >= 4)
            }
        }