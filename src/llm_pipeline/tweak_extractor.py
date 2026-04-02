"""
Step 1: Tweak Extraction & Parsing

This module extracts structured modifications from review text using LLM processing.
It converts natural language descriptions of recipe changes into structured
ModificationObject instances.
"""

import json
import os
from typing import Optional

from loguru import logger
from openai import OpenAI
from pydantic import ValidationError

from .models import ModificationObject, Recipe, Review
from .prompts import build_simple_prompt


class TweakExtractor:
    """Extracts structured modifications from review text using LLM processing."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the TweakExtractor.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: OpenAI model to use for extraction
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        logger.info(f"Initialized TweakExtractor with model: {model}")

    def extract_modification(
        self,
        review: Review,
        recipe: Recipe,
        max_retries: int = 2,
    ) -> Optional[ModificationObject]:
        """
        Extract a structured modification from a review.

        Args:
            review: Review object containing modification text
            recipe: Original recipe being modified
            max_retries: Number of retry attempts if parsing fails

        Returns:
            ModificationObject if extraction successful, None otherwise
        """
        if not review.has_modification:
            logger.warning("Review has no modification flag set")
            return None

        # Build the prompt - use simple prompt to avoid format string issues
        prompt = build_simple_prompt(
            review.text, recipe.title, recipe.ingredients, recipe.instructions
        )

        logger.debug(
            "Extracting modification from review: {}...".format(review.text[:100])
        )

        for attempt in range(max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    temperature=0.1,  # Low temperature for consistent extractions
                    max_tokens=1000,
                )

                raw_output = response.choices[0].message.content
                logger.debug(f"LLM raw output: {raw_output}")

                # Check if we got a response
                if not raw_output:
                    logger.warning(f"Attempt {attempt + 1}: Empty response from LLM")
                    continue

                # Parse and validate the JSON response
                modification_data = json.loads(raw_output)
                modification = ModificationObject(**modification_data)

                logger.info(
                    f"Successfully extracted {modification.modification_type} "
                    f"modification with {len(modification.edits)} edits"
                )
                return modification

            except json.JSONDecodeError as e:
                logger.warning(f"Attempt {attempt + 1}: Failed to parse JSON: {e}")
                if attempt == max_retries:
                    logger.error(f"Max retries reached. Raw output: {raw_output}")

            except ValidationError as e:
                logger.warning(f"Attempt {attempt + 1}: Validation error: {e}")
                if attempt == max_retries:
                    logger.error(
                        f"Max retries reached. Invalid data: {modification_data}"
                    )

            except Exception as e:
                logger.error(f"Attempt {attempt + 1}: Unexpected error: {e}")
                if attempt == max_retries:
                    return None

        return None

    def extract_multiple_modifications(
        self, reviews: list[Review], recipe: Recipe, limit: int = 3
    ) -> list[tuple[ModificationObject, Review]]:
        """
        Extract modifications from the first N reviews with modification flags.

        Args:
            reviews: List of reviews to process
            recipe: Original recipe being modified
            limit: Maximum number of modification reviews to process

        Returns:
            List of tuples: (ModificationObject, source_review)
        """
        if limit <= 0:
            logger.warning(f"Invalid limit={limit}; returning no modifications")
            return []

        modification_reviews = [r for r in reviews if r.has_modification][:limit]

        if not modification_reviews:
            logger.warning("No reviews with modifications found")
            return []

        logger.info(
            f"Processing {len(modification_reviews)} review(s) for modification extraction"
        )

        modifications_with_reviews: list[tuple[ModificationObject, Review]] = []
        for index, selected_review in enumerate(modification_reviews, start=1):
            logger.info(
                f"Processing review {index}/{len(modification_reviews)}: "
                f"{selected_review.text[:100]}..."
            )

            modification = self.extract_modification(selected_review, recipe)
            if modification:
                logger.info("Successfully extracted modification from review")
                modifications_with_reviews.append((modification, selected_review))
            else:
                logger.warning("Failed to extract modification from review")

        logger.info(
            f"Extracted {len(modifications_with_reviews)} valid modification(s) "
            f"from {len(modification_reviews)} processed review(s)"
        )
        return modifications_with_reviews

    def extract_single_modification(
        self, reviews: list[Review], recipe: Recipe
    ) -> tuple[ModificationObject, Review] | tuple[None, None]:
        """Backward-compatible wrapper around multi-review extraction."""
        modifications_with_reviews = self.extract_multiple_modifications(
            reviews, recipe, limit=1
        )
        if not modifications_with_reviews:
            return None, None
        return modifications_with_reviews[0]

    def test_extraction(
        self, review_text: str, recipe_data: dict
    ) -> Optional[ModificationObject]:
        """
        Test extraction with raw text and recipe data.

        Args:
            review_text: Raw review text
            recipe_data: Raw recipe dictionary

        Returns:
            ModificationObject if successful
        """
        review = Review(text=review_text, has_modification=True)
        recipe = Recipe(
            recipe_id=recipe_data.get("recipe_id", "test"),
            title=recipe_data.get("title", "Test Recipe"),
            ingredients=recipe_data.get("ingredients", []),
            instructions=recipe_data.get("instructions", []),
        )

        return self.extract_modification(review, recipe)
