# Official source register

Last checked: 2026-08-30 against upstream commit `d21241f0a4b3acbb34c97dae47fa417b7065e438`. This file is an indexed, human-maintained register. Exact copies of the official mode guides required at runtime are bundled under `references/official/`; a separate project-level snapshot remains available for update comparison.

## Official sources

| ID | Source | Use | Evidence boundary |
|---|---|---|---|
| O-01 | https://platform.minimax.io/docs/guides/video-generation | API modes and prompt field behavior | The page documents text-to-video, image-to-video, first/last-frame, and subject-reference workflows. It does not establish a universal six-section grammar. |
| O-02 | https://platform.minimaxi.com/docs/guides/video-prompt | MiniMax video prompt guidance | Use the page's current examples and recommendations; verify wording when updating. |
| O-03 | https://huggingface.co/MiniMaxAI | MiniMax maintained model materials | Model cards and repositories are official only when published under the MiniMaxAI organization; model-specific claims must cite the exact artifact. |
| O-04 | https://github.com/MiniMax-AI/MiniMax-H3 | Official H3 model repository and bundled prompt-writing skill | `skills/h3-prompt-writing/` is authoritative for current H3 rewrite fields, ordering, labels, timing notation, and language rules. Track upstream changes because the `main` branch can move. |

## Current interpretation

- H3's official bundled skill defines T2VA, I2VA, FL2VA, L2VA, and Ref2VA modes (O-04).
- Base modes use three ordered fields: `integrated_multimodal_description`, `overall_soundscape`, and `non_diegetic_music`. Keyframe modes add a mode-specific picture-alignment instruction (O-04).
- Ref2VA uses six ordered sections and stable `<Subject N>`, `<Picture N>`, `<Video N>`, and `<Audio N>` labels according to asset role (O-04).
- Official rewrite sections are written in English while dialogue, lyrics, and visible scene text preserve their original language (O-04).
- Official tips explicitly require matching the description to 4–15 seconds, keeping media labels consistent, preferring concrete audiovisual detail over abstract quality words, and connecting keyframes clearly to the timeline (O-04).
- These are official rewrite-format rules for the bundled skill, not a claim that arbitrary prose submitted through every H3 surface will fail parsing.

## Official skill ecosystem boundary

The official repository now lists one portable `h3-prompt-writing` skill plus eight style-specific production skills. The style skills depend on MiniMax Hub canvas tools such as image/video generation, canvas nodes, and choice cards. They are upstream workflow examples, not runtime dependencies of this portable Director, and are not bundled here.

## Source maintenance

On each update, record URL, access date, changed section, exact claim, evidence class, and impact in `CHANGELOG.md`. Do not silently promote community advice to official status.
