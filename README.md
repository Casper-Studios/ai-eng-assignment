# LLM Recipe Enhancement Pipeline

## Project Overview
This project implements a Python-based LLM pipeline that enhances recipe data by learning from user reviews. The system identifies actionable review feedback, converts it into structured edits, applies those edits to recipe content, and generates enhanced recipe JSON outputs with attribution.

Core flow:
1. Parse recipe and review data from JSON.
2. Extract structured modifications from reviews flagged as containing recipe changes.
3. Apply edits sequentially to ingredients and instructions.
4. Produce enhanced recipes with change provenance and summary metadata.
5. Evaluate pipeline behavior using simple extraction/application metrics.

The target outcome is explainable recipe enhancement, where each applied change can be traced back to its source review.

## Repo Structure
- src/
  - llm_pipeline/
    - pipeline.py: Orchestrates extraction, modification, and generation.
    - tweak_extractor.py: Uses GPT-3.5-turbo to extract structured edits from reviews.
    - recipe_modifier.py: Applies replace, remove, add_after, and add_before operations.
    - enhanced_recipe_generator.py: Creates enhanced recipe payloads with attribution.
    - prompts.py: Prompt templates and extraction guidance.
    - models.py: Pydantic models for recipes, reviews, edits, and outputs.
    - __init__.py
  - evaluate_pipeline.py: End-to-end evaluation script and metrics reporting.
  - scraper_v2.py: Data acquisition utility.
  - test_pipeline.py: Pipeline execution helper.
- data/
  - recipe_*.json: Source recipe documents with review data.
  - enhanced/: Generated enhanced recipes and evaluation artifacts.
- Agent_History.md: Iterative build/debug history with coding agent.
- README.md: Project summary and execution guide.
- REPORT.md: Detailed analysis and engineering rationale.

## Setup & Installation
Prerequisites:
- Python 3.11+ (project uses uv and pyproject configuration).
- uv package manager.
- OpenAI API key with access to GPT-3.5-turbo.

Install and configure:

```bash
uv venv
source .venv/bin/activate
uv pip sync pyproject.toml
```

Set environment variable:

```bash
export OPENAI_API_KEY="your_api_key"
```

Optional: place OPENAI_API_KEY in a local .env file if your workflow loads it automatically.

## Usage
Run evaluation pipeline (recommended for reviewer walkthrough):

```bash
cd src
uv run python evaluate_pipeline.py
```

Alternative run options:

```bash
cd src
uv run python test_pipeline.py single
uv run python test_pipeline.py all
```

What evaluate_pipeline.py does:
1. Loads multiple recipe JSON files.
2. Prints original ingredients and instructions preview.
3. Extracts multiple modifications from reviews with has_modification=true.
4. Applies modifications sequentially.
5. Prints extracted edits, applied changes, and enhanced summary.
6. Saves enhanced outputs for verification.

## Outputs
Primary outputs are written to data/enhanced/.

Artifacts include:
- enhanced_<recipe_id>_<recipe_title>.json: Enhanced recipe documents.
- pipeline_summary_report.json: Aggregated run-level metrics and summary.

Each enhanced recipe captures:
- Updated ingredients/instructions.
- Modifications applied with operation-level change records.
- Source review attribution for traceability.
- Enhancement summary metadata.

Simple evaluation metrics reported by the script:
- Number of modifications extracted.
- Total edits applied.
- Recipe-level success counts.

## Notes
- The extractor is constrained to explicit review content and aims to avoid invented edits.
- Matching is resilient via similarity logic, with fallback behavior when exact find text is not present.
- Modifications are applied in sequence, so ordering can affect final output.
- Output quality depends on review clarity and consistency of source recipe text.
- The project is designed for reviewer readability: deterministic data models, structured logs, and reproducible JSON artifacts.
