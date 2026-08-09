# Deferred asset binding

Use deferred binding when a later H3 generation unit must reference an asset that a declared earlier production step will create. This is a `project_experiment` planning protocol outside the official H3 prompt grammar.

## Core distinction

- A fictional asset has no verified file and no declared producer. Reject it.
- A deferred asset has no file yet, but has a unique producer, expected media type, consumer unit, and logical URI. Allow its official label inside the prewritten future prompt while keeping execution blocked.

Never write a guessed future filename. Use one of these logical URIs outside the prompt:

- `unit://01/output/video`: the complete video output of Generation Unit 01.
- `unit://01/output/audio`: an explicitly exported audio output of Generation Unit 01.
- `derive://unit-01/final-frame`: an image extracted from the verified final frame of Unit 01.
- `asset-request://CHAR-MAIN-01`: the output of a declared reference-asset request.

## Manifest syntax

Verified binding:

```markdown
- <Video 1> | UNIT-01-VIDEO | D:\project\outputs\unit-01.mp4 | video | verified | continuation source
```

Deferred upstream binding:

```markdown
- <Video 1> | UNIT-01-VIDEO | unit://01/output/video | video | pending_upstream | continuation source
```

Deferred generated reference:

```markdown
- <Picture 1> | CHAR-MAIN | asset-request://CHAR-MAIN-01 | image | pending_generation | protagonist identity
```

The older five-field manifest form remains equivalent to `verified`. Use the explicit six-field form in new deliverables.

## Unit readiness metadata

For a unit with unresolved bindings, write:

```markdown
- Prompt status: text_ready
- Asset binding status: pending_upstream
- Execution status: blocked_until_verified
```

Its prompt must already contain the correct `<Picture N>`, `<Video N>`, and `<Audio N>` labels, but title the block `Prewritten prompt — asset binding pending`. The text can remain unchanged after resolution; only the manifest URI/status and readiness metadata change.

After the artifact exists and passes validation, replace the logical URI with its real path, set the entry to `verified`, set asset binding status to `verified`, execution status to `copy_ready`, and title the block `Copy-ready prompt`.

## Dependency rules

- A unit may depend only on an earlier unit, never itself or a future unit.
- Reject circular or missing producers.
- Match logical output type to the official label: video to `<Video N>`, audio to `<Audio N>`, final frame to `<Picture N>`.
- Reserve labels independently and consecutively inside each consumer request.
- Count deferred inputs against that consumer's normal H3 input budget.
- Do not claim that a deferred asset was uploaded, attached, analyzed, retained, or copied. Describe the prompt as prewritten until verification.

## Validation phases

- `planning`: allow valid deferred bindings; verify producer order, type, manifest/prompt label consistency, and readiness metadata. Check real paths for entries marked `verified`.
- `execution --through-unit N`: require every media binding consumed by units 1 through N to be verified; allow later units to remain deferred.
- `final`: require every binding in every unit to be verified. This is the default phase.

Planning success means the dependency graph and prompt text are ready, not that all H3 requests are immediately executable.
