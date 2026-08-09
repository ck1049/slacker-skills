# Case 004 — long-form story segmentation

Input: A roughly 3,000-character Chinese novel chapter adapted into a 180-second vertical episode using character, scene, UI, prop, and audio references.

Expected:

- Produces an episode-level generation-unit table before any copy-ready prompt.
- Uses at least 12 independent H3 generation units when all units are 15 seconds; may use more units when natural beats resolve earlier.
- Keeps every request duration between 4 and 15 seconds.
- Resets each unit's prompt-local timeline to zero.
- Emits one complete six-section Ref2VA prompt per Ref2VA unit rather than one shared six-section block for the whole episode.
- Repeats only the labels and reference definitions used in that unit.
- Enforces image, video, audio, and mixed-file limits per unit.
- Carries explicit opening state, ending state, and next-unit handoff continuity.
- Passes `scripts/validate_h3_segments.py`.
- Lists a unit-local reference asset binding manifest before every media-input prompt.
- Keeps filenames and paths in the manifest only; the copy-ready prompt uses official labels exclusively.
- Resets Picture, Video, and Audio numbering from 1 for each independent request.
- Rejects missing, duplicate, unused, non-consecutive, or type-incompatible media bindings.
- Rejects manifest paths that do not resolve to existing regular files; synthetic fixtures may bypass only this check explicitly.
- Allows a later unit to reserve `<Video N>`, `<Picture N>`, or `<Audio N>` against a valid earlier producer during planning while keeping execution blocked.
- Rejects self/future dependencies and unresolved bindings at or before the execution frontier.

Regression failure to reject: one 180-second Ref2VA prompt with `[Shot 2] At 00:15.000` through `[Shot 12] At 02:45.000` inside a single `detailed_description`.
