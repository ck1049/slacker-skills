---
name: manju-project-scaffold
description: Create and maintain long-form 漫剧 project workspaces, shared assets and per-episode live HTML review overviews. Use for creating 漫剧工程, migrating chapters, adding seasons/episodes, organizing global characters/scenes/props, or maintaining consistent adaptation scripts, storyboard prompts, reference materials and current-version production pages.
---

# 漫剧工程脚手架

Use this skill to create and maintain Codex-era 漫剧 projects. Keep the project usable for 200+ chapter adaptations by separating source text, global assets, per-episode assets, and platform rules.

## Core Workflow

1. Identify the 漫剧 workspace root. Prefer the current Git/project root when it contains `基础漫剧工程模板`, `.agents/skills`, or existing work folders such as `正片`, `全局角色`, `全局场景`, and `全局道具`. If uncertain, search upward from the current working directory and avoid hard-coding absolute paths.
2. Create or update the project structure with `scripts/scaffold_manju.py`.
3. Store original novel chapters under `大纲/原文/第XXXX章_原文.txt`.
4. For each chapter, create one episode under `正片/第一季/XX`.
5. Put recurring character, scene, prop, style, audio, and platform rules in global folders first. Put episode-only materials in the episode folder.
6. Generate per-episode outputs using `references/episode-output-spec.md`. Maintain one stable, current-version HTML production overview per episode; read [审阅页规范](references/episode-review-page.md) when creating or updating it. Use the bundled template and renderer rather than inventing a different page for every batch.
7. Check Seedance 2.5 constraints and prompt templates with `references/seedance2.5-production-rules.md`. Distinguish platform capabilities from the selected execution channel; for Canvas CLI, verify its live model/mode parameters before promising executable outputs. Use the legacy `references/seedance2-production-rules.md` only when the user explicitly targets Seedance 2.0.

## Directory Rules

Project root:

- `db`: indexes, metadata, continuity tables.
- `制作规则`: reusable rules, platform constraints, naming conventions, style bible.
- `全局角色`: recurring character profiles and reference prompts.
- `全局场景`: recurring scene profiles and reference prompts.
- `全局道具`: recurring prop/UI/system-object profiles and reference prompts.
- `全局音频`: reusable music, sound effect, voice references.
- `大纲`: source chapters, worldbuilding, season and episode planning.
- `正片`: season and episode production outputs.

Episode root:

- `剧本`: adapted episode script and dialogue/voiceover.
- `分镜/分镜脚本`: Seedance-ready clip prompts.
- `分镜/分镜图`: reference-image prompts and generated storyboard stills.
- `分镜/分镜视频`: generated video clips and notes.
- `角色`, `场景`, `道具`, `音频`: episode-only assets.
- `制作审阅/素材清单.json` and `制作审阅/本集制作总览.html`: current selections, production status and playable/viewable materials. Rebuild the same overview after script, asset, task, review or final-cut changes; hide replaced/rejected media while preserving their source evidence outside the current display.

## Script Usage

Run from the 漫剧 workspace root. Prefer relative paths so the skill remains portable when the project moves.

```powershell
python ".agents/skills/manju-project-scaffold/scripts/scaffold_manju.py" project "作品名" --base "."
python ".agents/skills/manju-project-scaffold/scripts/scaffold_manju.py" season "第二季" --under "作品名/正片"
python ".agents/skills/manju-project-scaffold/scripts/scaffold_manju.py" episodes 02 03 --season "作品名/正片/第一季"
python ".agents/skills/manju-project-scaffold/scripts/render_episode_review.py" "作品名/正片/第一季/02/制作审阅/素材清单.json"
```

If the skill is invoked from outside the project root, first change into the project root or pass project-relative paths from that root.

## Adaptation Standard

All user-facing responses and all deliverables written into a 漫剧 workspace must default to Simplified Chinese. This includes adaptation scripts, storyboard scripts, Seedance prompts, material maps, dialogue, voiceover, audio design, production notes, and validation checklists. Keep English only where required for model parameters, file-format names, proper nouns, or established technical terms. Do not create English production deliverables unless the user explicitly requests another language.

For each chapter-to-episode task:

1. Read the chapter source and existing global materials.
2. Extract new or changed characters, scenes, props, UI/system elements, powers, and audio motifs.
3. Update global materials for recurring elements; write episode-local materials for one-off elements.
4. Produce an episode adaptation script before storyboard clips.
5. Default to Seedance 2.5 standard clips of 4-30 seconds. Prefer 8-15 seconds for dense or continuity-sensitive beats; use 30-180 second super-long mode only for a deliberately timecoded long-form sequence.
6. For every clip, specify duration, aspect ratio, visual style, characters, expressions, actions, lighting, camera angle, camera movement, sound, and reference materials.
7. When continuity matters, create storyboard/reference-image prompts before video prompts.
8. End with a production checklist: clip duration valid, reference count valid, global assets updated, episode assets complete, and the stable HTML overview refreshed from actual current selections and task states.

Read these references as needed:

- `references/episode-output-spec.md`: exact files and sections to create for each episode. 用户认可并要求登记正片时，按其中“正片登记与发布副本”交付存档母版与经字段检查的发布副本，保留必要 AI 标识与真实来源。
- [references/episode-review-page.md](references/episode-review-page.md): current-version selection, incremental refresh, folder/file links and the local HTML template.
- `references/seedance2.5-production-rules.md`: current Seedance 2.5 platform constraints, mode selection, prompt templates, and validation rules.
- `references/seedance2-production-rules.md`: legacy Seedance 2.0 rules for explicitly requested 2.0 deliverables.
