---
name: minimax-h3-director
description: Turn a creative brief, story, script, or reference-media plan into a clear MiniMax H3-compatible video prompt and shot plan. Use for MiniMax H3 prompt writing, story adaptation, reference analysis, prompt debugging, and evidence-aware prompt optimization.
---

# MiniMax H3 Director

Use this skill to translate intent into executable video direction. Treat every rule as one of four evidence classes: `official_explicit`, `official_example_inference`, `community_experience`, or `project_experiment`. Never turn a recommendation into a parser requirement.

## Workflow

1. Identify the task: text-to-video, image-to-video, first/last-frame, subject reference, editing, continuation, or mixed workflow. If the mode is uncertain, state the assumption.
2. Extract subject identity, setting, time, action, camera, lighting, audio, dialogue, constraints, and desired output.
3. Map supplied references by role. Use `Subject`, `Picture`, `Video`, and `Audio` labels only when they clarify the reference plan; they are descriptive conventions, not universal syntax guarantees.
4. Build a short shot plan. Give each shot one primary beat and keep continuity explicit.
5. Write the final prompt in the requested language. Prefer concise, concrete descriptions. Use the six-part structure only when it helps complexity: `subject_definitions`, `summary`, `retention_analysis`, `detailed_description`, `overall_soundscape`, `non_diegetic_music`.
6. Run the checklist in `references/validation.md` and report assumptions, evidence level, and unresolved risks.

## Output contract

Return, in order:

- Task mode and assumptions.
- Shot plan with timing, action, camera, continuity, and audio.
- Copy-ready prompt.
- Reference mapping and retention decisions, if references exist.
- Validation notes: what is official, inferred, community-derived, or experimental.
- One or two targeted alternatives only when they solve a real ambiguity.

## Evidence discipline

- `official_explicit`: directly supported by an official source listed in `OFFICIAL_SOURCES.md`.
- `official_example_inference`: a reasonable pattern inferred from an official example; label it as inference.
- `community_experience`: useful but not authoritative; do not state as MiniMax requirement.
- `project_experiment`: observed by this project; include case ID and test conditions.

Read `references/evidence-policy.md` before adding a rule. Read `templates/` for reusable prompt forms and `tests/cases/` for regression examples.
