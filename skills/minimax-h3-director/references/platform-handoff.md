# Platform handoff checks

Checked 2026-09-29. These are platform-specific checks, not changes to the bundled H3 rewrite grammar. Confirm the target surface before applying them; if unknown, deliver a draft with platform readiness unverified.

## MiniMax hosted API

Sources: [generation guide](https://platform.minimax.io/docs/guides/video-generation) and [V2 request reference](https://platform.minimax.io/docs/api-reference/video-generation-v2-create). Evidence: `official_explicit`.

- Select the user's model explicitly. H3 accepts integer durations 4–15 seconds at 768P or 2K. H3 Max accepts 5–15 seconds at 480P or 768P; do not migrate automatically.
- Check the final submitted prompt against 7000 characters and the serialized request against 64 MB. File limits are 30 MB per image, 50 MB per video, and 15 MB per audio file. Preserve the existing per-unit reference budgets.
- Keyframe roles and reference roles cannot be combined in one request. Text-only requests require a concrete ratio; keyframes use adaptive ratio. Check media dimensions, codecs, and clip durations against the linked request reference before marking handoff ready.
- Public-URL recommendations do not authorize uploading private assets. Verify the chosen transport and its encoded size within the user's authorization.

## Native ComfyUI

Source: [ComfyUI native H3 workflows](https://docs.comfy.org/tutorials/video/minimax/minimax-h3-native), authoritative for ComfyUI integration, not MiniMax model-wide requirements.

Native workflow duration snaps to a 17k+5 frame grid at 24 fps; dimensions use multiples of 32. Record requested duration separately from configured frame count and measured output duration. Do not impose hosted HTTP body limits or API integer-duration rules on local inference. Check the actual saved workflow and installed node/model versions before claiming runtime readiness; a current online template alone is insufficient. Do not automatically install nodes, change checkpoints, or enable turbo LoRAs.

The segment validator checks prompt structure and bindings only. Report platform preflight, file validation, and visual/audio acceptance separately; offline validation does not prove rendered quality.
