"""
Quality Scoring for Reviews and Modifications

This module calculates quality scores for reviews to help filter out
low-quality modifications and prioritize high-value community tweaks.
"""

import re
from typing import Optional

from loguru import logger

from .models import ModificationObject, Review


class QualityScorer:
    """Calculate quality scores for reviews and modifications."""

    def __init__(self):
        """Initialize the QualityScorer."""
        logger.info("Initialized QualityScorer")

    def calculate_review_quality_score(
        self,
        review: Review,
        modification: Optional[ModificationObject] = None
    ) -> float:
        """
        Calculate quality score (0.0-1.0) for a review.

        Quality signals:
        - Base score from rating (4★ = 0.8, 5★ = 1.0)
        - Text length bonus (longer reviews = more detailed)
        - Modification complexity (multiple edits = more thoughtful)
        - Specificity bonus (specific quantities > vague statements)

        Args:
            review: Review to score
            modification: Extracted modification (optional, increases accuracy)

        Returns:
            float: Quality score between 0.0 and 1.0
        """
        score = 0.0

        # 1. Base score from rating (most important signal)
        if review.rating is not None:
            if review.rating >= 5:
                score += 1.0
            elif review.rating >= 4:
                score += 0.8
            elif review.rating >= 3:
                score += 0.6
            else:
                score += 0.4
        else:
            # No rating = low base score
            score += 0.5

        # 2. Text length bonus (0-0.15)
        text_length = len(review.text) if review.text else 0
        if text_length > 200:
            score += 0.15
        elif text_length > 100:
            score += 0.10
        elif text_length > 50:
            score += 0.05

        # 3. Modification complexity bonus (0-0.10)
        if modification:
            edit_count = len(modification.edits)
            if edit_count >= 3:
                score += 0.10
            elif edit_count >= 2:
                score += 0.06
            elif edit_count >= 1:
                score += 0.03

            # 4. Specificity bonus (0-0.05) - check for specific quantities
            specificity = self._calculate_specificity(modification)
            score += specificity

        # Cap at 1.0
        return min(score, 1.0)

    def _calculate_specificity(self, modification: ModificationObject) -> float:
        """
        Calculate specificity score based on how specific the modifications are.

        Specific modifications use exact quantities and measurements.
        Vague modifications use general terms like "more", "less", "some".

        Args:
            modification: Modification to analyze

        Returns:
            float: Specificity bonus (0.0-0.05)
        """
        specificity_score = 0.0

        for edit in modification.edits:
            # Check for specific quantity patterns
            text_to_find = edit.find.lower()

            # Specific quantities (fractions, decimals, measurements)
            specific_patterns = [
                r'\d+\s*\/\s*\d+',  # Fractions: "1/2", "3/4"
                r'\d+\.\d+',  # Decimals: "0.5", "1.5"
                r'\d+\s*(cup|cups|tbsp|tbsp|tablespoon|teaspoon|tsp|oz|ounce|pound|lb)',
                r'\d+\s*(gram|grams|g|kg|kilogram|ml|liter|l)'
            ]

            for pattern in specific_patterns:
                if re.search(pattern, text_to_find):
                    specificity_score += 0.02
                    break

            # Check for vague terms (reduce specificity)
            vague_terms = ['more', 'less', 'some', 'extra', 'bit', 'little', 'few']
            if any(term in text_to_find for term in vague_terms):
                specificity_score -= 0.01

        # Cap specificity bonus
        return max(0.0, min(specificity_score, 0.05))

    def score_reviews(
        self,
        reviews: list[Review],
        modifications_map: dict[str, ModificationObject]
    ) -> dict[str, float]:
        """
        Calculate quality scores for multiple reviews.

        Args:
            reviews: List of reviews to score
            modifications_map: Map of review text to modification objects

        Returns:
            dict: Map of review text to quality score
        """
        scores = {}

        for review in reviews:
            modification = modifications_map.get(review.text)
            score = self.calculate_review_quality_score(review, modification)
            scores[review.text] = score

            logger.debug(
                f"Review quality score: {score:.2f} "
                f"(rating={review.rating}, length={len(review.text) if review.text else 0})"
            )

        return scores

    def get_quality_distribution(
        self,
        scores: list[float]
    ) -> dict[str, float]:
        """
        Get distribution statistics for quality scores.

        Args:
            scores: List of quality scores

        Returns:
            dict: Statistics (min, max, avg, median)
        """
        if not scores:
            return {"min": 0.0, "max": 0.0, "avg": 0.0, "median": 0.0}

        sorted_scores = sorted(scores)
        n = len(sorted_scores)

        return {
            "min": sorted_scores[0],
            "max": sorted_scores[-1],
            "avg": sum(sorted_scores) / n,
            "median": sorted_scores[n // 2] if n % 2 == 1 else (sorted_scores[n // 2 - 1] + sorted_scores[n // 2]) / 2
        }
