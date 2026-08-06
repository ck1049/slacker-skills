# Reference asset orchestration

Use this project-level protocol to decide whether an empty or incomplete project should remain T2VA or acquire reusable reference assets. This workflow is a `project_experiment`; it is not an official MiniMax API contract.

## Decision states

Choose exactly one:

- `T2VA_DIRECT`: the explicit task can be completed without reusable identity, continuity, keyframe, composition, or voice anchors. Produce no asset request and continue immediately.
- `REFERENCE_RECOMMENDED`: references would materially improve consistency or reuse, but a useful T2VA result remains possible. Explain the tradeoff, emit requests when useful, and do not block T2VA.
- `REFERENCE_REQUIRED`: an explicit constraint cannot be met responsibly without a reference, such as a fixed character identity across many independent clips, an exact prop/UI appearance, a mandated opening/ending frame, or a specified voice. Emit requests and block only the dependent media prompt until required assets become verified.

Do not upgrade a task from direct to recommended or required merely because the project is blank, the source is long, or an image/audio tool is installed. Base the decision on explicit continuity and fidelity requirements.

## Fast-path tests

Choose `T2VA_DIRECT` when all applicable answers are yes:

1. Is the output self-contained or allowed to vary between clips?
2. Can the model freely design people, clothing, props, environment, composition, and voice?
3. Is there no exact first/last frame, reusable identity, or cross-request match requirement?
4. Would generating a reference add setup work without solving an explicit production risk?

Typical direct tasks include one-off atmosphere shots, anonymous action, abstract transitions, scenery, mood pieces, and a single short anime scene whose character design may be invented by H3.

## Capability-neutral request protocol

Use `templates/reference-asset-request.yaml`. Declare what outcome is needed, not which implementation must provide it.

Allowed examples:

- `required_capability: image_generation`
- `required_capability: image_editing`
- `required_capability: audio_generation`
- `required_capability: voice_reference_creation`
- `required_capability: video_reference_creation`

Do not write `required_skill`, fixed tool names, vendors, model IDs, API endpoints, or installation paths. The current runtime selects an available compatible capability. If none exists, preserve the request as a handoff artifact.

## Execution authorization

Execute a request only when all are true:

1. The user explicitly requested automatic or end-to-end completion, or separately approved asset generation.
2. A compatible capability is currently available.
3. The action stays inside the authorized files, services, and people.
4. Any paid, quota-consuming, externally published, or irreversible action has the required approval.

Otherwise output the request and continue with T2VA when the decision is recommended. For a required request, stop only the dependent final prompt and identify the missing capability or approval.

## Lifecycle and re-entry

Track each request with one status:

- `planned`: specified but not executed; never bind to an H3 label.
- `generated`: a capability reported output, but the file has not yet passed verification; never bind it.
- `verified`: the resolved file exists, is readable, has the expected media type, and is inside the authorized scope; it may enter the asset inventory.
- `failed`: execution or verification failed; report the reason and choose retry, T2VA degradation, or a blocked handoff according to necessity.

After execution, return control to the Director. Re-scan files rather than trusting proposed output names. Select I2VA, FL2VA, L2VA, or Ref2VA only from verified assets. Planning records and generated-but-unverified outputs are not H3 inputs.

## Minimum-request discipline

Request the smallest reusable set that resolves the production risk. Prefer one coherent character sheet over multiple redundant portraits, one scene anchor over decorative variants, and one verified voice sample over several unused clips. Every request must identify which generation units consume it.
