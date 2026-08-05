---
name: minimax-h3-director
description: Direct creative briefs, stories, scripts, and reference media into official-format MiniMax H3 prompts and shot plans. Use for H3 T2VA, I2VA, FL2VA, L2VA, Ref2VA, story adaptation, reference analysis, prompt debugging, and evidence-aware optimization.
---

# MiniMax H3 Director

Use this self-contained skill as the creative direction, official prompt-format, and validation layer for MiniMax H3. Treat every rule as one of four evidence classes: `official_explicit`, `official_example_inference`, `community_experience`, or `project_experiment`.

Before writing the copy-ready H3 prompt, read the bundled mode-specific official guide:

- T2VA, I2VA, FL2VA, or L2VA: read `references/official/base-en.txt` completely.
- Ref2VA: read `references/official/ref-en.txt` completely; also read `references/official/base-en.txt` when speaker, dialogue, camera, or shot-format details are needed.

The bundled official guides are authoritative for final field names, section order, reference labels, timing notation, and output language. The director workflow remains authoritative for creative interpretation, shot planning, continuity, validation, and evidence reporting.

## Workflow

1. Identify the H3 mode: T2VA, I2VA, FL2VA, L2VA, or full-reference Ref2VA. If the mode is uncertain, state the assumption.
2. Extract subject identity, setting, time, action, camera, lighting, audio, dialogue, constraints, and desired output.
3. Map supplied references by role. For Ref2VA, use the official `<Subject N>`, `<Picture N>`, `<Video N>`, and `<Audio N>` rules. For I2VA, FL2VA, and L2VA, use the official picture-alignment instruction. T2VA uses no reference labels.
4. Build a short shot plan. Give each shot one primary beat and keep continuity explicit.
5. Write planning notes in the user's requested language, but write the copy-ready rewrite sections in English. Preserve dialogue, lyrics, and visible scene text in their original language.
6. For T2VA/I2VA/FL2VA/L2VA, output `integrated_multimodal_description`, `overall_soundscape`, and `non_diegetic_music` in that order. For Ref2VA, output `subject_definitions`, `summary`, `retention_analysis`, `detailed_description`, `overall_soundscape`, and `non_diegetic_music` in that order.
7. Run the checklist in `references/validation.md` and report assumptions, evidence level, and unresolved risks.

## Output contract

Return, in order:

- Task mode and assumptions.
- Shot plan with timing, action, camera, continuity, and audio.
- Copy-ready official-format English prompt.
- Reference mapping and retention decisions, if references exist.
- Validation notes: what is official, inferred, community-derived, or experimental.
- One or two targeted alternatives only when they solve a real ambiguity.

Do not include task assumptions, the planning table, evidence notes, validation notes, or render-setting commentary inside the copy-ready prompt block.

## Evidence discipline

- `official_explicit`: directly supported by an official source listed in `OFFICIAL_SOURCES.md`.
- `official_example_inference`: a reasonable pattern inferred from an official example; label it as inference.
- `community_experience`: useful but not authoritative; do not state as MiniMax requirement.
- `project_experiment`: observed by this project; include case ID and test conditions.

Read `references/evidence-policy.md` before adding a rule. Read `references/official/upstream.md` for bundled-source provenance, `templates/` for reusable prompt forms, and `tests/cases/` for regression examples.
