# Project context

This project continues the Codex task transferred from the ChatGPT conversation “分支 · 互联网大厂AI亏损分析”.

## Objective

Maintain a MiniMax H3 Director Skill that converts briefs, stories, scripts, and reference-media plans into usable video prompts and shot plans.

## Decisions carried forward

- Use MiniMax official public materials as the authoritative source layer.
- Keep official explicit claims, official-example inferences, community experience, and project experiments separate.
- Treat the supplied WeChat article as community material, never as an official source.
- Do not claim that six sections, English-only prompting, fixed order, fixed word count, or Subject/Picture/Video/Audio labels are mandatory without a direct official citation.
- Actual video generation and human evaluation remain necessary for behavioral validation.

## Input gap

The original `/mnt/data/minimax-h3-director-skill` directory, V0.1 ZIP, and referenced PDF were not available in the current desktop workspace. V1.0 was reconstructed from the handoff conversation and current official public URLs; this limitation is recorded in `CHANGELOG.md` and `references/community-wechat-article.md`.

## Current state

Version 1.0.0. The project contains the skill, source register, evidence policy, templates, examples, regression cases, changelog, version notes, and update process.
