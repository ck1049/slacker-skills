---
name: minimax-h3-director
description: Direct creative briefs, empty or media-rich projects, long-form stories, scripts, and reference media into production plans and one or more paste-ready official-format MiniMax H3 prompts. Use for H3 T2VA, I2VA, FL2VA, L2VA, Ref2VA, novel-to-video adaptation, deciding whether references are unnecessary, recommended, or required, capability-neutral reference-asset requests, multi-clip episode breakdowns, per-clip asset manifests, creator-platform handoff, continuity planning, reference analysis, prompt debugging, and evidence-aware optimization.
---

# MiniMax H3 Director

Use this self-contained skill as the creative direction, official prompt-format, and validation layer for MiniMax H3. Treat every rule as one of four evidence classes: `official_explicit`, `official_example_inference`, `community_experience`, or `project_experiment`.

Before writing the copy-ready H3 prompt, read the bundled mode-specific official guide:

- T2VA, I2VA, FL2VA, or L2VA: read `references/official/base-en.txt` completely.
- Ref2VA: read `references/official/ref-en.txt` completely; also read `references/official/base-en.txt` when speaker, dialogue, camera, or shot-format details are needed.

The bundled official guides are authoritative for final field names, section order, reference labels, timing notation, and output language. The director workflow remains authoritative for creative interpretation, shot planning, continuity, validation, and evidence reporting.

## Workflow

1. Determine the requested total runtime before writing any H3 prompt. If the target exceeds 15 seconds, or the source contains more story beats than one 15-second clip can execute clearly, read `references/long-form-video-workflow.md` completely and plan multiple H3 generation units.
2. Extract subject identity, setting, story beats, time, action, camera, lighting, audio, dialogue, constraints, and desired output. Adapt prose into observable audiovisual beats; do not map prose paragraphs directly to shots.
3. Before selecting modes, assess reference necessity. Read `references/reference-asset-orchestration.md` completely when the project has no verified media, the task spans multiple generation units, or identity/scene/prop/UI/voice continuity matters. Choose exactly one project-level decision: `T2VA_DIRECT`, `REFERENCE_RECOMMENDED`, or `REFERENCE_REQUIRED`. Do not recommend references merely because generation capability exists.
4. Take the T2VA fast path for a self-contained task that can meet its explicit constraints without reusable identity, continuity, keyframe, or voice anchors. Emit `T2VA_DIRECT`, skip asset requests, and continue directly to the official T2VA prompt. A blank project alone is not a reason to generate references.
5. When references are recommended or required but missing, emit capability-neutral asset requests using `templates/reference-asset-request.yaml`. Declare `required_capability` such as `image_generation` or `audio_generation`; never require a specific skill, model, vendor, or platform. The current agent or orchestrator may choose any available compatible capability.
6. Execute asset requests automatically only when the user requested an end-to-end workflow, the required capability is available, and the action is within the user's authorization and applicable cost boundary. Otherwise hand off the requests without pretending they were executed. `REFERENCE_RECOMMENDED` must not block a usable T2VA result; `REFERENCE_REQUIRED` must block the media-dependent final prompt until required assets are verified.
7. Before selecting a media-input mode, build a verified asset inventory from files actually supplied, attached, generated, or found inside the user-authorized search scope. Resolve every path and confirm it is a readable file. Track each request as `planned`, `generated`, `verified`, or `failed`; only `verified` assets may receive H3 labels. Never infer an asset from prose, a directory name, an expected production convention, or a desired shot. Never invent a filename, path, extension, asset ID, upload label, or placeholder asset.
8. For each generation unit independently, identify the H3 mode: T2VA, I2VA, FL2VA, L2VA, or full-reference Ref2VA. A long-form project may use different modes across units. Map only verified assets needed by that unit and enforce its input-asset budget. When a unit has media inputs, read `references/asset-binding-and-copy-ready.md` completely and output a unit-local asset binding manifest before the prompt. Reset `<Picture N>`, `<Video N>`, and `<Audio N>` numbering from 1 for each independent request. For Ref2VA, use the official `<Subject N>` rules. For I2VA, FL2VA, and L2VA, use the official picture-alignment instruction. T2VA uses no reference labels or manifest.
9. Build the episode-level generation-unit table first, then a short shot plan inside each unit. Keep every unit between 4 and 15 seconds, give each shot one primary beat, and make handoff continuity explicit.
10. Write one self-contained copy-ready prompt block per generation unit. Keep local filenames, paths, asset IDs, upload instructions, planning notes, and platform instructions outside that block. Inside it, refer to uploaded media only through official `<Picture N>`, `<Video N>`, and `<Audio N>` labels and derived `<Subject N>` labels. Reset every unit's internal timeline to `00:00.000`; every later cut time must be strictly less than that unit's duration.
11. Write planning notes in the user's requested language, but write copy-ready rewrite sections in English. Preserve dialogue, lyrics, and visible scene text in their original language.
12. For each T2VA/I2VA/FL2VA/L2VA unit, output `integrated_multimodal_description`, `overall_soundscape`, and `non_diegetic_music` in that order. For each Ref2VA unit, output `subject_definitions`, `summary`, `retention_analysis`, `detailed_description`, `overall_soundscape`, and `non_diegetic_music` in that order.
13. Run the checklist in `references/validation.md`. For multi-unit documents, run `python scripts/validate_h3_segments.py <document.md>` and resolve every error before delivery. Do not use `--skip-asset-existence` for a user deliverable.

## Output contract

Return, in order:

- Total target runtime, adaptation assumptions, and generation-unit count.
- Reference decision and concise rationale. Include asset requests and their lifecycle states only for `REFERENCE_RECOMMENDED` or `REFERENCE_REQUIRED`.
- Episode-level generation-unit table with episode range, request duration, mode, story beat, continuity handoff, and per-unit asset budget.
- Per-unit asset binding manifest, optional subject-source binding list, shot plan, and then exactly one self-contained official-format English prompt block.
- Reference mapping and retention decisions, if references exist.
- Validation notes: what is official, inferred, community-derived, or experimental.
- One or two targeted alternatives only when they solve a real ambiguity.

Do not include task assumptions, planning tables, evidence notes, validation notes, platform instructions, filenames, paths, file extensions, or local asset IDs inside the copy-ready prompt block. The user must be able to copy everything inside the block without editing after attaching assets according to the manifest.

For a target longer than 15 seconds, do not collapse all units into one shared three-field or six-section prompt. Shared character and continuity bibles may appear once at document level, but every copy-ready block must repeat the complete mode-required fields and include only references actually submitted for that unit.

## Evidence discipline

- `official_explicit`: directly supported by an official source listed in `OFFICIAL_SOURCES.md`.
- `official_example_inference`: a reasonable pattern inferred from an official example; label it as inference.
- `community_experience`: useful but not authoritative; do not state as MiniMax requirement.
- `project_experiment`: observed by this project; include case ID and test conditions.

Read `references/evidence-policy.md` before adding a rule. Read `references/official/upstream.md` for bundled-source provenance, `references/reference-asset-orchestration.md` for decoupled asset decisions and execution, `references/long-form-video-workflow.md` for multi-clip adaptation, `references/asset-binding-and-copy-ready.md` for portable media handoff, `templates/` for reusable prompt forms, and `tests/cases/` for regression examples.
