# Casper Studios Take-Home Assessment

## Objective

Evaluate whether the existing recipe enhancement pipeline actually works beyond a few superficial examples, then fix the most important reliability issues.

## What I Focused On

I prioritized the pipeline behaviors that most directly conflicted with the assessment brief:

1. The pipeline only selected one random modification review, which meant it did not reflect the highest-signal community tweaks and could not combine multiple useful modifications.
2. The modifier was brittle for instruction-level and near-match edits, so valid extracted tweaks often produced zero real changes.
3. Featured tweaks were already present in the data, but the pipeline was not prioritizing them and could double-count duplicate review text.

I intentionally did not spend time on UI or deployment work because the current question is whether the enhancement system is reliable.

## Key Findings

### 1. Random single-review processing was the wrong orchestration model

The existing pipeline chose one random modification review and generated one enhanced recipe from that single extraction. That created three practical issues:

- Results were non-deterministic between runs.
- The system ignored other strong community-tested tweaks in the same recipe.
- It did not match the brief's emphasis on featured or highest-value community modifications.

### 2. Valid edits were often not applied

`RecipeModifier.apply_edit()` matched against whole list items only, then called `original_text.replace(edit.find, ...)`. This broke common cases such as:

- instruction-level edits where the extracted text was only a phrase inside a full instruction line
- fuzzy ingredient matches where the selected candidate was close but not text-identical

In those cases the pipeline could claim success while making no meaningful edit.

### 3. Review ingestion left signal on the table

The scraped data already includes `featured_tweaks`, but the pipeline only parsed `reviews`. The same text also appears in both locations, so the current ingestion path risked duplication while still failing to prioritize the higher-signal source.

## Changes Made

### Pipeline orchestration

- Added review deduplication across `featured_tweaks` and `reviews`.
- Prioritized featured tweaks first, then sorted remaining reviews by rating.
- Replaced single-random-review extraction with sequential extraction across prioritized modification reviews.
- Applied successful modifications sequentially to the recipe and preserved attribution for each concrete change.

### Modifier reliability

- Added substring-aware matching before fuzzy whole-line fallback.
- Added case-insensitive replacement for partial instruction matches.
- Added safer fallback behavior for strong fuzzy matches so a selected line can still be replaced when the raw search string is not text-identical.

### Enhanced recipe generation

- Added support for generating a single enhanced recipe from multiple applied modifications instead of only one.
- Preserved per-review attribution while aggregating summary statistics across all successful changes.

### Testability

- Added dependency injection to the pipeline so the extractor can be stubbed in tests.
- Added focused tests for modifier behavior and multi-review pipeline behavior.

## Validation

Executed:

```bash
uv run python -m unittest discover -s tests -v
```

```bash
uv run python src/test_pipeline.py single
```

```powershell
$env:ALL_RECIPES_MAX_FILES='2'
$env:ALL_RECIPES_MAX_REVIEWS='1'
uv run python src/test_pipeline.py all
```

Covered by tests:

- substring replacement inside a full instruction line
- fuzzy ingredient replacement against a near-match line
- deduping and prioritizing featured tweaks during review parsing
- applying multiple extracted modifications within a single recipe run

Live validation results:

- Unit suite passed: 7 tests
- Single live Gemini run succeeded and generated `data/enhanced/enhanced_10813_best-chocolate-chip-cookies.json`
- Controlled all-recipes Gemini run succeeded as a smoke test with 1 successful enhancement out of 2 recipes under a low-quota setting

## Constraints

I did not run a full unrestricted live sweep across all recipes because Gemini free-tier behavior is still rate- and output-length-sensitive on some reviews. The repo now supports quota-aware validation settings, and the live Gemini checks above confirm that the end-to-end path works with the current configuration.

I also did not run a separate OpenAI-backed live validation in this environment because no `OPENAI_API_KEY` was provided for the assessment repository.

## Files Added For Submission

- `ASSESSMENT.md` - this write-up
- `AGENT_TRAJECTORY.md` - coding agent execution log summary
- `CASPER_HANDOFF_CHECKLIST.md` - final packaging and submission checklist
- `tests/test_recipe_modifier.py`
- `tests/test_pipeline.py`

## Future Improvements

1. Add conflict resolution and deduping across extracted modifications so overlapping edits can be merged more intelligently.
2. Introduce extraction confidence scoring and skip low-confidence LLM outputs rather than applying them blindly.
3. Add a deterministic offline fixture set for representative recipes and reviews so regression testing does not depend on live LLM calls.
4. Improve change attribution to expose more precise line- or token-level diffs for UI rendering.
5. Add ranking heuristics beyond featured status and star rating, such as review helpfulness if that data becomes available.