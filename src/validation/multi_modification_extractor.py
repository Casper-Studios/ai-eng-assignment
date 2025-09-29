"""
Enhanced Multi-Modification Extraction System

This module extends the original TweakExtractor to capture ALL discrete modifications
from reviews, addressing the critical gap where reviews like "I added an egg and
halved the sugar" contain multiple modifications but only one was extracted.
"""

import json
import os
import re
from typing import List, Optional, Tuple, Dict, Any

from loguru import logger
from openai import OpenAI
from pydantic import ValidationError

from ..llm_pipeline.models import ModificationObject, Recipe, Review
from ..llm_pipeline.prompts import build_simple_prompt


class MultiModificationExtractor:
    """Enhanced extractor that captures ALL discrete modifications from review text."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the MultiModificationExtractor.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: OpenAI model to use for extraction
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        logger.info(f"Initialized MultiModificationExtractor with model: {model}")

    def build_multi_modification_prompt(
        self, review_text: str, recipe_title: str, ingredients: List[str], instructions: List[str]
    ) -> str:
        """
        Build a specialized prompt for extracting multiple discrete modifications.

        Args:
            review_text: The review text to analyze
            recipe_title: Title of the recipe
            ingredients: List of ingredients
            instructions: List of instructions

        Returns:
            Formatted prompt for multi-modification extraction
        """
        ingredients_text = "\n".join(f"- {ing}" for ing in ingredients)
        instructions_text = "\n".join(f"{i+1}. {inst}" for i, inst in enumerate(instructions))

        prompt = f"""You are analyzing a recipe review to extract ALL discrete modifications mentioned by the reviewer.

CRITICAL: Many reviews contain MULTIPLE separate modifications. For example:
- "I added an egg and halved the sugar" = 2 modifications
- "I used brown sugar instead of white, added vanilla, and baked at 375°F" = 3 modifications
- "I omitted nuts, doubled chocolate chips, and added extra salt" = 3 modifications

Your task is to identify EVERY individual modification and return them as a JSON array.

Recipe: {recipe_title}

Ingredients:
{ingredients_text}

Instructions:
{instructions_text}

Review: "{review_text}"

Return a JSON object with this exact structure:
{{
    "total_modifications_found": <number>,
    "modifications": [
        {{
            "modification_type": "ingredient_substitution|quantity_adjustment|technique_change|addition|removal",
            "reasoning": "explanation of this specific modification",
            "edits": [
                {{
                    "target": "ingredients|instructions",
                    "operation": "replace|add_after|remove",
                    "find": "text to find",
                    "replace": "replacement text (for replace operations)",
                    "add": "text to add (for add_after operations)"
                }}
            ]
        }}
    ]
}}

IMPORTANT RULES:
1. Extract EVERY discrete modification mentioned in the review
2. Each modification should be a separate object in the array
3. If only one modification is found, return an array with one element
4. Count carefully - "I added X and changed Y" = 2 modifications
5. Be precise about what constitutes a separate modification"""

        return prompt

    def extract_all_modifications(
        self,
        review: Review,
        recipe: Recipe,
        max_retries: int = 2,
    ) -> Tuple[List[ModificationObject], int]:
        """
        Extract ALL discrete modifications from a review.

        Args:
            review: Review object containing modification text
            recipe: Original recipe being modified
            max_retries: Number of retry attempts if parsing fails

        Returns:
            Tuple of (List of ModificationObjects, total_count_found)
        """
        if not review.has_modification:
            logger.warning("Review has no modification flag set")
            return [], 0

        prompt = self.build_multi_modification_prompt(
            review.text, recipe.title, recipe.ingredients, recipe.instructions
        )

        logger.debug(f"Extracting ALL modifications from review: {review.text[:100]}...")

        for attempt in range(max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    temperature=0.1,
                    max_tokens=2000,  # Increased for multiple modifications
                )

                raw_output = response.choices[0].message.content
                logger.debug(f"LLM raw output: {raw_output}")

                if not raw_output:
                    logger.warning(f"Attempt {attempt + 1}: Empty response from LLM")
                    continue

                # Parse the JSON response
                response_data = json.loads(raw_output)

                total_found = response_data.get("total_modifications_found", 0)
                modifications_data = response_data.get("modifications", [])

                logger.info(f"LLM reported finding {total_found} total modifications")
                logger.info(f"Parsed {len(modifications_data)} modification objects")

                # Validate each modification
                modifications = []
                for i, mod_data in enumerate(modifications_data):
                    try:
                        modification = ModificationObject(**mod_data)
                        modifications.append(modification)
                        logger.debug(f"  Modification {i+1}: {modification.modification_type}")
                    except ValidationError as e:
                        logger.warning(f"Failed to validate modification {i+1}: {e}")

                if modifications:
                    logger.info(f"Successfully extracted {len(modifications)} valid modifications")
                    return modifications, total_found
                else:
                    logger.warning(f"No valid modifications extracted on attempt {attempt + 1}")

            except json.JSONDecodeError as e:
                logger.warning(f"Attempt {attempt + 1}: Failed to parse JSON: {e}")
                if attempt == max_retries:
                    logger.error(f"Max retries reached. Raw output: {raw_output}")

            except Exception as e:
                logger.error(f"Attempt {attempt + 1}: Unexpected error: {e}")
                if attempt == max_retries:
                    return [], 0

        return [], 0

    def count_discrete_modifications_heuristic(self, review_text: str) -> int:
        """
        Use heuristic patterns to estimate the number of discrete modifications.

        This provides a baseline to compare against LLM extraction.

        Args:
            review_text: The review text to analyze

        Returns:
            Estimated number of discrete modifications
        """
        # Convert to lowercase for pattern matching
        text = review_text.lower()

        # Common patterns that indicate multiple modifications
        patterns = [
            r'\band\b',  # "I added X and changed Y"
            r'\balso\b',  # "I also added..."
            r'\bplus\b',  # "I used X plus Y"
            r'\bthen\b',  # "I did X then Y"
            r'\bnext\b',  # "I did X next I did Y"
            r',\s*(?:and\s+)?(?:i\s+)?(?:also\s+)?(?:added|used|changed|increased|decreased|substituted|omitted)',
            # Comma followed by another action
        ]

        # Start with 1 (assume at least one modification if marked as having one)
        count = 1

        # Count additional modification indicators
        for pattern in patterns:
            matches = re.findall(pattern, text)
            count += len(matches)

        # Look for specific action words that might indicate separate modifications
        action_words = ['added', 'used', 'changed', 'increased', 'decreased',
                       'substituted', 'omitted', 'replaced', 'doubled', 'halved']

        actions_found = []
        for action in action_words:
            if action in text:
                actions_found.append(action)

        # If we found multiple action words, that's a good indicator
        if len(actions_found) > 1:
            count = max(count, len(actions_found))

        logger.debug(f"Heuristic analysis: '{text[:100]}...' -> estimated {count} modifications")
        return count

    def validate_extraction_completeness(
        self,
        review_text: str,
        extracted_modifications: List[ModificationObject],
        expected_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Validate that all discrete modifications were captured.

        Args:
            review_text: Original review text
            extracted_modifications: List of extracted modifications
            expected_count: Expected number of modifications (if known)

        Returns:
            Validation results dictionary
        """
        heuristic_count = self.count_discrete_modifications_heuristic(review_text)
        extracted_count = len(extracted_modifications)

        # Determine if extraction appears complete
        is_complete = True
        completeness_score = 1.0

        if expected_count is not None:
            completeness_score = min(extracted_count / expected_count, 1.0)
            is_complete = extracted_count >= expected_count
        elif heuristic_count > extracted_count:
            completeness_score = extracted_count / heuristic_count
            is_complete = False

        return {
            "review_text": review_text[:200] + "..." if len(review_text) > 200 else review_text,
            "extracted_count": extracted_count,
            "heuristic_estimated_count": heuristic_count,
            "expected_count": expected_count,
            "completeness_score": completeness_score,
            "appears_complete": is_complete,
            "modification_types": [mod.modification_type for mod in extracted_modifications],
            "validation_notes": self._generate_validation_notes(
                review_text, extracted_modifications, heuristic_count
            )
        }

    def _generate_validation_notes(
        self,
        review_text: str,
        extracted_modifications: List[ModificationObject],
        heuristic_count: int
    ) -> List[str]:
        """Generate human-readable validation notes."""
        notes = []

        extracted_count = len(extracted_modifications)

        if extracted_count == 0:
            notes.append("No modifications extracted - review may not contain actionable changes")
        elif extracted_count == 1 and heuristic_count > 1:
            notes.append(f"Only 1 modification extracted but heuristic suggests {heuristic_count} - possible under-extraction")
        elif extracted_count > heuristic_count:
            notes.append("More modifications extracted than heuristically expected - good thoroughness")
        elif extracted_count == heuristic_count:
            notes.append("Extraction count matches heuristic estimate - likely complete")

        # Look for common multi-modification patterns
        text_lower = review_text.lower()
        if ' and ' in text_lower and extracted_count == 1:
            notes.append("Review contains 'and' which often indicates multiple modifications")

        if any(word in text_lower for word in ['also', 'plus', 'additionally']) and extracted_count == 1:
            notes.append("Review contains additive language suggesting multiple changes")

        return notes

    def test_multi_modification_extraction(
        self,
        test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Test multi-modification extraction on a set of test cases.

        Args:
            test_cases: List of test cases with 'review_text', 'expected_count', and 'recipe_data'

        Returns:
            Test results summary
        """
        results = []
        total_completeness = 0

        for i, test_case in enumerate(test_cases):
            logger.info(f"Testing case {i+1}: {test_case['review_text'][:50]}...")

            # Create review and recipe objects
            review = Review(text=test_case['review_text'], has_modification=True)
            recipe = Recipe(
                recipe_id=f"test_{i}",
                title=test_case['recipe_data'].get('title', 'Test Recipe'),
                ingredients=test_case['recipe_data'].get('ingredients', []),
                instructions=test_case['recipe_data'].get('instructions', [])
            )

            # Extract modifications
            modifications, llm_reported_count = self.extract_all_modifications(review, recipe)

            # Validate completeness
            validation = self.validate_extraction_completeness(
                test_case['review_text'],
                modifications,
                test_case.get('expected_count')
            )

            result = {
                "test_case_id": i + 1,
                "review_text": test_case['review_text'],
                "expected_count": test_case.get('expected_count'),
                "extracted_count": len(modifications),
                "llm_reported_count": llm_reported_count,
                "validation": validation,
                "modifications": [
                    {
                        "type": mod.modification_type,
                        "reasoning": mod.reasoning,
                        "edits_count": len(mod.edits)
                    }
                    for mod in modifications
                ]
            }

            results.append(result)
            total_completeness += validation['completeness_score']

        # Calculate summary metrics
        average_completeness = total_completeness / len(test_cases) if test_cases else 0
        successful_extractions = sum(1 for r in results if r['extracted_count'] > 0)
        complete_extractions = sum(1 for r in results if r['validation']['appears_complete'])

        summary = {
            "test_summary": {
                "total_test_cases": len(test_cases),
                "successful_extractions": successful_extractions,
                "complete_extractions": complete_extractions,
                "average_completeness_score": average_completeness,
                "success_rate": successful_extractions / len(test_cases) if test_cases else 0,
                "completeness_rate": complete_extractions / len(test_cases) if test_cases else 0
            },
            "detailed_results": results
        }

        logger.info(f"Multi-modification test complete: {average_completeness:.2%} average completeness")
        return summary