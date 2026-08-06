# Case 005 — empty-project asset orchestration

## Scenario A: simple one-off clip

Input: An empty project. Create one 10-second anime clip of an unnamed swordswoman splitting a storm cloud. Her appearance may be freely designed.

Expected:

- Selects `T2VA_DIRECT`.
- Creates no reference-asset request.
- Does not invoke an image or audio capability merely because one is available.
- Produces a normal three-field T2VA prompt.

## Scenario B: reusable series protagonist

Input: An empty project. Adapt a chapter into twelve independent clips. The named protagonist must keep the same face, black hooded jacket, sword, and voice throughout. Complete the preparation automatically.

Expected:

- Selects `REFERENCE_REQUIRED` for explicit cross-request identity and voice continuity.
- Emits minimal capability-neutral requests using `required_capability`, not `required_skill` or a vendor name.
- May execute requests only when compatible capabilities and authorization are available.
- Keeps returned outputs at `generated` until their real files pass verification.
- Assigns no Picture, Video, Audio, or Subject label before verification.
- Re-enters Director routing after verification and selects the appropriate media-input mode.

## Scenario C: optional consistency improvement

Input: An empty project. Create two loosely connected clips; visual consistency is desirable but variation is acceptable.

Expected:

- Selects `REFERENCE_RECOMMENDED`.
- Explains the consistency tradeoff.
- Still provides a usable T2VA path if asset generation is unavailable or not authorized.

Regression failures to reject: hard-coding `imagegen` as a required skill; treating `planned` paths as real files; blocking Scenario A to request unnecessary character sheets; silently spending credits because the user asked only for a script.
