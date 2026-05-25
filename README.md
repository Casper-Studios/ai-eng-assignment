# Recipe Enhancement Platform

Automatically enhances recipes by analyzing and applying community-tested modifications from AllRecipes.com. Uses LLM processing to extract meaningful recipe tweaks and apply them with full citation tracking.

## Installation

This project uses [`uv`](https://docs.astral.sh/uv/) for fast, reliable Python package management.

### Prerequisites

- Python 3.13+
- `uv` package manager

## Setup

```bash
# Install dependencies
uv venv
source .venv/bin/activate
uv pip sync pyproject.toml
```

### Environment Variables

Create a `.env` file in the project root:

```env
# Option 1: Google AI Studio / Gemini
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-google-ai-studio-key-here

# Option 2: OpenAI
# LLM_PROVIDER=openai
# OPENAI_API_KEY=your-openai-api-key-here

# Optional overrides
# LLM_MODEL=gemini-3.5-flash
# LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```

The repo now supports either provider:

- `gemini` via Google AI Studio using the OpenAI-compatible Gemini endpoint
- `openai` via the standard OpenAI API

If `LLM_PROVIDER` is not set, the code will prefer `GEMINI_API_KEY` when present, otherwise it falls back to `OPENAI_API_KEY`.

The loader will read either `./.env` or `./.venv/.env`, so an existing virtualenv-local secret file also works.

## Usage

### 1. Scrape Recipes (Optional - data already provided)

```bash
uv run python src/scraper_v2.py
```

### 2. Run Recipe Enhancement Pipeline

```bash
# Test single recipe (chocolate chip cookies)
uv run python src/test_pipeline.py single

# Process all recipes
uv run python src/test_pipeline.py all

# Run focused unit tests
uv run python -m unittest discover -s tests -v
```

### Quota-Aware Gemini Usage

Google AI Studio free-tier limits are tight enough that the default live checks intentionally stay small:

- `single` defaults to `SINGLE_RECIPE_MAX_REVIEWS=1`
- `all` supports `ALL_RECIPES_MAX_FILES` and `ALL_RECIPES_MAX_REVIEWS`

Example PowerShell smoke test:

```powershell
$env:ALL_RECIPES_MAX_FILES='2'
$env:ALL_RECIPES_MAX_REVIEWS='1'
uv run python src/test_pipeline.py all
```

This keeps the batch validation under a small request budget while still exercising the live extraction path.

## Verified Validation

Validated locally on 2026-05-25:

- `uv run python -m unittest discover -s tests -v` -> 7 tests passed
- `uv run python src/test_pipeline.py single` -> succeeded with Gemini and wrote `data/enhanced/enhanced_10813_best-chocolate-chip-cookies.json`
- quota-aware batch run with `ALL_RECIPES_MAX_FILES=2` and `ALL_RECIPES_MAX_REVIEWS=1` -> processed 1 of 2 recipes successfully and wrote `data/enhanced/pipeline_summary_report.json`

The controlled batch run is intended as a free-tier smoke test, not a claim that Gemini free tier is stable enough for a full unrestricted sweep across all recipes.

## Output

### Enhanced Recipes

Enhanced recipes are saved in `data/enhanced/`:

- `enhanced_[recipe_id]_[recipe-name].json` - Individual enhanced recipes with modifications applied
- `pipeline_summary_report.json` - Summary of all processing results

### Data Structure

Original scraped recipes in `data/` directory contain reviews with `has_modification: true` flags. Enhanced recipes include:

```json
{
  "recipe_id": "10813_enhanced",
  "title": "Best Chocolate Chip Cookies (Community Enhanced)",
  "ingredients": ["1 cup butter", "1 additional egg yolk", ...],
  "modifications_applied": [
    {
      "source_review": {
        "text": "I added an extra egg yolk for chewier texture",
        "rating": 5
      },
      "modification_type": "addition",
      "reasoning": "Improves texture and chewiness",
      "changes_made": [...]
    }
  ],
  "enhancement_summary": {
    "total_changes": 1,
    "change_types": ["addition"],
    "expected_impact": "Chewier texture and improved consistency"
  }
}
```

## How It Works

The LLM Analysis Pipeline processes recipes in 3 steps:

1. **Review Prioritization**: Deduplicates review text, prioritizes featured tweaks, and orders remaining modification reviews by signal
2. **Tweak Extraction**: Extracts structured changes from multiple prioritized reviews
3. **Recipe Modification & Attribution**: Applies changes sequentially and generates an enhanced recipe with full attribution back to each source review

Each run produces one enhanced recipe per original recipe, with complete attribution showing what changed, which review suggested it, and the aggregate impact of the applied community tweaks.

## Development

```bash
# Add dependencies
uv add <package_name>

# Run tests
uv run python -m unittest discover -s tests -v
```
