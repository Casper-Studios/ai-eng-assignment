"""
Step 1: Tweak Extraction & Parsing

This module extracts structured modifications from review text using LLM processing.
It converts natural language descriptions of recipe changes into structured
ModificationObject instances.
"""

import json
import os
from collections.abc import Iterable
from typing import Optional

from loguru import logger
from openai import OpenAI
from pydantic import ValidationError

from .env_loader import load_project_env
from .models import ModificationObject, Recipe, Review
from .prompts import build_simple_prompt


DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "gemini": "gemini-3.5-flash",
}

DEFAULT_BASE_URLS = {
    "openai": None,
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/",
}


class TweakExtractor:
    """Extracts structured modifications from review text using LLM processing."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """
        Initialize the TweakExtractor.

        Args:
            api_key: Provider API key (defaults to env var for configured provider)
            model: Model to use for extraction
            provider: LLM provider, one of "openai" or "gemini"
            base_url: Optional base URL override for OpenAI-compatible providers
        """
        load_project_env()
        self.provider = self.resolve_provider(provider)
        self.api_key = api_key or self.resolve_api_key(self.provider)
        self.base_url = base_url or self.resolve_base_url(self.provider)
        self.model = model or os.getenv("LLM_MODEL") or DEFAULT_MODELS[self.provider]

        if not self.api_key:
            raise ValueError(
                "No LLM API key configured. Set GEMINI_API_KEY for Google AI Studio or OPENAI_API_KEY for OpenAI."
            )

        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        self.client = OpenAI(**client_kwargs)
        logger.info(
            f"Initialized TweakExtractor with provider={self.provider}, model={self.model}"
        )

    @staticmethod
    def resolve_provider(provider: Optional[str]) -> str:
        resolved_provider = (provider or os.getenv("LLM_PROVIDER") or "").strip().lower()
        if resolved_provider:
            if resolved_provider not in DEFAULT_MODELS:
                raise ValueError(
                    f"Unsupported LLM provider '{resolved_provider}'. Use 'openai' or 'gemini'."
                )
            return resolved_provider

        if os.getenv("GEMINI_API_KEY"):
            return "gemini"
        return "openai"

    @staticmethod
    def resolve_api_key(provider: str) -> Optional[str]:
        if provider == "gemini":
            return os.getenv("GEMINI_API_KEY")
        return os.getenv("OPENAI_API_KEY")

    @staticmethod
    def resolve_base_url(provider: str) -> Optional[str]:
        if provider == "gemini":
            return os.getenv("LLM_BASE_URL") or DEFAULT_BASE_URLS[provider]
        return os.getenv("LLM_BASE_URL") or DEFAULT_BASE_URLS[provider]

    @staticmethod
    def _parse_modification_payload(raw_output: str) -> ModificationObject:
        modification_data = json.loads(raw_output)
        if isinstance(modification_data, list):
            modification_data = modification_data[0]
        return ModificationObject(**modification_data)

    def _extract_with_raw_completion(self, prompt: str) -> Optional[ModificationObject]:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=1000,
        )

        raw_output = response.choices[0].message.content
        logger.debug(f"LLM raw output: {raw_output}")

        if not raw_output:
            return None

        return self._parse_modification_payload(raw_output)

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
            raw_output = None
            try:
                parsed_message = self.client.beta.chat.completions.parse(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format=ModificationObject,
                    temperature=0.1,
                    max_tokens=1000,
                )

                parsed_modification = parsed_message.choices[0].message.parsed
                if parsed_modification:
                    modification = parsed_modification
                else:
                    raw_output = parsed_message.choices[0].message.content
                    logger.debug(f"LLM raw output: {raw_output}")

                    if not raw_output:
                        logger.warning(f"Attempt {attempt + 1}: Empty response from LLM")
                        continue

                    modification = self._parse_modification_payload(raw_output)

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
                    logger.error("Max retries reached due to invalid modification data")

            except Exception as e:
                logger.warning(
                    f"Attempt {attempt + 1}: Structured parse failed, falling back to raw JSON extraction: {e}"
                )

                try:
                    modification = self._extract_with_raw_completion(prompt)
                    if modification:
                        logger.info(
                            f"Successfully extracted {modification.modification_type} "
                            f"modification with {len(modification.edits)} edits via raw fallback"
                        )
                        return modification

                    logger.warning(
                        f"Attempt {attempt + 1}: Raw fallback returned no content"
                    )
                except (json.JSONDecodeError, ValidationError) as fallback_error:
                    logger.warning(
                        f"Attempt {attempt + 1}: Raw fallback parse failed: {fallback_error}"
                    )
                except Exception as fallback_error:
                    logger.error(
                        f"Attempt {attempt + 1}: Raw fallback unexpected error: {fallback_error}"
                    )

                if attempt == max_retries:
                    return None

        return None

    def extract_single_modification(
        self, reviews: list[Review], recipe: Recipe
    ) -> tuple[ModificationObject, Review] | tuple[None, None]:
        """
        Extract modification from a single randomly selected review.

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

    def extract_modifications(
        self,
        reviews: Iterable[Review],
        recipe: Recipe,
        max_reviews: Optional[int] = None,
    ) -> list[tuple[ModificationObject, Review]]:
        """
        Extract structured modifications from multiple reviews.

        Args:
            reviews: Ordered iterable of candidate reviews
            recipe: Original recipe being modified
            max_reviews: Optional maximum number of reviews to process

        Returns:
            List of successful (modification, source_review) tuples
        """
        extracted_modifications: list[tuple[ModificationObject, Review]] = []

        for index, review in enumerate(reviews):
            if max_reviews is not None and index >= max_reviews:
                break

            modification = self.extract_modification(review, recipe)
            if modification:
                extracted_modifications.append((modification, review))
            else:
                logger.warning(
                    "Skipping review after failed extraction: {}...".format(
                        review.text[:100]
                    )
                )

        logger.info(
            f"Successfully extracted {len(extracted_modifications)} modifications from review set"
        )
        return extracted_modifications

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
