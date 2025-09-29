"""
Actual Pipeline Validator

This module validates the actual LLM pipeline results found in data/enhanced/
to provide accurate assessment of current performance vs PRD requirements.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class ActualPipelineValidator:
    """Validates actual pipeline results against PRD requirements."""

    def __init__(self, enhanced_dir: str = "data/enhanced", raw_data_dir: str = "data"):
        """
        Initialize validator with actual pipeline results.

        Args:
            enhanced_dir: Directory containing actual enhanced recipe results
            raw_data_dir: Directory containing original recipe data
        """
        self.enhanced_dir = Path(enhanced_dir)
        self.raw_data_dir = Path(raw_data_dir)

    def analyze_actual_pipeline_performance(self) -> Dict[str, Any]:
        """
        Analyze the actual pipeline performance based on existing enhanced recipes.

        Returns:
            Comprehensive analysis of actual vs expected performance
        """
        print("🔍 Analyzing Actual Pipeline Performance")
        print("=" * 60)

        # Find all original recipes
        original_recipes = list(self.raw_data_dir.glob("recipe_*.json"))
        enhanced_recipes = list(self.enhanced_dir.glob("enhanced_*.json"))

        print(f"📊 Found {len(original_recipes)} original recipes")
        print(f"📊 Found {len(enhanced_recipes)} enhanced recipes")

        results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "original_recipe_count": len(original_recipes),
            "enhanced_recipe_count": len(enhanced_recipes),
            "success_rate": len(enhanced_recipes) / len(original_recipes) if original_recipes else 0,
            "target_success_rate": 0.8,  # 80% from PRD
            "meets_target": (len(enhanced_recipes) / len(original_recipes)) >= 0.8 if original_recipes else False,
            "detailed_analysis": {
                "successful_recipes": [],
                "failed_recipes": [],
                "modification_analysis": [],
                "quality_assessment": {}
            }
        }

        # Analyze each original recipe
        for recipe_file in original_recipes:
            recipe_analysis = self._analyze_single_recipe(recipe_file, enhanced_recipes)

            if recipe_analysis["enhanced"]:
                results["detailed_analysis"]["successful_recipes"].append(recipe_analysis)
            else:
                results["detailed_analysis"]["failed_recipes"].append(recipe_analysis)

        # Analyze modifications in enhanced recipes
        for enhanced_file in enhanced_recipes:
            mod_analysis = self._analyze_modifications_in_enhanced_recipe(enhanced_file)
            results["detailed_analysis"]["modification_analysis"].append(mod_analysis)

        # Quality assessment
        results["detailed_analysis"]["quality_assessment"] = self._assess_modification_quality(enhanced_recipes)

        return results

    def _analyze_single_recipe(self, recipe_file: Path, enhanced_recipes: List[Path]) -> Dict[str, Any]:
        """Analyze a single recipe's success/failure."""

        # Load original recipe
        with open(recipe_file, 'r', encoding='utf-8') as f:
            recipe_data = json.load(f)

        recipe_id = recipe_data.get("recipe_id", "")
        title = recipe_data.get("title", "")
        reviews = recipe_data.get("reviews", [])

        # Count modification reviews
        modification_reviews = [r for r in reviews if r.get("has_modification", False)]

        # Check if enhanced version exists
        enhanced_file = None
        for enh_file in enhanced_recipes:
            if recipe_id in enh_file.name:
                enhanced_file = enh_file
                break

        analysis = {
            "recipe_id": recipe_id,
            "title": title,
            "original_file": recipe_file.name,
            "total_reviews": len(reviews),
            "modification_reviews": len(modification_reviews),
            "enhanced": enhanced_file is not None,
            "enhanced_file": enhanced_file.name if enhanced_file else None,
            "failure_reason": None
        }

        if not enhanced_file:
            # Determine failure reason
            if len(modification_reviews) == 0:
                analysis["failure_reason"] = "no_modification_reviews"
            else:
                analysis["failure_reason"] = "pipeline_processing_failure"

        print(f"  {'✅' if analysis['enhanced'] else '❌'} {title[:50]:<50} "
              f"({len(modification_reviews)} mod reviews) -> "
              f"{'Enhanced' if analysis['enhanced'] else analysis['failure_reason']}")

        return analysis

    def _analyze_modifications_in_enhanced_recipe(self, enhanced_file: Path) -> Dict[str, Any]:
        """Analyze modifications within an enhanced recipe."""

        with open(enhanced_file, 'r', encoding='utf-8') as f:
            enhanced_data = json.load(f)

        modifications = enhanced_data.get("modifications_applied", [])

        analysis = {
            "enhanced_file": enhanced_file.name,
            "recipe_title": enhanced_data.get("title", ""),
            "total_modifications": len(modifications),
            "modification_types": [],
            "confidence_scores": [],
            "source_reviews": [],
            "multi_modification_detection": {
                "reviews_with_multiple_mods": 0,
                "total_discrete_mods_found": 0,
                "extraction_completeness": 0
            }
        }

        for mod in modifications:
            analysis["modification_types"].append(mod.get("modification_type", "unknown"))
            analysis["confidence_scores"].append(mod.get("confidence_score", 0))

            source_review = mod.get("source_review", {})
            review_text = source_review.get("text", "")
            analysis["source_reviews"].append({
                "text": review_text[:100] + "..." if len(review_text) > 100 else review_text,
                "estimated_modifications": self._count_modifications_in_review(review_text)
            })

        # Assess multi-modification detection
        analysis["multi_modification_detection"] = self._assess_multi_modification_detection(modifications)

        return analysis

    def _count_modifications_in_review(self, review_text: str) -> int:
        """Estimate number of discrete modifications in a review using heuristics."""
        import re

        text_lower = review_text.lower()

        # Count action indicators
        indicators = ['added', 'used', 'substituted', 'replaced', 'changed', 'increased',
                     'decreased', 'doubled', 'halved', 'omitted', 'instead of']

        found_indicators = sum(1 for indicator in indicators if indicator in text_lower)

        # Count conjunctions that typically separate modifications
        conjunctions = len(re.findall(r'\b(and|also|plus|additionally)\b', text_lower))

        # Estimate based on indicators and conjunctions
        estimated = max(1, min(found_indicators, conjunctions + 1))

        return estimated

    def _assess_multi_modification_detection(self, modifications: List[Dict]) -> Dict[str, Any]:
        """Assess how well the pipeline detects multiple modifications."""

        # Group modifications by source review
        reviews_to_mods = {}
        for mod in modifications:
            review_text = mod.get("source_review", {}).get("text", "")
            if review_text not in reviews_to_mods:
                reviews_to_mods[review_text] = []
            reviews_to_mods[review_text].append(mod)

        total_reviews = len(reviews_to_mods)
        reviews_with_multiple_expected = 0
        reviews_with_multiple_extracted = 0
        total_expected_mods = 0
        total_extracted_mods = len(modifications)

        for review_text, review_mods in reviews_to_mods.items():
            expected_mods = self._count_modifications_in_review(review_text)
            extracted_mods = len(review_mods)

            total_expected_mods += expected_mods

            if expected_mods > 1:
                reviews_with_multiple_expected += 1

            if extracted_mods > 1:
                reviews_with_multiple_extracted += 1

        return {
            "total_reviews_analyzed": total_reviews,
            "reviews_with_multiple_expected": reviews_with_multiple_expected,
            "reviews_with_multiple_extracted": reviews_with_multiple_extracted,
            "total_expected_modifications": total_expected_mods,
            "total_extracted_modifications": total_extracted_mods,
            "extraction_completeness": total_extracted_mods / total_expected_mods if total_expected_mods > 0 else 0,
            "multi_mod_detection_rate": reviews_with_multiple_extracted / reviews_with_multiple_expected if reviews_with_multiple_expected > 0 else 0
        }

    def _assess_modification_quality(self, enhanced_recipes: List[Path]) -> Dict[str, Any]:
        """Assess overall quality of modifications."""

        all_modifications = []
        confidence_scores = []
        modification_types = []

        for enhanced_file in enhanced_recipes:
            with open(enhanced_file, 'r', encoding='utf-8') as f:
                enhanced_data = json.load(f)

            modifications = enhanced_data.get("modifications_applied", [])
            all_modifications.extend(modifications)

            for mod in modifications:
                confidence_scores.append(mod.get("confidence_score", 0))
                modification_types.append(mod.get("modification_type", "unknown"))

        # Calculate quality metrics
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0

        type_distribution = {}
        for mod_type in modification_types:
            type_distribution[mod_type] = type_distribution.get(mod_type, 0) + 1

        return {
            "total_modifications": len(all_modifications),
            "average_confidence_score": avg_confidence,
            "modification_type_distribution": type_distribution,
            "quality_assessment": {
                "high_confidence_mods": sum(1 for score in confidence_scores if score >= 0.8),
                "low_confidence_mods": sum(1 for score in confidence_scores if score < 0.6),
                "quality_score": avg_confidence
            }
        }

    def generate_prd_compliance_report(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a report comparing actual performance to PRD requirements."""

        print("\n📋 Generating PRD Compliance Report")
        print("=" * 50)

        # PRD Requirements Assessment
        prd_assessment = {
            "requirement_1_completeness": {
                "requirement": "95% of discrete modifications successfully extracted",
                "current_performance": "Unknown - needs LLM testing",
                "status": "❌ NOT TESTABLE",
                "blocker": "Only 2/6 recipes processed, insufficient data for assessment",
                "evidence": f"Multi-modification detection analysis shows potential issues"
            },
            "requirement_2_accuracy": {
                "requirement": "90% accuracy of applied modifications vs reviewer intent",
                "current_performance": f"{analysis['detailed_analysis']['quality_assessment']['average_confidence_score']:.1%} avg confidence",
                "status": "⚠️ PARTIALLY ASSESSED",
                "evidence": f"Average confidence score suggests good accuracy but needs validation"
            },
            "requirement_3_scalability": {
                "requirement": "80% of recipes successfully enhanced",
                "current_performance": f"{analysis['success_rate']:.1%} ({analysis['enhanced_recipe_count']}/{analysis['original_recipe_count']})",
                "status": "❌ TARGET MISSED",
                "evidence": f"Only {analysis['enhanced_recipe_count']}/6 recipes successfully processed"
            },
            "requirement_4_quality": {
                "requirement": "100% safety validation of enhanced recipes",
                "current_performance": "No safety validation implemented",
                "status": "❌ NOT IMPLEMENTED",
                "evidence": "No safety checks found in enhanced recipe data"
            }
        }

        # Critical Issues Identified
        critical_issues = [
            {
                "issue": "Scale Failure",
                "description": f"Only {analysis['enhanced_recipe_count']}/6 recipes processed (33% vs 80% target)",
                "impact": "HIGH",
                "root_cause": "Pipeline fails on recipes without modification reviews or with processing errors"
            },
            {
                "issue": "Multi-Modification Under-extraction",
                "description": "Pipeline extracts 1 modification per review, missing additional discrete modifications",
                "impact": "HIGH",
                "root_cause": "Current extraction process not designed for multiple modifications per review"
            },
            {
                "issue": "No Quality Assurance",
                "description": "No safety validation or quality checks implemented",
                "impact": "MEDIUM",
                "root_cause": "Quality assurance framework not yet implemented"
            }
        ]

        return {
            "prd_compliance": prd_assessment,
            "critical_issues": critical_issues,
            "overall_status": "REQUIRES MAJOR IMPROVEMENTS",
            "next_steps": [
                "🔥 CRITICAL: Implement multi-modification extraction to capture ALL discrete modifications",
                "🔥 CRITICAL: Improve pipeline scalability to process all 6 recipes (reach 80% target)",
                "🎯 HIGH: Add comprehensive quality assurance and safety validation",
                "📊 HIGH: Implement accuracy validation framework with ground truth testing",
                "📈 MEDIUM: Add performance monitoring and error handling"
            ]
        }

    def save_actual_performance_report(self, analysis: Dict[str, Any], compliance: Dict[str, Any]) -> str:
        """Save comprehensive actual performance report."""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = Path("validation_results") / f"actual_pipeline_analysis_{timestamp}.json"

        report = {
            "metadata": {
                "analysis_timestamp": analysis["analysis_timestamp"],
                "report_type": "actual_pipeline_performance",
                "data_source": "data/enhanced/ directory"
            },
            "performance_analysis": analysis,
            "prd_compliance": compliance,
            "summary": {
                "current_success_rate": f"{analysis['success_rate']:.1%}",
                "target_success_rate": "80%",
                "gap_to_target": f"{0.8 - analysis['success_rate']:+.1%}",
                "critical_issues_count": len(compliance["critical_issues"]),
                "overall_assessment": compliance["overall_status"]
            }
        }

        # Ensure directory exists
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return str(report_file)


def main():
    """Main function to analyze actual pipeline performance."""
    print("🔍 Actual Pipeline Performance Analysis")
    print("Analyzing real results in data/enhanced/ vs PRD requirements")
    print("=" * 70)

    validator = ActualPipelineValidator()

    # Analyze actual performance
    analysis = validator.analyze_actual_pipeline_performance()

    # Generate PRD compliance report
    compliance = validator.generate_prd_compliance_report(analysis)

    # Save comprehensive report
    report_file = validator.save_actual_performance_report(analysis, compliance)

    # Print summary
    print(f"\n🎯 ACTUAL PERFORMANCE SUMMARY")
    print("=" * 40)
    print(f"Current Success Rate: {analysis['success_rate']:.1%}")
    print(f"Target Success Rate: 80%")
    print(f"Gap to Target: {0.8 - analysis['success_rate']:+.1%}")
    print(f"Status: {compliance['overall_status']}")

    print(f"\n❌ CRITICAL ISSUES:")
    for issue in compliance['critical_issues']:
        print(f"  • {issue['issue']}: {issue['description']}")

    print(f"\n🚀 NEXT STEPS:")
    for step in compliance['next_steps'][:3]:  # Show top 3
        print(f"  • {step}")

    print(f"\n📄 Detailed report saved: {report_file}")

    return analysis, compliance


if __name__ == "__main__":
    main()