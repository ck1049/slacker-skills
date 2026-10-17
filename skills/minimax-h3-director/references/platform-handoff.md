# Platform handoff checks

Checked 2026-09-29. These are platform-specific checks, not changes to the bundled H3 rewrite grammar. Confirm the target surface before applying them; if unknown, deliver a draft with platform readiness unverified.

## MiniMax hosted API

Sources: [generation guide](https://platform.minimax.io/docs/guides/video-generation) and [V2 request reference](https://platform.minimax.io/docs/api-reference/video-generation-v2-create). Evidence: `official_explicit`.

- Select the user's model explicitly. H3 accepts integer durations 4–15 seconds at 768P or 2K. H3 Max accepts 5–15 seconds at 480P or 768P; do not migrate automatically.
- Check the final submitted prompt against 7000 characters and the serialized request against 64 MB. File limits are 30 MB per image, 50 MB per video, and 15 MB per audio file. Preserve the existing per-unit reference budgets.
- Keyframe roles and reference roles cannot be combined in one request. Text-only requests require a concrete ratio; keyframes use adaptive ratio. Check media dimensions, codecs, and clip durations against the linked request reference before marking handoff ready.
- Public-URL recommendations do not authorize uploading private assets. Verify the chosen transport and its encoded size within the user's authorization.

### Optional Context-IR and 2K regeneration

Checked 2026-10-17. Evidence: `official_explicit`, from the Chinese platform's [Context-IR reference](https://platform.minimax.cn/docs/api-reference/video-generation-v2-h3-context-ir.md) and [regeneration reference](https://platform.minimax.cn/docs/api-reference/video-generation-v2-regeneration.md). This fills a documentation coverage gap; the discovery date is not a launch date. Verify availability and contract on the selected region/account before proposing execution. These endpoints document `MiniMax-H3`; do not extend them to H3 Max or local ComfyUI.

- `POST /v2/h3_context_ir` creates an asynchronous prompt-enhancement task, not a video. It requires a nonempty text input, model and integer duration 4–15; retain the documented role exclusion and ratio rules above. Query the task and read `content.prompt` for the result (`task_type=h3_context_ir`). Record the actual returned prompt separately from the Director draft; local rewriting does not prove that the official service ran.
- `POST /v2/video_regeneration` regenerates a qualifying H3 768P source to 2K. It is not general-purpose video upscaling. Choose exactly one input route: `source_task_id`, or `content` containing exactly one video with `role=base_video`.
- The task-ID route requires account whitelist access and a successful `/v2/video_generation` task owned by the same account, created within the seven-day query window and still queryable. Do not assume an old task ID remains usable.
- The source-video route must preserve every actual input used to produce the source: the final prompt after any Context-IR enhancement and the original reference inputs. A pre-enhancement brief is insufficient. The source must contain audio, run at 24 fps, have width and height divisible by 32, area 589824–1032192 pixels, and 107–362 frames in increments of 17. Check the real file before declaring readiness.
- Regeneration permits up to 40000 characters per text item; Context-IR and ordinary video creation remain limited to 7000. Keep these endpoint limits distinct. The regeneration request remains limited to 64 MB, with reference media restrictions inherited from creation. Save the selected source/task, final prompt and reference manifest as handoff provenance; missing provenance blocks the source-video route.

These are optional handoff checks, not authorization to submit tasks, incur charges, upload assets or regenerate existing work. Keep the user's chosen model and existing works unchanged unless separately authorized. Successful structural checks do not establish regenerated visual or audio quality.

## Native ComfyUI

Source: [ComfyUI native H3 workflows](https://docs.comfy.org/tutorials/video/minimax/minimax-h3-native), authoritative for ComfyUI integration, not MiniMax model-wide requirements.

Native workflow duration snaps to a 17k+5 frame grid at 24 fps; dimensions use multiples of 32. Record requested duration separately from configured frame count and measured output duration. Do not impose hosted HTTP body limits or API integer-duration rules on local inference. Check the actual saved workflow and installed node/model versions before claiming runtime readiness; a current online template alone is insufficient. Do not automatically install nodes, change checkpoints, or enable turbo LoRAs.

The segment validator checks prompt structure and bindings only. Report platform preflight, file validation, and visual/audio acceptance separately; offline validation does not prove rendered quality.
