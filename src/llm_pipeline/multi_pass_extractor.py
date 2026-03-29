"""
Multi-Pass Extraction for Comprehensive Modification Capture

This module implements a multi-pass extraction strategy to capture
all types of modifications from reviews, including:
- Main ingredient substitutions
- Quantity adjustments
- Minor additions (spices, garnishes, finishing touches)
- Technique changes
"""

import json
from typing import List, Optional

from loguru import logger

from .models import ModificationObject, Recipe, Review
from .prompts import build_simple_prompt
from .quality_scorer import QualityScorer


class MultiPassExtractor:
    """Extract modifications using multiple targeted passes."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the MultiPassExtractor.

        Args:
            api_key: OpenAI API key
            model: OpenAI model to use
        """
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.scorer = QualityScorer()
        logger.info(f"Initialized MultiPassExtractor with model: {model}")

    def extract_with_passes(
        self,
        review: Review,
        recipe: Recipe,
        passes: int = 3
    ) -> List[ModificationObject]:
        """
        Extract modifications using multiple passes with different focuses.

        Pass 1: Main ingredients and quantities
        Pass 2: Spices, garnishes, and finishing touches
        Pass 3: Technique changes and special instructions

        Args:
            review: Review to extract from
            recipe: Original recipe
            passes: Number of extraction passes

        Returns:
            List of all extracted modifications (deduplicated)
        """
        all_modifications = []

        pass_prompts = [
            # Pass 1: Main ingredients
            build_simple_prompt(
                review.text,
                recipe.title,
                recipe.ingredients,
                recipe.instructions
            ) + "\n\nFocus on main ingredients and quantity adjustments.",
        ]

        # Pass 2: Minor additions
        pass_prompts.append(
            build_simple_prompt(
                review.text,
                recipe.title,
                recipe.ingredients,
                recipe.instructions
            ) + "\n\nFocus on catching minor additions like spices, garnishes, "
            "finishing touches (e.g., 'drizzled with', 'dash of', 'pinch of', "
            "'sprinkled', 'topped with'). Extract these even if they seem minor."
        )

        # Pass 3: Technique changes
        pass_prompts.append(
            build_simple_prompt(
                review.text,
                recipe.title,
                recipe.ingredients,
                recipe.instructions
            ) + "\n\nFocus on technique changes like cooking methods, temperatures, "
            "times, and special instructions."
        )

        for i, prompt in enumerate(pass_prompts[:passes], 1):
            logger.debug(f"Pass {i}/{passes}: Extracting with focused prompt")

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    temperature=0.3,
                    max_tokens=1500,
                )

                raw_output = response.choices[0].message.content
                if raw_output:
                    modification_data = json.loads(raw_output)
                    modification = ModificationObject(**modification_data)

                    if modification.edits:
                        logger.info(
                            f"Pass {i}: Extracted {len(modification.edits)} edits "
                            f"({modification.modification_type})"
                        )
                        all_modifications.append(modification)
                    else:
                        logger.debug(f"Pass {i}: No edits extracted")

            except Exception as e:
                logger.warning(f"Pass {i} failed: {e}")
                continue

        # Merge and deduplicate modifications
        merged = self._merge_modifications(all_modifications)
        logger.info(f"Merged {len(all_modifications)} passes into {len(merged.edits)} total edits")

        return [merged] if merged.edits else []

    def _merge_modifications(self, modifications: List[ModificationObject]) -> ModificationObject:
        """
        Merge multiple modification objects into one comprehensive modification.

        Args:
            modifications: List of modifications to merge

        Returns:
            Single merged ModificationObject
        """
        if not modifications:
            return ModificationObject(
                modification_type="addition",
                reasoning="No modifications extracted",
                edits=[]
            )

        if len(modifications) == 1:
            return modifications[0]

        # Merge all edits
        all_edits = []
        seen_edits = set()

        for mod in modifications:
            for edit in mod.edits:
                # Create a unique key for deduplication
                edit_key = (edit.target, edit.operation, edit.find, edit.replace or edit.add or "")
                if edit_key not in seen_edits:
                    seen_edits.add(edit_key)
                    all_edits.append(edit)

        # Use the first modification's type and reasoning
        primary = modifications[0]

        return ModificationObject(
            modification_type=primary.modification_type,
            reasoning=primary.reasoning,
            edits=all_edits
        )

    def extract_all_modifications_multi_pass(
        self,
        reviews: List[Review],
        recipe: Recipe,
        min_rating: int = 4,
        min_quality_score: float = 0.75
    ) -> List[tuple[ModificationObject, Review]]:
        """
        Extract modifications from all reviews using multi-pass strategy.

        Args:
            reviews: List of reviews to process
            recipe: Original recipe
            min_rating: Minimum star rating
            min_quality_score: Minimum quality score

        Returns:
            List of (ModificationObject, Review) tuples
        """
        # Filter by rating and modification flag
        rating_filtered = [
            r for r in reviews
            if r.has_modification and r.rating is not None and r.rating >= min_rating
        ]

        if not rating_filtered:
            logger.warning(f"No reviews with rating >= {min_rating} found")
            return []

        logger.info(
            f"Multi-pass extraction: {len(rating_filtered)} reviews with rating >= {min_rating}"
        )

        results = []

        for review in rating_filtered:
            logger.debug(f"Processing {review.rating}★ review with multi-pass extraction")

            # Extract with multiple passes
            modifications = self.extract_with_passes(review, recipe, passes=3)

            if modifications:
                modification = modifications[0]  # Already merged

                # Calculate quality score
                review.text_length = len(review.text) if review.text else 0
                quality_score = self.scorer.calculate_review_quality_score(review, modification)
                review.quality_score = quality_score

                if quality_score >= min_quality_score:
                    results.append((modification, review))
                    logger.info(
                        f"✓ Extracted {len(modification.edits)} edits "
                        f"(quality={quality_score:.2f})"
                    )
                else:
                    logger.debug(
                        f"✗ Low quality score: {quality_score:.2f} "
                        f"(threshold={min_quality_score})"
                    )

        logger.info(f"Multi-pass extraction complete: {len(results)} high-quality modifications")
        return results
