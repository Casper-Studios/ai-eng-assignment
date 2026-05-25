"""
Step 2: Recipe Modification

This module applies structured modifications to recipes using search-and-replace operations.
It takes ModificationObject instances and applies their edits to recipe ingredients and instructions.
"""

import copy
from difflib import SequenceMatcher
from typing import List, Optional, Tuple

from loguru import logger

from .models import (
    ModificationObject,
    ModificationEdit,
    Recipe,
    ChangeRecord
)


class RecipeModifier:
    """Applies structured modifications to recipes using search-and-replace operations."""

    def __init__(self, similarity_threshold: float = 0.6):
        """
        Initialize the RecipeModifier.

        Args:
            similarity_threshold: Minimum similarity score for fuzzy matching (0-1)
        """
        self.similarity_threshold = similarity_threshold
        logger.info(f"Initialized RecipeModifier with similarity threshold: {similarity_threshold}")

    def find_containing_match(
        self, target: str, candidates: List[str]
    ) -> Tuple[Optional[str], Optional[int], float]:
        """
        Find the first candidate that contains the target text as a substring.

        This catches common instruction edits where the LLM extracts a phrase like
        "about 10 minutes" but the recipe stores the full instruction sentence.

        Args:
            target: Text to locate within candidates
            candidates: List of recipe strings to search in

        Returns:
            Tuple of (matching_candidate, index, similarity_score)
        """
        target_lower = target.lower().strip()
        if not target_lower:
            return None, None, 0.0

        for i, candidate in enumerate(candidates):
            candidate_lower = candidate.lower()
            if target_lower in candidate_lower:
                similarity = SequenceMatcher(None, target_lower, candidate_lower).ratio()
                return candidate, i, similarity

        return None, None, 0.0

    def replace_case_insensitive(self, text: str, find: str, replace: str) -> str:
        """Replace the first case-insensitive occurrence of find within text."""
        text_lower = text.lower()
        find_lower = find.lower()
        start = text_lower.find(find_lower)

        if start == -1:
            return text

        end = start + len(find)
        return text[:start] + replace + text[end:]

    def find_best_match(self, target: str, candidates: List[str]) -> Tuple[Optional[str], Optional[int], float]:
        """
        Find the best matching string in a list of candidates.

        Args:
            target: String to find
            candidates: List of strings to search in

        Returns:
            Tuple of (best_match, index, similarity_score)
        """
        if not candidates:
            return None, None, 0.0

        best_match = None
        best_index = None
        best_score = 0.0

        for i, candidate in enumerate(candidates):
            similarity = SequenceMatcher(None, target.lower(), candidate.lower()).ratio()
            if similarity > best_score:
                best_score = similarity
                best_match = candidate
                best_index = i

        if best_score >= self.similarity_threshold:
            return best_match, best_index, best_score
        else:
            return None, None, best_score

    def apply_edit(
        self,
        edit: ModificationEdit,
        recipe_content: List[str]
    ) -> Tuple[List[str], List[ChangeRecord]]:
        """
        Apply a single edit to a recipe content list.

        Args:
            edit: The edit operation to apply
            recipe_content: List of ingredients or instructions

        Returns:
            Tuple of (modified_content, change_records)
        """
        modified_content = copy.deepcopy(recipe_content)
        change_records = []

        logger.debug(f"Applying {edit.operation} edit: find='{edit.find}'")

        if edit.operation == "replace":
            # Prefer substring matches within a recipe line before fuzzy line matching.
            match, index, score = self.find_containing_match(edit.find, modified_content)

            if not match:
                match, index, score = self.find_best_match(edit.find, modified_content)

            if match and index is not None:
                original_text = modified_content[index]

                if edit.find in original_text:
                    new_text = original_text.replace(edit.find, edit.replace or "", 1)
                else:
                    new_text = self.replace_case_insensitive(
                        original_text, edit.find, edit.replace or ""
                    )

                if new_text == original_text and score >= self.similarity_threshold:
                    new_text = edit.replace or ""

                modified_content[index] = new_text

                change_records.append(ChangeRecord(
                    type="ingredient" if edit.target == "ingredients" else "instruction",
                    from_text=original_text,
                    to_text=new_text,
                    operation="replace"
                ))

                logger.info(f"Replaced '{edit.find}' with '{edit.replace}' (similarity: {score:.2f})")
            else:
                logger.warning(f"Could not find '{edit.find}' in {edit.target} (best similarity: {score:.2f})")

        elif edit.operation == "add_after":
            # Add new content after finding target
            match, index, score = self.find_best_match(edit.find, modified_content)

            if match and index is not None and edit.add:
                modified_content.insert(index + 1, edit.add)

                change_records.append(ChangeRecord(
                    type="ingredient" if edit.target == "ingredients" else "instruction",
                    from_text="",
                    to_text=edit.add,
                    operation="add"
                ))

                logger.info(f"Added '{edit.add}' after '{edit.find}' (similarity: {score:.2f})")
            else:
                logger.warning(f"Could not find target '{edit.find}' for addition")

        elif edit.operation == "remove":
            # Remove matching content
            match, index, score = self.find_best_match(edit.find, modified_content)

            if match and index is not None:
                removed_text = modified_content.pop(index)

                change_records.append(ChangeRecord(
                    type="ingredient" if edit.target == "ingredients" else "instruction",
                    from_text=removed_text,
                    to_text="",
                    operation="remove"
                ))

                logger.info(f"Removed '{edit.find}' (similarity: {score:.2f})")
            else:
                logger.warning(f"Could not find '{edit.find}' to remove")

        return modified_content, change_records

    def apply_modification(
        self,
        recipe: Recipe,
        modification: ModificationObject
    ) -> Tuple[Recipe, List[ChangeRecord]]:
        """
        Apply a complete modification to a recipe.

        Args:
            recipe: Original recipe to modify
            modification: Structured modification to apply

        Returns:
            Tuple of (modified_recipe, all_change_records)
        """
        logger.info(f"Applying {modification.modification_type} with {len(modification.edits)} edits")

        # Deep copy the recipe
        modified_recipe = Recipe(
            recipe_id=f"{recipe.recipe_id}_modified",
            title=recipe.title,
            ingredients=copy.deepcopy(recipe.ingredients),
            instructions=copy.deepcopy(recipe.instructions),
            description=recipe.description,
            servings=recipe.servings,
            rating=recipe.rating
        )

        all_change_records = []

        # Apply each edit
        for edit in modification.edits:
            if edit.target == "ingredients":
                modified_recipe.ingredients, change_records = self.apply_edit(
                    edit, modified_recipe.ingredients
                )
            elif edit.target == "instructions":
                modified_recipe.instructions, change_records = self.apply_edit(
                    edit, modified_recipe.instructions
                )
            else:
                logger.warning(f"Unknown edit target: {edit.target}")
                continue

            all_change_records.extend(change_records)

        logger.info(f"Applied modification successfully: {len(all_change_records)} changes made")
        return modified_recipe, all_change_records

    def apply_modifications_batch(
        self,
        recipe: Recipe,
        modifications: List[ModificationObject]
    ) -> Tuple[Recipe, List[List[ChangeRecord]]]:
        """
        Apply multiple modifications to a recipe sequentially.

        Args:
            recipe: Original recipe to modify
            modifications: List of modifications to apply

        Returns:
            Tuple of (final_modified_recipe, list_of_change_records_per_modification)
        """
        current_recipe = recipe
        all_change_records = []

        logger.info(f"Applying {len(modifications)} modifications sequentially")

        for i, modification in enumerate(modifications):
            logger.info(f"Applying modification {i + 1}/{len(modifications)}: {modification.modification_type}")

            current_recipe, change_records = self.apply_modification(current_recipe, modification)
            all_change_records.append(change_records)

        logger.info(f"Applied all modifications. Final recipe has {len(current_recipe.ingredients)} ingredients and {len(current_recipe.instructions)} instructions")
        return current_recipe, all_change_records

    def validate_modification_safety(
        self,
        modification: ModificationObject,
        recipe: Recipe
    ) -> Tuple[bool, List[str]]:
        """
        Validate that a modification won't break the recipe.

        Args:
            modification: Modification to validate
            recipe: Recipe being modified

        Returns:
            Tuple of (is_safe, list_of_warnings)
        """
        warnings = []
        is_safe = True

        for edit in modification.edits:
            # Check if target content exists
            target_content = recipe.ingredients if edit.target == "ingredients" else recipe.instructions
            match, _, score = self.find_best_match(edit.find, target_content)

            if not match:
                warnings.append(f"Cannot find '{edit.find}' in {edit.target}")
                is_safe = False
            elif score < 0.8:
                warnings.append(f"Low similarity match for '{edit.find}' (score: {score:.2f})")

            # Check for required fields
            if edit.operation == "replace" and not edit.replace:
                warnings.append(f"Replace operation missing replacement text for '{edit.find}'")
                is_safe = False
            elif edit.operation == "add_after" and not edit.add:
                warnings.append(f"Add operation missing text to add after '{edit.find}'")
                is_safe = False

        return is_safe, warnings