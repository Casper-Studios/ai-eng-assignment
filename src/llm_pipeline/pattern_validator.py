"""
Rule-Based Pattern Validator for Missed Modifications

This module uses regex patterns and keyword matching to catch
commonly missed modifications that the LLM might skip.
"""

import re
from typing import List, Optional

from loguru import logger

from .models import ModificationObject, ModificationEdit


class PatternValidator:
    """Validate and supplement LLM extractions with rule-based patterns."""

    def __init__(self):
        """Initialize the PatternValidator."""
        self.missed_patterns = {
            'finishing_touches': [
                r'drizzled?\s+(?:with\s+)?(\w+(?:\s+\w+)?)',
                r'dash\s+(?:of\s+)?(\w+(?:\s+\w+)?)',
                r'pinch\s+(?:of\s+)?(\w+(?:\s+\w+)?)',
                r'sprinkled?\s+(?:with\s+)?(\w+(?:\s+\w+)?)',
                r'topped?\s+(?:with\s+)?(\w+(?:\s+\w+)?)',
                r'garnished?\s+(?:with\s+)?(\w+(?:\s+\w+)?)',
            ],
            'milk_cream_substitutions': [
                r'(?:used|substituted|instead\s+of)\s+(?:\d%\s+)?(?:milk|cream|half-?-?\s*and-?\s*half)',
                r'(?:with\s+)?(?:\d%?\s*)?(?:milk|cream|half\s*and\s*half)(?:\s+instead)',
            ],
            'spice_additions': [
                r'added\s+(?:a\s+)?(?:tiny|small|little|bit)\s+(?:of\s+)?(\w+\s+(?:powder|cinnamon|ginger|nutmeg|clove|allspice))',
                r'splash\s+(?:of\s+)?(\w+(?:\s+\w+)?)',
            ],
            'broth_liquid_adjustments': [
                r'(?:more|less|extra)\s+(?:broth|stock|water|liquid)',
                r'will\s+use\s+(?:more|less)\s+(?:broth|stock|water)',
            ],
        }

        logger.info("Initialized PatternValidator")

    def find_missed_modifications(
        self,
        review_text: str,
        extracted_edits: List[ModificationEdit]
    ) -> List[dict]:
        """
        Find modifications that may have been missed by LLM extraction.

        Args:
            review_text: Original review text
            extracted_edits: Edits already extracted by LLM

        Returns:
            List of potential missed modifications with details
        """
        missed = []

        # Get list of already captured ingredients/changes
        captured_texts = set()
        for edit in extracted_edits:
            captured_texts.add(edit.find.lower())
            if edit.replace:
                captured_texts.add(edit.replace.lower())
            if edit.add:
                captured_texts.add(edit.add.lower())

        # Check each pattern category
        for category, patterns in self.missed_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, review_text, re.IGNORECASE)
                for match in matches:
                    matched_text = match.group(0).lower()

                    # Check if this was already captured
                    if not any(captured in matched_text for captured in captured_texts):
                        missed.append({
                            'category': category,
                            'matched_text': match.group(0),
                            'full_match': match.group(),
                            'suggested_operation': self._infer_operation(match.group(0)),
                        })

        if missed:
            logger.info(f"Found {len(missed)} potentially missed modifications")

        return missed

    def _infer_operation(self, text: str) -> str:
        """Infer the likely operation type from matched text."""
        text_lower = text.lower()

        if any(word in text_lower for word in ['drizzled', 'dash', 'pinch', 'sprinkled', 'topped', 'added']):
            return 'add_after'
        elif any(word in text_lower for word in ['used', 'substituted', 'instead', 'with', 'more', 'less']):
            return 'replace'
        else:
            return 'add_after'

    def create_supplemental_edits(
        self,
        missed_modifications: List[dict],
        recipe_ingredients: List[str]
    ) -> List[ModificationEdit]:
        """
        Create supplemental edits from missed modifications.

        Args:
            missed_modifications: List of missed modifications from pattern matching
            recipe_ingredients: Original recipe ingredients for context

        Returns:
            List of ModificationEdit objects
        """
        edits = []

        for missed in missed_modifications:
            operation = missed['suggested_operation']
            matched_text = missed['matched_text']

            # Try to find a good anchor point in ingredients
            anchor = self._find_anchor_point(matched_text, recipe_ingredients)

            if anchor:
                edit = ModificationEdit(
                    target="ingredients",
                    operation=operation,
                    find=anchor,
                    replace=matched_text if operation == "replace" else None,
                    add=matched_text if operation == "add_after" else None
                )
                edits.append(edit)
                logger.info(f"Created supplemental edit: {operation} '{matched_text}' after '{anchor}'")

        return edits

    def _find_anchor_point(self, text: str, ingredients: List[str]) -> Optional[str]:
        """Find the best anchor point in ingredients for adding a modification."""
        text_lower = text.lower()

        # If it's a finishing touch, anchor after the last ingredient
        if any(word in text_lower for word in ['drizzled', 'topped', 'sprinkled', 'garnished']):
            if ingredients:
                return ingredients[-1]

        # If it's a liquid/cream, find similar ingredients
        if any(word in text_lower for word in ['milk', 'cream', 'broth', 'liquid']):
            for ingredient in ingredients:
                if any(word in ingredient.lower() for word in ['milk', 'cream', 'broth', 'liquid']):
                    return ingredient

        # If it's a spice, find other spices
        if any(word in text_lower for word in ['cinnamon', 'ginger', 'nutmeg', 'clove', 'powder']):
            for ingredient in ingredients:
                if any(word in ingredient.lower() for word in ['sugar', 'salt', 'spice', 'cinnamon', 'ginger']):
                    return ingredient

        # Default: return first ingredient
        return ingredients[0] if ingredients else None

    def supplement_extraction(
        self,
        review_text: str,
        modification: ModificationObject,
        recipe_ingredients: List[str]
    ) -> ModificationObject:
        """
        Supplement LLM extraction with rule-based pattern matching.

        Args:
            review_text: Original review text
            modification: Modification extracted by LLM
            recipe_ingredients: Original recipe ingredients

        Returns:
            Supplemented ModificationObject with additional edits
        """
        # Find missed modifications
        missed = self.find_missed_modifications(review_text, modification.edits)

        if not missed:
            return modification

        # Create supplemental edits
        supplemental_edits = self.create_supplemental_edits(missed, recipe_ingredients)

        if not supplemental_edits:
            return modification

        # Merge edits (avoiding duplicates)
        all_edits = modification.edits.copy()
        seen = {(e.target, e.operation, e.find) for e in all_edits}

        for edit in supplemental_edits:
            key = (edit.target, edit.operation, edit.find)
            if key not in seen:
                seen.add(key)
                all_edits.append(edit)

        logger.info(f"Supplemented extraction: {len(modification.edits)} → {len(all_edits)} edits")

        return ModificationObject(
            modification_type=modification.modification_type,
            reasoning=modification.reasoning,
            edits=all_edits
        )
