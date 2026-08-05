# Official source register

Last checked: 2026-08-05. This file is an indexed, human-maintained register; it is not a downloaded copy of MiniMax documentation.

## Official sources

| ID | Source | Use | Evidence boundary |
|---|---|---|---|
| O-01 | https://platform.minimax.io/docs/guides/video-generation | API modes and prompt field behavior | The page documents text-to-video, image-to-video, first/last-frame, and subject-reference workflows. It does not establish a universal six-section grammar. |
| O-02 | https://platform.minimaxi.com/docs/guides/video-prompt | MiniMax video prompt guidance | Use the page's current examples and recommendations; verify wording when updating. |
| O-03 | https://huggingface.co/MiniMaxAI | MiniMax maintained model materials | Model cards and repositories are official only when published under the MiniMaxAI organization; model-specific claims must cite the exact artifact. |

## Current interpretation

- Official API documentation supports a prompt describing the requested video and documents several input modes. Camera-motion tokens shown in API examples are model/mode-specific examples, not a universal requirement (O-01).
- A structured prompt can improve clarity for complex work, but this project does not claim that a six-part prompt, English, XML-like tags, a fixed order, or a fixed word count is mandatory unless a future official source explicitly says so.
- `Subject/Picture/Video/Audio`, `retention_analysis`, and the six-part layout are tracked as community material or project conventions until an exact official source passage is attached.

## Source maintenance

On each update, record URL, access date, changed section, exact claim, evidence class, and impact in `CHANGELOG.md`. Do not silently promote community advice to official status.
