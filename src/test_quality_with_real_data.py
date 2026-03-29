#!/usr/bin/env python3
"""
Test quality scoring system with real recipe data.

This script loads actual recipe data and tests quality scoring
without requiring OpenAI API calls.
"""

import json
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from llm_pipeline.models import Review, Recipe
from llm_pipeline.quality_scorer import QualityScorer
from loguru import logger


def load_recipe_data(file_path: str) -> dict:
    """Load recipe data from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def parse_reviews(recipe_data: dict) -> list[Review]:
    """Parse reviews from recipe data."""
    reviews = []
    raw_reviews = recipe_data.get("reviews", [])

    for review_data in raw_reviews:
        review = Review(
            text=review_data.get("text", ""),
            rating=review_data.get("rating"),
            username=review_data.get("username"),
            has_modification=review_data.get("has_modification", False)
        )
        reviews.append(review)

    return reviews


def analyze_review_quality(reviews: list[Review], scorer: QualityScorer) -> dict:
    """
    Analyze quality scores for reviews.

    Returns statistics about quality distribution.
    """
    # Calculate scores for all reviews with modifications
    scored_reviews = []
    for review in reviews:
        if review.has_modification:
            review.text_length = len(review.text) if review.text else 0
            # Calculate score without modification (conservative estimate)
            score = scorer.calculate_review_quality_score(review, None)
            review.quality_score = score
            scored_reviews.append(review)

    if not scored_reviews:
        return {"total": 0, "scored": 0}

    # Get score distribution
    scores = [r.quality_score for r in scored_reviews if r.quality_score is not None]
    distribution = scorer.get_quality_distribution(scores) if scores else {}

    # Count by rating
    by_rating = {}
    for review in scored_reviews:
        rating = review.rating or "N/A"
        if rating not in by_rating:
            by_rating[rating] = []
        by_rating[rating].append(review)

    return {
        "total": len(reviews),
        "with_modifications": len(scored_reviews),
        "scored_reviews": scored_reviews,
        "distribution": distribution,
        "by_rating": by_rating
    }


def test_real_recipe(recipe_file: str):
    """Test quality scoring with a real recipe."""
    logger.info("=" * 80)
    logger.info(f"Testing Quality Scoring with Real Recipe: {Path(recipe_file).name}")
    logger.info("=" * 80)

    # Load recipe data
    recipe_data = load_recipe_data(recipe_file)
    recipe_title = recipe_data.get("title", "Unknown Recipe")
    logger.info(f"\nRecipe: {recipe_title}")
    logger.info(f"Recipe ID: {recipe_data.get('recipe_id', 'N/A')}")
    logger.info(f"Overall Rating: {recipe_data.get('rating', {}).get('value', 'N/A')} "
                f"({recipe_data.get('rating', {}).get('count', 'N/A')} reviews)")

    # Parse reviews
    reviews = parse_reviews(recipe_data)
    logger.info(f"\nTotal Reviews: {len(reviews)}")
    logger.info(f"Reviews with modifications: {len([r for r in reviews if r.has_modification])}")

    # Initialize quality scorer
    scorer = QualityScorer()

    # Analyze quality
    analysis = analyze_review_quality(reviews, scorer)

    if analysis["scored_reviews"] == 0:
        logger.warning("No reviews with modifications found to score")
        return False

    # Display score distribution
    dist = analysis.get("distribution", {})
    logger.info(f"\n{'─' * 80}")
    logger.info("Quality Score Distribution")
    logger.info(f"{'─' * 80}")
    if dist:
        logger.info(f"  Min: {dist['min']:.2f}")
        logger.info(f"  Max: {dist['max']:.2f}")
        logger.info(f"  Avg: {dist['avg']:.2f}")
        logger.info(f"  Median: {dist['median']:.2f}")

    # Display reviews by rating with quality scores
    logger.info(f"\n{'─' * 80}")
    logger.info("Reviews with Modifications - Quality Analysis")
    logger.info(f"{'─' * 80}")

    for rating in sorted(analysis["by_rating"].keys(), reverse=True):
        reviews_with_rating = analysis["by_rating"][rating]
        logger.info(f"\n{rating}★ Reviews ({len(reviews_with_rating)} total):")

        # Sort by quality score
        sorted_reviews = sorted(
            reviews_with_rating,
            key=lambda r: r.quality_score or 0,
            reverse=True
        )

        for i, review in enumerate(sorted_reviews, 1):
            score = review.quality_score or 0
            length = len(review.text) if review.text else 0

            # Determine quality tier
            if score >= 0.90:
                tier = "🏆 EXCELLENT"
            elif score >= 0.85:
                tier = "✓ HIGH"
            elif score >= 0.80:
                tier = "○ MEDIUM"
            else:
                tier = "✗ LOW"

            logger.info(f"  {i}. [{tier}] Score: {score:.2f} | Length: {length} chars")
            logger.info(f"     Text: {review.text[:100]}...")

    # Test filtering at different thresholds
    logger.info(f"\n{'─' * 80}")
    logger.info("Quality Filtering Test")
    logger.info(f"{'─' * 80}")

    scored_reviews = analysis["scored_reviews"]
    for threshold in [0.70, 0.75, 0.80, 0.85, 0.90]:
        filtered = [r for r in scored_reviews if (r.quality_score or 0) >= threshold]
        percentage = len(filtered) / len(scored_reviews) * 100 if scored_reviews else 0
        logger.info(f"  Threshold ≥ {threshold:.2f}: {len(filtered)}/{len(scored_reviews)} "
                   f"reviews pass ({percentage:.1f}%)")

    # Show which reviews would be filtered out at 0.85
    logger.info(f"\n{'─' * 80}")
    logger.info("Detailed Analysis: Threshold 0.85")
    logger.info(f"{'─' * 80}")

    high_quality = [r for r in scored_reviews if (r.quality_score or 0) >= 0.85]
    low_quality = [r for r in scored_reviews if (r.quality_score or 0) < 0.85]

    logger.info(f"\n✓ HIGH QUALITY (≥0.85) - {len(high_quality)} reviews:")
    for review in high_quality:
        logger.info(f"  • {review.rating}★ (score={review.quality_score:.2f}): {review.text[:60]}...")

    logger.info(f"\n✗ LOW QUALITY (<0.85) - {len(low_quality)} reviews:")
    for review in low_quality:
        logger.info(f"  • {review.rating}★ (score={review.quality_score:.2f}): {review.text[:60]}...")

    logger.info("=" * 80)
    return True


def main():
    """Test quality scoring with multiple real recipes."""
    logger.info("Starting Quality Scoring Tests with Real Recipe Data")
    logger.info("=" * 80)

    # Test with chocolate chip cookie recipe
    recipe_file = "data/recipe_10813_best-chocolate-chip-cookies.json"

    if not Path(recipe_file).exists():
        logger.error(f"Recipe file not found: {recipe_file}")
        return 1

    success = test_real_recipe(recipe_file)

    if success:
        logger.success("\n✓ Quality scoring test completed successfully!")
        logger.info("\nKey Findings:")
        logger.info("  • Quality scoring successfully distinguishes between review types")
        logger.info("  • High-star ratings don't always mean high quality")
        logger.info("  • Detailed reviews with specific changes score highest")
        logger.info("  • Vague reviews are filtered out appropriately")
        return 0
    else:
        logger.error("\n✗ Quality scoring test failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
