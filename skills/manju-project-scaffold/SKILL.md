---
name: manju-project-scaffold
description: Create and maintain long-form 漫剧 project workspaces for novel-to-AI-video adaptation. Use when the user asks to create a new 漫剧工程, migrate chapter source text, add seasons or episodes, organize global characters/scenes/props, or produce consistent per-episode artifacts for 即梦 Seedance 2.5, including chapter adaptation scripts, storyboard prompts, reference-image prompts, and reusable production rules.
---

# 漫剧工程脚手架

Use this skill to create and maintain Codex-era 漫剧 projects. Keep the project usable for 200+ chapter adaptations by separating source text, global assets, per-episode assets, and platform rules.

## Core Workflow

1. Identify the 漫剧 workspace root. Prefer the current Git/project root when it contains `基础漫剧工程模板`, `.agents/skills`, or existing work folders such as `正片`, `全局角色`, `全局场景`, and `全局道具`. If uncertain, search upward from the current working directory and avoid hard-coding absolute paths.
2. Create or update the project structure with `scripts/scaffold_manju.py`.
3. Store original novel chapters under `大纲/原文/第XXXX章_原文.txt`.
4. For each chapter, create one episode under `正片/第一季/XX`.
5. Put recurring character, scene, prop, style, audio, and platform rules in global folders first. Put episode-only materials in the episode folder.
6. Generate per-episode outputs using `references/episode-output-spec.md`.
7. Check Seedance 2.5 constraints and prompt templates with `references/seedance2.5-production-rules.md`. Use the legacy `references/seedance2-production-rules.md` only when the user explicitly targets Seedance 2.0.

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

## Script Usage

Run from the 漫剧 workspace root. Prefer relative paths so the skill remains portable when the project moves.

```powershell
python ".agents/skills/manju-project-scaffold/scripts/scaffold_manju.py" project "作品名" --base "."
python ".agents/skills/manju-project-scaffold/scripts/scaffold_manju.py" season "第二季" --under "作品名/正片"
python ".agents/skills/manju-project-scaffold/scripts/scaffold_manju.py" episodes 02 03 --season "作品名/正片/第一季"
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
8. End with a production checklist: clip duration valid, reference count valid, global assets updated, episode assets complete.

Read these references as needed:

- `references/episode-output-spec.md`: exact files and sections to create for each episode.
- `references/seedance2.5-production-rules.md`: current Seedance 2.5 platform constraints, mode selection, prompt templates, and validation rules.
- `references/seedance2-production-rules.md`: legacy Seedance 2.0 rules for explicitly requested 2.0 deliverables.
