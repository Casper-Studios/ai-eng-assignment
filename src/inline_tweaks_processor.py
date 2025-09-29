"""
Inline Tweaks Processor

This module transforms enhanced recipe data to include featured tweaks
inline with the specific ingredients they modify, making it easier to
see which tweaks apply to which ingredients.
"""

import json
import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InlineTweaksProcessor:
    """Processes enhanced recipes to inline tweaks with ingredients."""

    def __init__(self):
        """Initialize the processor."""
        self.ingredient_patterns = {
            'egg': ['egg', 'yolk', 'white'],
            'sugar': ['sugar', 'brown sugar', 'white sugar'],
            'butter': ['butter'],
            'flour': ['flour', 'all-purpose flour'],
            'vanilla': ['vanilla'],
            'chocolate': ['chocolate chip', 'chips'],
            'nuts': ['walnut', 'nuts'],
            'salt': ['salt'],
            'baking_soda': ['baking soda'],
            'water': ['water'],
            'cream_of_tartar': ['cream of tartar'],
            'cinnamon': ['cinnamon']
        }

    def extract_ingredient_info(self, ingredient: str) -> Dict[str, Any]:
        """
        Extract structured information from an ingredient string.

        Args:
            ingredient: Raw ingredient string

        Returns:
            Dictionary with ingredient information
        """
        # Basic parsing of quantity, unit, and ingredient
        # Pattern: number/fraction + unit + ingredient
        pattern = r'^([\d./\s]+)?\s*([a-zA-Z]*)\s+(.+)$'
        match = re.match(pattern, ingredient.strip())

        if match:
            quantity = match.group(1).strip() if match.group(1) else "1"
            unit = match.group(2).strip() if match.group(2) else ""
            name = match.group(3).strip()
        else:
            quantity = ""
            unit = ""
            name = ingredient.strip()

        return {
            'original': ingredient,
            'quantity': quantity,
            'unit': unit,
            'name': name,
            'category': self._categorize_ingredient(name)
        }

    def _categorize_ingredient(self, ingredient_name: str) -> Optional[str]:
        """Categorize an ingredient based on its name."""
        ingredient_lower = ingredient_name.lower()

        # Order matters - check more specific patterns first
        priority_patterns = [
            ('sugar', ['white sugar', 'brown sugar', 'sugar']),
            ('egg', ['egg yolk', 'egg white', 'egg']),
            ('chocolate', ['chocolate chip', 'chips', 'chocolate']),
            ('nuts', ['walnut', 'nuts']),
            ('flour', ['all-purpose flour', 'flour']),
            ('butter', ['butter']),
            ('vanilla', ['vanilla']),
            ('salt', ['salt']),
            ('baking_soda', ['baking soda']),
            ('water', ['water']),
            ('cream_of_tartar', ['cream of tartar']),
            ('cinnamon', ['cinnamon'])
        ]

        for category, patterns in priority_patterns:
            for pattern in patterns:
                if pattern in ingredient_lower:
                    return category
        return None

    def match_tweak_to_ingredients(self, tweak: Dict[str, Any], ingredients: List[str]) -> List[int]:
        """
        Match a tweak to the ingredient indices it modifies.

        Args:
            tweak: Featured tweak dictionary
            ingredients: List of ingredient strings

        Returns:
            List of ingredient indices that this tweak modifies
        """
        tweak_text = tweak['text'].lower()
        matched_indices = []

        # Parse ingredients for matching
        ingredient_infos = [self.extract_ingredient_info(ing) for ing in ingredients]

        # Specific high-priority matching patterns
        specific_matches = {
            'egg yolk': ['additional egg yolk', 'egg yolk'],
            'half cup of sugar': ['white sugar'],
            'one-and-a-half cups of brown sugar': ['brown sugar'],
            'whole cup of white sugar': ['white sugar'],
            '1/2 c of brown': ['brown sugar'],
            'omitted the water': ['water'],
            'omitted the nuts': ['walnut', 'nuts'],
            '1 tsp. of salt': ['salt'],
            '1/2 c less flour': ['flour'],
            'cream of tartar': [],  # Not in ingredients but mentioned
            'cinnamon': []  # Not in original ingredients
        }

        # Apply specific matches first
        for pattern, target_ingredients in specific_matches.items():
            if pattern in tweak_text:
                for i, ing_info in enumerate(ingredient_infos):
                    name_lower = ing_info['name'].lower()
                    for target in target_ingredients:
                        if target in name_lower:
                            matched_indices.append(i)

        # General pattern matching for remaining cases
        for i, ing_info in enumerate(ingredient_infos):
            if i in matched_indices:
                continue  # Skip already matched

            category = ing_info['category']
            name = ing_info['name'].lower()

            # Sugar-specific matching
            if category == 'sugar':
                if ('sugar' in tweak_text and
                    ('white' in name and 'white' in tweak_text) or
                    ('brown' in name and 'brown' in tweak_text)):
                    matched_indices.append(i)

            # Egg-specific matching
            elif category == 'egg':
                if 'egg' in tweak_text:
                    matched_indices.append(i)

            # Salt-specific matching
            elif category == 'salt':
                if 'salt' in tweak_text:
                    matched_indices.append(i)

            # Nuts-specific matching
            elif category == 'nuts':
                if any(word in tweak_text for word in ['nuts', 'walnut']):
                    matched_indices.append(i)

            # Water-specific matching
            elif category == 'water':
                if 'water' in tweak_text:
                    matched_indices.append(i)

            # Flour-specific matching
            elif category == 'flour':
                if 'flour' in tweak_text:
                    matched_indices.append(i)

        return list(set(matched_indices))  # Remove duplicates

    def create_inline_ingredients(self, recipe_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create new ingredients structure with inline tweaks.

        Args:
            recipe_data: Enhanced recipe data

        Returns:
            List of ingredient objects with inline tweaks
        """
        ingredients = recipe_data.get('ingredients', [])
        featured_tweaks = recipe_data.get('featured_tweaks', [])

        # Create ingredient objects with inline tweaks
        inline_ingredients = []

        for i, ingredient in enumerate(ingredients):
            ing_info = self.extract_ingredient_info(ingredient)

            # Find tweaks that apply to this ingredient
            applicable_tweaks = []
            for tweak in featured_tweaks:
                matched_indices = self.match_tweak_to_ingredients(tweak, ingredients)
                if i in matched_indices:
                    applicable_tweaks.append({
                        'text': tweak['text'],
                        'rating': tweak['rating'],
                        'modification_type': self._infer_modification_type(tweak['text'], ingredient)
                    })

            ingredient_obj = {
                'original_text': ingredient,
                'quantity': ing_info['quantity'],
                'unit': ing_info['unit'],
                'name': ing_info['name'],
                'category': ing_info['category'],
                'featured_tweaks': applicable_tweaks
            }

            inline_ingredients.append(ingredient_obj)

        return inline_ingredients

    def _infer_modification_type(self, tweak_text: str, ingredient: str) -> str:
        """Infer the type of modification from tweak text."""
        tweak_lower = tweak_text.lower()

        if 'add' in tweak_lower or 'additional' in tweak_lower:
            return 'addition'
        elif 'omit' in tweak_lower or 'without' in tweak_lower:
            return 'removal'
        elif 'instead' in tweak_lower or 'substitute' in tweak_lower:
            return 'substitution'
        elif any(word in tweak_lower for word in ['more', 'less', 'cup', 'teaspoon', 'tablespoon']):
            return 'quantity_adjustment'
        else:
            return 'technique_change'

    def process_recipe(self, recipe_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single recipe to inline tweaks with ingredients.

        Args:
            recipe_data: Enhanced recipe data

        Returns:
            Recipe data with inline tweaks
        """
        logger.info(f"Processing recipe: {recipe_data.get('title', 'Unknown')}")

        # Create new structure
        processed_data = recipe_data.copy()

        # Create inline ingredients
        inline_ingredients = self.create_inline_ingredients(recipe_data)

        # Replace ingredients with inline structure
        processed_data['enhanced_ingredients'] = inline_ingredients

        # Keep original ingredients for reference
        processed_data['original_ingredients'] = recipe_data.get('ingredients', [])

        # Add processing metadata
        processed_data['processing_info'] = {
            'inline_tweaks_version': '1.0.0',
            'total_ingredients': len(inline_ingredients),
            'ingredients_with_tweaks': len([ing for ing in inline_ingredients if ing['featured_tweaks']]),
            'processing_method': 'automatic_matching'
        }

        logger.info(f"Created {len(inline_ingredients)} inline ingredients, "
                   f"{len([ing for ing in inline_ingredients if ing['featured_tweaks']])} with tweaks")

        return processed_data

    def process_file(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        Process a single enhanced recipe file.

        Args:
            input_path: Path to input JSON file
            output_path: Path for output file (optional)

        Returns:
            Path to output file
        """
        input_file = Path(input_path)

        if output_path is None:
            output_path = input_file.parent / f"inline_{input_file.name}"

        # Load recipe data
        with open(input_path, 'r', encoding='utf-8') as f:
            recipe_data = json.load(f)

        # Process the recipe
        processed_data = self.process_recipe(recipe_data)

        # Save processed data
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved processed recipe to: {output_path}")
        return str(output_path)

    def process_directory(self, input_dir: str, output_dir: Optional[str] = None) -> List[str]:
        """
        Process all enhanced recipe files in a directory.

        Args:
            input_dir: Directory containing enhanced recipe files
            output_dir: Output directory (optional)

        Returns:
            List of output file paths
        """
        input_path = Path(input_dir)

        if output_dir is None:
            output_dir = input_path / "inline_processed"

        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        processed_files = []

        # Find all enhanced JSON files
        for json_file in input_path.glob("enhanced_*.json"):
            output_file = output_path / f"inline_{json_file.name}"
            result_path = self.process_file(str(json_file), str(output_file))
            processed_files.append(result_path)

        logger.info(f"Processed {len(processed_files)} files")
        return processed_files


def main():
    """Main function for command line usage."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python inline_tweaks_processor.py <input_file_or_directory>")
        sys.exit(1)

    input_path = sys.argv[1]
    processor = InlineTweaksProcessor()

    if Path(input_path).is_file():
        output_path = processor.process_file(input_path)
        print(f"Processed file saved to: {output_path}")
    elif Path(input_path).is_dir():
        output_files = processor.process_directory(input_path)
        print(f"Processed {len(output_files)} files")
        for file_path in output_files:
            print(f"  - {file_path}")
    else:
        print(f"Error: {input_path} is not a valid file or directory")
        sys.exit(1)


if __name__ == "__main__":
    main()