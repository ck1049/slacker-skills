# Changelog

## 1.6.1 — 2026-08-30

- Refreshed the official project-local `h3-prompt-writing` snapshot to MiniMax-H3 commit `d21241f0a4b3acbb34c97dae47fa417b7065e438`.
- Recorded the official portability declaration and tips for 4–15-second duration matching, label consistency, concrete audiovisual detail, and explicit keyframe timeline connections.
- Verified that normalized `base-en.txt` and `ref-en.txt` content is unchanged; no H3 prompt schema or validator behavior changed.
- Documented that the other eight official skills are MiniMax Hub canvas workflows and remain intentionally outside the portable Director runtime.

## 1.6.0 — 2026-08-09

- Added deferred bindings for earlier unit video/audio outputs, derived final frames, and planned generated references.
- Allowed future prewritten prompts to contain their final official media labels without inventing filenames.
- Added explicit text, asset-binding, and execution readiness states.
- Added planning, execution-frontier, and final validation phases.
- Preserved strict existence checks for every binding claimed as verified or currently executable.

## 1.5.0 — 2026-08-07

- Added `T2VA_DIRECT`, `REFERENCE_RECOMMENDED`, and `REFERENCE_REQUIRED` decisions for empty and incomplete projects.
- Preserved a no-reference fast path for simple one-off T2VA tasks.
- Added capability-neutral asset requests without hard dependencies on skills, vendors, models, or platforms.
- Added authorization and cost gates for automatic asset execution.
- Added `planned`, `generated`, `verified`, and `failed` lifecycle states; only verified outputs may receive H3 labels.
- Added an asset-request template and empty-project orchestration regression case.

## 1.4.1 — 2026-08-06

- Added a filesystem-backed asset inventory gate before media-mode routing and label assignment.
- Prohibited invented, implied, convention-derived, and placeholder filenames or paths.
- Made manifest asset existence checking the validator default, with an explicit test-fixture-only bypass.

## 1.4.0 — 2026-08-06

- Added a per-generation-unit reference asset binding manifest with official label, stable asset ID, path, type, and role.
- Reset Picture, Video, and Audio numbering per independent request for portable platform handoff.
- Required exactly one paste-ready prompt block containing labels only, with no filenames, paths, extensions, platform instructions, or project asset IDs.
- Added optional subject-source binding lists for operator clarity.
- Extended deterministic validation to catch missing, duplicate, unused, non-consecutive, or type-incompatible mappings and prompt path leakage.

## 1.3.0 — 2026-08-06

- Added a required long-form workflow for stories and target runtimes beyond 15 seconds.
- Added episode-level generation-unit planning and per-unit local timelines.
- Required one complete official prompt structure per 4–15 second H3 request.
- Added per-unit Ref2VA asset budgets and cross-unit continuity handoffs.
- Added a reusable multi-unit episode template, deterministic validator, and regression case based on a 180-second novel adaptation failure.

## 1.2.0 — 2026-08-06

- Bundled exact copies of the official H3 base-mode and full-reference prompt guides under `references/official/`.
- Removed the runtime dependency on the sibling `skills/official/h3-prompt-writing/` directory.
- Added upstream provenance and SHA-256 records for independently verifiable redistribution.
- Kept the separate project-level official snapshot only as a maintenance and diff source.

## 1.1.0 — 2026-08-06

- Added the official MiniMax H3 repository and bundled `h3-prompt-writing` skill as a primary source.
- Added explicit T2VA, I2VA, FL2VA, L2VA, and Ref2VA routing.
- Adopted the official three-field base-mode and six-section Ref2VA rewrite structures.
- Corrected reference-label guidance: T2VA uses no labels; keyframe and Ref2VA modes follow their official label rules.
- Adopted English rewrite sections while preserving dialogue, lyrics, and visible scene text in their original language.
- Updated templates, validation checks, and regression expectations.

## 1.0.0 — 2026-08-05

- Rebuilt the project as an evidence-aware MiniMax H3 Director skill.
- Added official source register with explicit boundaries and URLs.
- Added four-level evidence policy.
- Added task-mode workflow, shot planning, reference mapping, and validation contract.
- Added reusable simple and six-part templates.
- Added examples and two regression cases.
- Recorded the WeChat article as pending community verification; the source PDF and prior V0.1 directory were not present in the current workspace.
