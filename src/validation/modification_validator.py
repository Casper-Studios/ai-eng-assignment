"""
ModificationValidator - Comprehensive Validation Framework

This module provides validation classes and methods for assessing the completeness,
accuracy, and quality of modification extraction and application in the Recipe
Enhancement Pipeline.
"""

import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

from loguru import logger
from pydantic import BaseModel

from ..llm_pipeline.models import ModificationObject, Recipe, Review, EnhancedRecipe


class ValidationResult(BaseModel):
    """Result of a validation operation."""

    test_id: str
    passed: bool
    score: float  # 0.0 to 1.0
    details: Dict[str, Any]
    timestamp: str
    notes: List[str] = []


class ValidationMetrics(BaseModel):
    """Aggregated validation metrics."""

    total_tests: int
    passed_tests: int
    failed_tests: int
    average_score: float
    pass_rate: float
    metrics_by_type: Dict[str, Dict[str, float]]


@dataclass
class GroundTruthEntry:
    """Ground truth entry for validation."""

    id: str
    review_text: str
    recipe_data: Dict[str, Any]
    expected_modifications: List[Dict[str, Any]]
    expected_count: int
    difficulty_level: str  # "simple", "medium", "complex"
    notes: str = ""


class ModificationValidator:
    """Validates completeness and accuracy of modification extraction."""

    def __init__(self, output_dir: str = "validation_results"):
        """
        Initialize the ModificationValidator.

        Args:
            output_dir: Directory to save validation results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.validation_history: List[ValidationResult] = []

        logger.info(f"Initialized ModificationValidator with output dir: {output_dir}")

    def validate_completeness(
        self,
        review_text: str,
        extracted_mods: List[ModificationObject],
        expected_count: Optional[int] = None,
        ground_truth: Optional[List[Dict[str, Any]]] = None
    ) -> ValidationResult:
        """
        Validate that all discrete modifications were extracted from a review.

        Args:
            review_text: Original review text
            extracted_mods: List of extracted ModificationObjects
            expected_count: Expected number of modifications (if known)
            ground_truth: Expected modifications for detailed comparison

        Returns:
            ValidationResult with completeness assessment
        """
        test_id = f"completeness_{int(time.time())}"
        extracted_count = len(extracted_mods)

        # Calculate completeness score
        if expected_count is not None:
            completeness_score = min(extracted_count / expected_count, 1.0) if expected_count > 0 else 1.0
        else:
            # Use heuristic estimation
            estimated_count = self._estimate_modification_count(review_text)
            completeness_score = min(extracted_count / estimated_count, 1.0) if estimated_count > 0 else 1.0

        # Detailed analysis
        details = {
            "review_text": review_text[:200] + "..." if len(review_text) > 200 else review_text,
            "extracted_count": extracted_count,
            "expected_count": expected_count,
            "estimated_count": self._estimate_modification_count(review_text),
            "completeness_score": completeness_score,
            "extracted_types": [mod.modification_type for mod in extracted_mods],
            "complexity_indicators": self._analyze_review_complexity(review_text)
        }

        # Generate validation notes
        notes = []
        if extracted_count == 0:
            notes.append("No modifications extracted - possible extraction failure")
        elif expected_count and extracted_count < expected_count:
            notes.append(f"Under-extraction: found {extracted_count}/{expected_count} expected modifications")
        elif expected_count and extracted_count > expected_count:
            notes.append(f"Over-extraction: found {extracted_count}/{expected_count} expected modifications")

        # Check for quality indicators
        if self._has_multiple_action_indicators(review_text) and extracted_count == 1:
            notes.append("Review contains multiple action indicators but only 1 modification extracted")

        # Determine pass/fail (pass if completeness >= 0.8)
        passed = completeness_score >= 0.8

        result = ValidationResult(
            test_id=test_id,
            passed=passed,
            score=completeness_score,
            details=details,
            timestamp=datetime.now().isoformat(),
            notes=notes
        )

        self.validation_history.append(result)
        return result

    def count_discrete_modifications(self, review_text: str) -> int:
        """
        Count discrete modifications in review text using advanced heuristics.

        Args:
            review_text: Review text to analyze

        Returns:
            Estimated number of discrete modifications
        """
        return self._estimate_modification_count(review_text)

    def compare_extracted_vs_expected(
        self,
        expected: List[Dict[str, Any]],
        extracted: List[ModificationObject]
    ) -> float:
        """
        Compare extracted modifications against expected ground truth.

        Args:
            expected: List of expected modification dictionaries
            extracted: List of extracted ModificationObjects

        Returns:
            Similarity score from 0.0 to 1.0
        """
        if not expected and not extracted:
            return 1.0

        if not expected or not extracted:
            return 0.0

        # Convert extracted to comparable format
        extracted_dicts = [
            {
                "type": mod.modification_type,
                "reasoning": mod.reasoning.lower(),
                "edits_count": len(mod.edits)
            }
            for mod in extracted
        ]

        # Calculate similarity metrics
        type_matches = 0
        reasoning_similarities = []

        for exp in expected:
            best_match_score = 0
            exp_type = exp.get("type", "").lower()
            exp_reasoning = exp.get("reasoning", "").lower()

            for ext in extracted_dicts:
                score = 0

                # Type match (40% weight)
                if exp_type == ext["type"]:
                    score += 0.4
                elif self._are_similar_types(exp_type, ext["type"]):
                    score += 0.2

                # Reasoning similarity (60% weight)
                reasoning_sim = self._calculate_text_similarity(exp_reasoning, ext["reasoning"])
                score += 0.6 * reasoning_sim

                best_match_score = max(best_match_score, score)

            reasoning_similarities.append(best_match_score)

        # Average similarity
        if reasoning_similarities:
            avg_similarity = sum(reasoning_similarities) / len(reasoning_similarities)
        else:
            avg_similarity = 0.0

        return avg_similarity

    def validate_extraction_quality(
        self,
        extracted_mods: List[ModificationObject],
        recipe: Recipe
    ) -> ValidationResult:
        """
        Validate the quality of extracted modifications.

        Args:
            extracted_mods: List of extracted modifications
            recipe: Original recipe

        Returns:
            ValidationResult with quality assessment
        """
        test_id = f"quality_{int(time.time())}"

        quality_score = 0.0
        details = {}
        notes = []

        if not extracted_mods:
            return ValidationResult(
                test_id=test_id,
                passed=False,
                score=0.0,
                details={"error": "No modifications to validate"},
                timestamp=datetime.now().isoformat(),
                notes=["No modifications extracted"]
            )

        # Quality checks
        total_checks = 0
        passed_checks = 0

        # 1. Check if modifications have reasonable edits
        for i, mod in enumerate(extracted_mods):
            total_checks += 1
            if mod.edits and len(mod.edits) > 0:
                passed_checks += 1
            else:
                notes.append(f"Modification {i+1} has no edits")

        # 2. Check reasoning quality
        for i, mod in enumerate(extracted_mods):
            total_checks += 1
            if len(mod.reasoning.strip()) > 10:  # Reasonable reasoning length
                passed_checks += 1
            else:
                notes.append(f"Modification {i+1} has insufficient reasoning")

        # 3. Check for valid modification types
        valid_types = {"ingredient_substitution", "quantity_adjustment", "technique_change", "addition", "removal"}
        for i, mod in enumerate(extracted_mods):
            total_checks += 1
            if mod.modification_type in valid_types:
                passed_checks += 1
            else:
                notes.append(f"Modification {i+1} has invalid type: {mod.modification_type}")

        # 4. Check for actionable edits
        for i, mod in enumerate(extracted_mods):
            total_checks += 1
            actionable = any(
                edit.find and (edit.replace or edit.add)
                for edit in mod.edits
            )
            if actionable:
                passed_checks += 1
            else:
                notes.append(f"Modification {i+1} has no actionable edits")

        quality_score = passed_checks / total_checks if total_checks > 0 else 0.0

        details = {
            "total_modifications": len(extracted_mods),
            "quality_checks_passed": passed_checks,
            "quality_checks_total": total_checks,
            "quality_score": quality_score,
            "modification_types": [mod.modification_type for mod in extracted_mods],
            "average_edits_per_mod": sum(len(mod.edits) for mod in extracted_mods) / len(extracted_mods),
            "average_reasoning_length": sum(len(mod.reasoning) for mod in extracted_mods) / len(extracted_mods)
        }

        passed = quality_score >= 0.7  # 70% quality threshold

        result = ValidationResult(
            test_id=test_id,
            passed=passed,
            score=quality_score,
            details=details,
            timestamp=datetime.now().isoformat(),
            notes=notes
        )

        self.validation_history.append(result)
        return result

    def run_comprehensive_validation(
        self,
        ground_truth_entries: List[GroundTruthEntry],
        extractor,  # MultiModificationExtractor instance
    ) -> ValidationMetrics:
        """
        Run comprehensive validation across multiple test cases.

        Args:
            ground_truth_entries: List of ground truth test cases
            extractor: MultiModificationExtractor instance

        Returns:
            Aggregated validation metrics
        """
        logger.info(f"Running comprehensive validation on {len(ground_truth_entries)} test cases")

        results = []
        metrics_by_type = {
            "completeness": {"total": 0, "passed": 0, "total_score": 0},
            "quality": {"total": 0, "passed": 0, "total_score": 0}
        }

        for entry in ground_truth_entries:
            logger.info(f"Validating: {entry.id}")

            # Create review and recipe objects
            review = Review(text=entry.review_text, has_modification=True)
            recipe = Recipe(
                recipe_id=entry.id,
                title=entry.recipe_data.get("title", "Test Recipe"),
                ingredients=entry.recipe_data.get("ingredients", []),
                instructions=entry.recipe_data.get("instructions", [])
            )

            try:
                # Extract modifications
                modifications, _ = extractor.extract_all_modifications(review, recipe)

                # Validate completeness
                completeness_result = self.validate_completeness(
                    entry.review_text,
                    modifications,
                    entry.expected_count,
                    entry.expected_modifications
                )

                # Validate quality
                quality_result = self.validate_extraction_quality(modifications, recipe)

                # Update metrics
                metrics_by_type["completeness"]["total"] += 1
                metrics_by_type["completeness"]["total_score"] += completeness_result.score
                if completeness_result.passed:
                    metrics_by_type["completeness"]["passed"] += 1

                metrics_by_type["quality"]["total"] += 1
                metrics_by_type["quality"]["total_score"] += quality_result.score
                if quality_result.passed:
                    metrics_by_type["quality"]["passed"] += 1

                results.extend([completeness_result, quality_result])

            except Exception as e:
                logger.error(f"Validation failed for {entry.id}: {e}")
                # Create failure result
                failure_result = ValidationResult(
                    test_id=f"failed_{entry.id}",
                    passed=False,
                    score=0.0,
                    details={"error": str(e)},
                    timestamp=datetime.now().isoformat(),
                    notes=[f"Validation failed: {e}"]
                )
                results.append(failure_result)

        # Calculate overall metrics
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        total_score = sum(r.score for r in results)

        # Calculate metrics by type
        for metric_type in metrics_by_type:
            data = metrics_by_type[metric_type]
            if data["total"] > 0:
                data["pass_rate"] = data["passed"] / data["total"]
                data["average_score"] = data["total_score"] / data["total"]
            else:
                data["pass_rate"] = 0.0
                data["average_score"] = 0.0

        metrics = ValidationMetrics(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=total_tests - passed_tests,
            average_score=total_score / total_tests if total_tests > 0 else 0.0,
            pass_rate=passed_tests / total_tests if total_tests > 0 else 0.0,
            metrics_by_type=metrics_by_type
        )

        # Save results
        self._save_validation_results(results, metrics)

        logger.info(f"Validation complete: {metrics.pass_rate:.1%} pass rate, {metrics.average_score:.2f} avg score")
        return metrics

    def _estimate_modification_count(self, review_text: str) -> int:
        """Estimate number of modifications using heuristics."""
        import re

        text = review_text.lower()

        # Start with 1 (assume at least one if reviewing)
        count = 1

        # Count conjunction patterns
        conjunctions = len(re.findall(r'\b(and|also|plus|additionally|then|next)\b', text))
        count += conjunctions

        # Count comma-separated actions
        action_pattern = r',\s*(?:and\s+)?(?:i\s+)?(?:also\s+)?(?:added|used|changed|increased|decreased|substituted|omitted|replaced)'
        comma_actions = len(re.findall(action_pattern, text))
        count += comma_actions

        # Count distinct action verbs
        action_verbs = ['added', 'used', 'changed', 'increased', 'decreased', 'substituted', 'omitted', 'replaced', 'doubled', 'halved']
        verb_count = sum(1 for verb in action_verbs if verb in text)

        # Use verb count if higher
        count = max(count, verb_count)

        return max(1, count)  # At least 1

    def _analyze_review_complexity(self, review_text: str) -> Dict[str, Any]:
        """Analyze complexity indicators in review text."""
        import re

        text = review_text.lower()

        return {
            "length": len(review_text),
            "sentence_count": len(re.findall(r'[.!?]+', review_text)),
            "conjunction_count": len(re.findall(r'\b(and|also|plus|additionally|then|next)\b', text)),
            "action_verb_count": len(re.findall(r'\b(added|used|changed|increased|decreased|substituted|omitted|replaced|doubled|halved)\b', text)),
            "numeric_references": len(re.findall(r'\b\d+\b', text)),
            "has_measurements": bool(re.search(r'\b(cup|cups|tablespoon|tablespoons|teaspoon|teaspoons|pound|pounds|ounce|ounces)\b', text))
        }

    def _has_multiple_action_indicators(self, review_text: str) -> bool:
        """Check if review has indicators of multiple actions."""
        import re

        text = review_text.lower()

        # Check for multiple action indicators
        indicators = [
            r'\band\b',
            r'\balso\b',
            r'\bplus\b',
            r'\bthen\b',
            r'\bnext\b',
            r',\s*(?:and\s+)?(?:i\s+)?(?:also\s+)?(?:added|used|changed)'
        ]

        for pattern in indicators:
            if re.search(pattern, text):
                return True

        return False

    def _are_similar_types(self, type1: str, type2: str) -> bool:
        """Check if two modification types are similar."""
        similar_groups = [
            {"addition", "ingredient_addition"},
            {"substitution", "ingredient_substitution"},
            {"adjustment", "quantity_adjustment"},
            {"change", "technique_change"}
        ]

        for group in similar_groups:
            if type1 in group and type2 in group:
                return True

        return False

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity using word overlap."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 and not words2:
            return 1.0

        if not words1 or not words2:
            return 0.0

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        return intersection / union if union > 0 else 0.0

    def _save_validation_results(self, results: List[ValidationResult], metrics: ValidationMetrics):
        """Save validation results to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save detailed results
        results_file = self.output_dir / f"validation_results_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump([r.dict() for r in results], f, indent=2, ensure_ascii=False)

        # Save metrics summary
        metrics_file = self.output_dir / f"validation_metrics_{timestamp}.json"
        with open(metrics_file, 'w') as f:
            json.dump(metrics.dict(), f, indent=2, ensure_ascii=False)

        logger.info(f"Saved validation results to {results_file}")
        logger.info(f"Saved validation metrics to {metrics_file}")

    def generate_validation_report(self, metrics: ValidationMetrics) -> str:
        """Generate a human-readable validation report."""
        report = f"""
# Modification Validation Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary
- **Total Tests**: {metrics.total_tests}
- **Passed**: {metrics.passed_tests} ({metrics.pass_rate:.1%})
- **Failed**: {metrics.failed_tests}
- **Average Score**: {metrics.average_score:.2f}

## Metrics by Type
"""

        for metric_type, data in metrics.metrics_by_type.items():
            report += f"""
### {metric_type.title()}
- **Tests**: {data['total']}
- **Pass Rate**: {data['pass_rate']:.1%}
- **Average Score**: {data['average_score']:.2f}
"""

        # Add recommendations
        report += "\n## Recommendations\n"

        if metrics.pass_rate < 0.8:
            report += "- ⚠️ **Low pass rate**: Consider improving extraction prompts or methods\n"

        if metrics.metrics_by_type.get("completeness", {}).get("average_score", 0) < 0.9:
            report += "- ⚠️ **Low completeness**: Focus on multi-modification detection improvements\n"

        if metrics.metrics_by_type.get("quality", {}).get("average_score", 0) < 0.8:
            report += "- ⚠️ **Low quality**: Review modification reasoning and edit generation\n"

        if metrics.pass_rate >= 0.9:
            report += "- ✅ **Excellent performance**: Pipeline meets quality standards\n"

        return report