# Casper Take-Home Report

## Assumptions
1. Reviews marked with has_modification=true are higher-signal candidates for actionable recipe edits.
2. Not every flagged review will produce valid, structured edits after LLM extraction.
3. Ingredient and instruction text may vary slightly, so fuzzy matching is required for robust edit application.
4. Sequential application is acceptable even when multiple reviews suggest overlapping or conflicting edits.
5. Reviewer trust is improved when every modification can be traced to source review text.

## Problem Analysis & Solution Approach
The core challenge is converting unstructured, opinionated review language into reliable, auditable recipe updates. A naive approach either overfits to free text or applies risky changes without traceability.

The implemented approach uses a structured, staged pipeline:
1. Parse source recipes and associated reviews from JSON.
2. Select reviews with explicit modification intent.
3. Use GPT-3.5-turbo to extract machine-readable modification objects (type, reasoning, edit list).
4. Apply edits with operation-aware logic over ingredients/instructions.
5. Generate enhanced recipe outputs that preserve provenance and summarize impacts.

This architecture separates extraction from transformation and keeps each stage observable through logs and typed models.

## Technical Decisions & Rationale
1. Pydantic data models for contract enforcement
Rationale: Early validation catches malformed extraction outputs and prevents silent downstream corruption.

2. LLM extraction constrained to JSON schema
Rationale: Structured extraction reduces parsing ambiguity and supports deterministic application logic.

3. Multi-review processing with sequential application
Rationale: A single review often misses useful community adjustments. Processing the first N flagged reviews improves coverage while remaining bounded.

4. Similarity-based matching with fallback replacement
Rationale: Recipe text rarely matches review phrasing exactly. Similarity search plus full-line fallback improves edit applicability without losing control.

5. Attribution-first enhanced output format
Rationale: Casper reviewers need inspectable changes. Each modification is linked to source review content and reasoning.

6. Scripted evaluation with simple metrics
Rationale: Quick performance signals (modifications extracted, edits applied, success counts) help validate pipeline behavior without requiring full benchmark infrastructure.

## Implementation Details & Challenges
1. Challenge: Reviews contain multiple independent modifications
Resolution: Extraction prompt and processing were updated to capture all distinct edits from a single review, not just one.

2. Challenge: Drift between single-modification and batch APIs
Resolution: Pipeline and evaluator were refactored to use extract_multiple_modifications and batch application consistently.

3. Challenge: No-op changes being recorded as applied
Resolution: Modifier now records change history only when text actually changes.

4. Challenge: Fuzzy matches that do not contain exact find text
Resolution: Replace logic now swaps the entire matched line when exact substring replacement is impossible, preserving progress and auditability.

5. Challenge: Balancing robustness with conservatism
Resolution: Prompt instructions explicitly discourage invented modifications and encourage exact line alignment to recipe text.

6. Challenge: Keeping outputs reviewer-friendly
Resolution: Evaluation script prints original content previews, extracted edits, applied changes, and summarized outcomes; artifacts are saved under data/enhanced.

## Future Improvements
1. Conflict detection and resolution strategy
Detect contradictory edits across reviews and rank by confidence, recency, or reviewer quality.

2. Stronger extraction quality controls
Add post-extraction validators for unsupported operations, invalid sections, and impossible replacements.

3. Better edit scoring and confidence
Introduce confidence fields per edit and use them to gate high-risk modifications.

4. Expanded evaluation framework
Add golden datasets, precision/recall-style metrics for extraction, and regression tests for modifier behavior.

5. Cost and latency optimizations
Batch API calls where possible, cache repeated prompt contexts, and add optional lower-cost model fallback.

6. Product-facing output improvements
Add human-readable diffs and per-change impact tags to help non-technical reviewers assess enhancements faster.

7. Broader operation support
Extend edit operations beyond current set and add explicit conflict semantics for insertion/removal ordering.
