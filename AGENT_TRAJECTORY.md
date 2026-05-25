# Agent Trajectory

## Summary

This file records the major steps taken by the coding agent while working through the assessment.

## Execution Log

1. Read the take-home brief and extracted the public repository link.
2. Cloned the repository locally and identified the main control path:
   - `src/llm_pipeline/pipeline.py`
   - `src/llm_pipeline/tweak_extractor.py`
   - `src/llm_pipeline/recipe_modifier.py`
   - `src/llm_pipeline/enhanced_recipe_generator.py`
   - `src/test_pipeline.py`
3. Inspected sample recipe data and confirmed that `featured_tweaks` already existed in the dataset.
4. Identified two primary issues:
   - the pipeline processed one random review instead of prioritized community tweaks
   - the modifier failed on common partial or near-match edits
5. Implemented and validated a fix for modifier application reliability.
6. Refactored the pipeline to:
   - dedupe and prioritize reviews
   - extract multiple modifications
   - apply them sequentially
   - generate a single enhanced recipe with multiple attributions
7. Added focused unit tests for both modifier behavior and pipeline orchestration.
8. Installed the repo dependencies with `uv sync`.
9. Validated the changed slices with:

```bash
uv run python -m unittest discover -s tests -v
```

10. Wrote submission documentation and updated the broader application plan with take-home follow-up status.
11. Added Gemini-compatible provider configuration through the OpenAI client interface so the repo can run without an OpenAI key.
12. Added environment loading support for both `.env` and `.venv/.env` to match the local setup.
13. Fixed CLI path resolution so `uv run python src/test_pipeline.py ...` works from the repository root.
14. Added quota-aware live-run controls for Gemini smoke tests:
   - `SINGLE_RECIPE_MAX_REVIEWS`
   - `ALL_RECIPES_MAX_FILES`
   - `ALL_RECIPES_MAX_REVIEWS`
15. Added a raw JSON extraction fallback when the structured parser fails on Gemini responses.
16. Validated the final state with:

```bash
uv run python -m unittest discover -s tests -v
uv run python src/test_pipeline.py single
```

```powershell
$env:ALL_RECIPES_MAX_FILES='2'
$env:ALL_RECIPES_MAX_REVIEWS='1'
uv run python src/test_pipeline.py all
```

## Notes

- The final single-recipe Gemini run succeeded and generated an enhanced cookie recipe.
- The controlled all-recipes Gemini smoke test succeeded at 1 of 2 recipes under a low-quota configuration; one recipe still exhibited truncated model output on free tier.
- Live OpenAI extraction was not executed because the local environment did not include an `OPENAI_API_KEY` for this repository.
- The highest-priority fixes were chosen to match the assessment prompt's emphasis on correctness, scalability, and product judgment rather than UI polish.