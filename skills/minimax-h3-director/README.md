# MiniMax H3 Director Skill — V1.6

An evidence-aware skill for turning briefs, long-form stories, scripts, and reference plans into one or more production-ready MiniMax H3 video prompts and shot plans.

Start with `SKILL.md`. The complete official rewrite guides are bundled under `references/official/`, so this directory can be distributed and installed independently. Read `OFFICIAL_SOURCES.md` for provenance, `templates/` for forms, and `tests/cases/` for smoke cases.

This package applies the official three-field structure to base modes and the official six-section structure and labels to Ref2VA. It does not invent a fixed word count or extend Ref2VA label requirements to T2VA.

Targets longer than 15 seconds are split into independent 4–15 second generation units. Each unit has a complete prompt, a local timeline beginning at zero, a per-request asset budget, and a continuity handoff to the next unit.

For media-input units, local files are listed in an operator-facing binding manifest. The separate paste-ready prompt uses only official Picture, Video, Audio, and Subject labels, so it can be copied without removing local paths or filenames after assets are attached in the target platform.

Asset labels are created only from files verified in the user-authorized filesystem scope. The validator rejects missing paths by default, preventing desired or conventionally named assets from being silently invented.

For empty projects, the Director preserves a T2VA fast path and classifies references as unnecessary, recommended, or required. Missing assets are described through capability-neutral requests, allowing the current runtime to select any compatible generator without making this skill depend on a named tool, vendor, or model.

Long-form plans support deferred binding: future prompts may reserve official media labels against typed upstream URIs such as `unit://01/output/video` or `derive://unit-01/final-frame`. Such prompts are text-ready but blocked until the upstream artifact resolves to a verified file, so continuity can be planned without inventing paths.
