#!/usr/bin/env python3
"""
Test script to validate the quality scoring system.

This script tests the QualityScorer with various review types and quality levels.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from llm_pipeline.models import Review, ModificationObject, ModificationEdit
from llm_pipeline.quality_scorer import QualityScorer


def create_test_reviews():
    """Create test reviews with varying quality levels."""
    return [
        # High-quality review (5★, detailed, specific)
        Review(
            text="I reduced the white sugar from 1 cup to 0.5 cup and increased the brown sugar to 1.5 cups. The cookies turned out perfectly chewy with crisp edges!",
            rating=5,
            username="expert_baker",
            has_modification=True
        ),
        # Medium-high quality (4★, moderately detailed)
        Review(
            text="Added extra chocolate chips, about 1 more cup. Made them much better.",
            rating=4,
            username="choco_lover",
            has_modification=True
        ),
        # Medium quality (4★, brief but specific)
        Review(
            text="Used 1 tsp salt instead of 0.5 tsp.",
            rating=4,
            username="salty_dog",
            has_modification=True
        ),
        # Low quality (4★, vague)
        Review(
            text="I added more sugar and they were good.",
            rating=4,
            username="vague_cook",
            has_modification=True
        ),
        # Very low quality (4★, extremely brief)
        Review(
            text="Good recipe.",
            rating=4,
            username="minimalist",
            has_modification=True
        ),
        # High rating but low detail
        Review(
            text="Amazing! Will make again.",
            rating=5,
            username="fan",
            has_modification=True
        ),
    ]


def create_test_modifications():
    """Create test modifications corresponding to reviews."""
    return [
        # High-quality: multiple specific edits
        ModificationObject(
            modification_type="quantity_adjustment",
            reasoning="Makes cookies more chewy and flavorful",
            edits=[
                ModificationEdit(
                    target="ingredients",
                    operation="replace",
                    find="1 cup white sugar",
                    replace="0.5 cup white sugar"
                ),
                ModificationEdit(
                    target="ingredients",
                    operation="replace",
                    find="1 cup packed brown sugar",
                    replace="1.5 cups packed brown sugar"
                ),
            ]
        ),
        # Medium-high: one specific edit
        ModificationObject(
            modification_type="addition",
            reasoning="More chocolate flavor",
            edits=[
                ModificationEdit(
                    target="ingredients",
                    operation="replace",
                    find="2 cups semisweet chocolate chips",
                    replace="3 cups semisweet chocolate chips"
                ),
            ]
        ),
        # Medium: one specific edit
        ModificationObject(
            modification_type="quantity_adjustment",
            reasoning="Better flavor balance",
            edits=[
                ModificationEdit(
                    target="ingredients",
                    operation="replace",
                    find="0.5 teaspoon salt",
                    replace="1 teaspoon salt"
                ),
            ]
        ),
        # Low: vague edit
        ModificationObject(
            modification_type="quantity_adjustment",
            reasoning="More sweetness",
            edits=[
                ModificationEdit(
                    target="ingredients",
                    operation="replace",
                    find="sugar",
                    replace="more sugar"
                ),
            ]
        ),
        # Very low: minimal edit
        ModificationObject(
            modification_type="addition",
            reasoning="Personal preference",
            edits=[
                ModificationEdit(
                    target="ingredients",
                    operation="add_after",
                    find="vanilla extract",
                    add="love"
                ),
            ]
        ),
        # High rating, no meaningful edit
        ModificationObject(
            modification_type="addition",
            reasoning="Just positive feedback",
            edits=[
                ModificationEdit(
                    target="ingredients",
                    operation="add_after",
                    find="chocolate chips",
                    add="nothing specific"
                ),
            ]
        ),
    ]


def test_quality_scoring():
    """Test quality scoring with various review types."""
    from loguru import logger

    logger.info("=" * 60)
    logger.info("Testing Quality Scoring System")
    logger.info("=" * 60)

    scorer = QualityScorer()
    reviews = create_test_reviews()
    modifications = create_test_modifications()

    logger.info(f"\nTesting {len(reviews)} reviews with varying quality levels\n")

    results = []
    for i, (review, modification) in enumerate(zip(reviews, modifications), 1):
        # Calculate quality score
        score = scorer.calculate_review_quality_score(review, modification)

        # Store result
        results.append({
            'review': review,
            'modification': modification,
            'score': score
        })

        # Log details
        logger.info(f"\n{'─' * 60}")
        logger.info(f"Review {i}: {review.username} ({review.rating}★)")
        logger.info(f"Text: {review.text[:60]}...")
        logger.info(f"Text length: {len(review.text)} chars")
        logger.info(f"Modification type: {modification.modification_type}")
        logger.info(f"Number of edits: {len(modification.edits)}")
        logger.info(f"Quality Score: {score:.2f}")

    # Validate scoring
    logger.info(f"\n{'=' * 60}")
    logger.info("Validation Results")
    logger.info("=" * 60)

    # Check that high-quality reviews score higher
    high_quality_score = results[0]['score']  # expert_baker
    low_quality_score = results[3]['score']  # vague_cook

    if high_quality_score > 0.9:
        logger.success(f"✓ High-quality review scored {high_quality_score:.2f} (> 0.9)")
    else:
        logger.error(f"✗ High-quality review scored {high_quality_score:.2f} (expected > 0.9)")
        return False

    if low_quality_score < 0.85:
        logger.success(f"✓ Low-quality review scored {low_quality_score:.2f} (< 0.85)")
    else:
        logger.error(f"✗ Low-quality review scored {low_quality_score:.2f} (expected < 0.85)")
        return False

    # Check that quality correlates with detail
    if high_quality_score > low_quality_score:
        logger.success("✓ Quality scoring favors detailed reviews over vague ones")
    else:
        logger.error("✗ Quality scoring not working correctly")
        return False

    # Test scoring distribution
    scores = [r['score'] for r in results]
    distribution = scorer.get_quality_distribution(scores)

    logger.info(f"\nScore Distribution:")
    logger.info(f"  Min: {distribution['min']:.2f}")
    logger.info(f"  Max: {distribution['max']:.2f}")
    logger.info(f"  Avg: {distribution['avg']:.2f}")
    logger.info(f"  Median: {distribution['median']:.2f}")

    if 0.5 <= distribution['avg'] <= 1.0:
        logger.success("✓ Score distribution in expected range")
    else:
        logger.error(f"✗ Average score {distribution['avg']:.2f} outside expected range")
        return False

    logger.info("=" * 60)
    return True


def test_quality_filtering():
    """Test that quality filtering works as expected."""
    from loguru import logger

    logger.info("\n" + "=" * 60)
    logger.info("Testing Quality-Based Filtering")
    logger.info("=" * 60)

    scorer = QualityScorer()
    reviews = create_test_reviews()
    modifications = create_test_modifications()

    # Calculate scores for all
    scored_reviews = []
    for review, modification in zip(reviews, modifications):
        score = scorer.calculate_review_quality_score(review, modification)
        review.quality_score = score
        review.text_length = len(review.text)
        scored_reviews.append(review)

    # Test different thresholds
    for threshold in [0.70, 0.75, 0.80, 0.85]:
        filtered = [r for r in scored_reviews if r.quality_score >= threshold]

        logger.info(f"\nThreshold {threshold:.2f}: {len(filtered)}/{len(scored_reviews)} reviews pass")

        for review in filtered:
            logger.info(
                f"  ✓ {review.username} ({review.rating}★) - "
                f"score={review.quality_score:.2f}"
            )

    # Validate that threshold 0.85 filters appropriately
    threshold_85_reviews = [r for r in scored_reviews if r.quality_score >= 0.85]
    threshold_85_count = len(threshold_85_reviews)

    # Should pass 4 reviews out of 6 (top quality ones)
    if threshold_85_count == 4:
        logger.success(
            f"✓ Threshold 0.85 filters to {threshold_85_count} reviews "
            f"(expected 4)"
        )
    else:
        logger.error(
            f"✗ Threshold 0.85 filtered to {threshold_85_count} reviews "
            f"(expected 4)"
        )
        return False

    logger.info("=" * 60)
    return True


def test_specificity_scoring():
    """Test that specific modifications score higher than vague ones."""
    from loguru import logger

    logger.info("\n" + "=" * 60)
    logger.info("Testing Specificity Bonus")
    logger.info("=" * 60)

    scorer = QualityScorer()

    # Specific modification
    specific_mod = ModificationObject(
        modification_type="quantity_adjustment",
        reasoning="Uses exact measurements",
        edits=[
            ModificationEdit(
                target="ingredients",
                operation="replace",
                find="1 cup white sugar",
                replace="0.5 cup white sugar"
            ),
        ]
    )

    # Vague modification
    vague_mod = ModificationObject(
        modification_type="quantity_adjustment",
        reasoning="Uses vague terms",
        edits=[
            ModificationEdit(
                target="ingredients",
                operation="replace",
                find="sugar",
                replace="more sugar"
            ),
        ]
    )

    # Same review base
    review = Review(
        text="Test review",
        rating=4,
        username="tester",
        has_modification=True
    )

    specific_score = scorer.calculate_review_quality_score(review, specific_mod)
    vague_score = scorer.calculate_review_quality_score(review, vague_mod)

    logger.info(f"Specific modification score: {specific_score:.2f}")
    logger.info(f"Vague modification score: {vague_score:.2f}")

    if specific_score > vague_score:
        logger.success("✓ Specific modifications score higher than vague ones")
        logger.info(f"  Difference: {specific_score - vague_score:.2f}")
    else:
        logger.error("✗ Specificity scoring not working correctly")
        return False

    logger.info("=" * 60)
    return True


def main():
    """Run all quality scoring tests."""
    from loguru import logger

    logger.info("Starting Quality Scoring Validation Tests")
    logger.info("=" * 60)

    # Test 1: Basic quality scoring
    if not test_quality_scoring():
        logger.error("✗ Quality scoring test failed")
        return 1

    # Test 2: Quality-based filtering
    if not test_quality_filtering():
        logger.error("✗ Quality filtering test failed")
        return 1

    # Test 3: Specificity bonus
    if not test_specificity_scoring():
        logger.error("✗ Specificity scoring test failed")
        return 1

    logger.success("\n✓✓✓ All quality scoring tests passed! ✓✓✓\n")
    logger.info("The QualityScorer successfully:")
    logger.info("  1. Calculates quality scores based on multiple signals")
    logger.info("  2. Favors detailed, specific reviews over vague ones")
    logger.info("  3. Provides score distribution statistics")
    logger.info("  4. Supports quality-based filtering with configurable thresholds")

    return 0


if __name__ == "__main__":
    sys.exit(main())
