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
from .quality_scorer import QualityScorer


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

    def extract_single_modification(
        self, reviews: list[Review], recipe: Recipe
    ) -> tuple[ModificationObject, Review] | tuple[None, None]:
        """
        Extract modification from a single randomly selected review.
        NOTE: This method is deprecated. Use extract_all_modifications instead.

        Args:
            reviews: List of reviews to choose from
            recipe: Original recipe being modified

        Returns:
            Tuple of (ModificationObject, source_Review) if successful, (None, None) otherwise
        """
        import random

        # Filter to reviews with modifications
        modification_reviews = [r for r in reviews if r.has_modification]

        if not modification_reviews:
            logger.warning("No reviews with modifications found")
            return None, None

        # Select one random review
        selected_review = random.choice(modification_reviews)
        logger.info(f"Selected review: {selected_review.text[:100]}...")

        modification = self.extract_modification(selected_review, recipe)
        if modification:
            logger.info("Successfully extracted modification from selected review")
            return modification, selected_review
        else:
            logger.warning("Failed to extract modification from selected review")
            return None, None

    def extract_all_modifications(
        self,
        reviews: list[Review],
        recipe: Recipe,
        min_rating: int = 4,
        min_quality_score: float = 0.75
    ) -> list[tuple[ModificationObject, Review]]:
        """
        Extract modifications from all reviews that meet quality criteria.

        Args:
            reviews: List of reviews to process
            recipe: Original recipe being modified
            min_rating: Minimum star rating (default: 4)
            min_quality_score: Minimum quality score threshold (default: 0.75)

        Returns:
            List of tuples: (ModificationObject, source_Review) for all successful extractions
        """
        # Initialize quality scorer
        scorer = QualityScorer()

        # Step 1: Filter by rating and modification flag
        rating_filtered = [
            r for r in reviews
            if r.has_modification and r.rating is not None and r.rating >= min_rating
        ]

        if not rating_filtered:
            logger.warning(f"No reviews with modifications and rating >= {min_rating} found")
            return []

        logger.info(
            f"Found {len(rating_filtered)} reviews with rating >= {min_rating} "
            f"out of {len(reviews)} total reviews"
        )

        # Step 2: Extract modifications from all rating-qualified reviews
        extractions_with_modifications = []

        for review in rating_filtered:
            logger.debug(f"Processing review with {review.rating}★ rating: {review.text[:80]}...")

            modification = self.extract_modification(review, recipe)

            if modification:
                # Calculate quality score
                review.text_length = len(review.text) if review.text else 0
                quality_score = scorer.calculate_review_quality_score(review, modification)
                review.quality_score = quality_score

                extractions_with_modifications.append((modification, review, quality_score))

                logger.debug(
                    f"✓ Extracted {modification.modification_type} with quality score: {quality_score:.2f}"
                )
            else:
                logger.debug(
                    f"✗ Failed to extract modification from {review.rating}★ review"
                )

        if not extractions_with_modifications:
            logger.warning("No modifications could be extracted from high-rated reviews")
            return []

        # Step 3: Filter by quality score
        quality_filtered = [
            (mod, review)
            for mod, review, score in extractions_with_modifications
            if score >= min_quality_score
        ]

        # Log quality distribution
        all_scores = [score for _, _, score in extractions_with_modifications]
        distribution = scorer.get_quality_distribution(all_scores)

        logger.info(
            f"Quality Score Distribution: "
            f"min={distribution['min']:.2f}, max={distribution['max']:.2f}, "
            f"avg={distribution['avg']:.2f}, median={distribution['median']:.2f}"
        )

        logger.info(
            f"Filtered to {len(quality_filtered)} reviews with quality score >= {min_quality_score} "
            f"out of {len(extractions_with_modifications)} extracted"
        )

        # Log successful extractions with details
        for modification, review in quality_filtered:
            logger.info(
                f"✓ {review.rating}★ review (quality={review.quality_score:.2f}): "
                f"{modification.modification_type} - {len(modification.edits)} edits - "
                f"{review.username or 'anonymous'}"
            )

        return quality_filtered

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
