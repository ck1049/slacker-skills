# Long-form story to H3 generation units

Use this workflow whenever the requested target runtime exceeds 15 seconds or the source cannot be expressed clearly in one 15-second clip.

## 1. Separate the episode plan from H3 requests

Treat the episode as an editorial timeline made from multiple independent H3 outputs. The episode may be minutes long; each H3 generation unit must be 4–15 seconds.

Do not write one prompt whose timeline continues beyond 15 seconds. Do not treat `[Shot N] At 00:15.000` as the next clip. A new clip is a new request with a new complete prompt and a local timeline beginning at `00:00.000`.

## 2. Adapt prose into audiovisual beats

Extract only observable story information: visible actions, reactions, spatial changes, spoken lines, sound events, and transitions. Compress narration and internal thought into acting, voiceover, UI, props, or omit it when it does not advance the scene.

Group beats by dramatic purpose. End units on useful handoff states such as a completed action, reaction, reveal, door opening, gaze direction, stable pose, or environmental transition. Do not split in the middle of a gesture or spoken line unless continuation is explicitly designed.

Use 15 seconds as a maximum, not a mandatory duration. Prefer a shorter 4–14 second unit when the beat resolves naturally earlier.

## 3. Build the generation-unit table

Before writing prompts, output one row per unit with:

- Unit number.
- Episode-level start and end time.
- H3 request duration.
- Unit mode.
- Primary story beat.
- Opening state.
- Ending state.
- Next-unit handoff.
- Input asset count and roles.

The sum of unit durations should equal the planned episode runtime unless editorial gaps, reused shots, or post-production-only sections are explicitly identified.

## 4. Select mode and assets per unit

Choose T2VA, I2VA, FL2VA, L2VA, or Ref2VA independently for every unit. Existing project assets are not automatically inputs. Include only files that will actually be submitted with that H3 request.

For each Ref2VA request, enforce the current official limits:

- Images: at most 9.
- Videos: at most 3; each 2–15 seconds; combined video duration at most 15 seconds.
- Audio: at most 3; each 2–15 seconds; combined audio duration at most 15 seconds; audio cannot be the only input modality.
- Mixed files: at most 12 total.

Assign stable project-level asset IDs outside prompts, but reset upload labels from 1 inside every independent request. For example, `CHAR-YECUN` may map to `<Picture 1>` in multiple units even when the local asset set changes. Define every relevant `<Subject N>` again inside each self-contained Ref2VA prompt. Omit labels and source assets unused by that unit.

## 5. Write each unit as a standalone request

Use this heading and metadata contract:

```markdown
## H3 Generation Unit 01

- Episode range: 00:00.000–00:15.000
- Request duration: 15
- Mode: Ref2VA
- Aspect ratio: 9:16
- Input assets: 6 images, 0 videos, 2 audio, 8 total
- Opening state: ...
- Ending state: ...
- Next-unit handoff: ...
```

Follow it with a canonical reference asset binding manifest, optional subject-source bindings, a unit-local shot plan, and exactly one fenced copy-ready prompt. Read `asset-binding-and-copy-ready.md` for the required manifest syntax. Use the complete official three-field structure for base modes or complete six-section structure for Ref2VA.

Within a unit:

- `[Shot 1]` has no timestamp.
- Later shots use local cut times such as `[Shot 2] At 00:06.500, ...`.
- Cut times are strictly increasing and strictly less than the request duration.
- The final action resolves by the request duration.
- Episode-level times never appear inside the copy-ready prompt.
- Filenames, paths, drive letters, file extensions, project asset IDs, and upload instructions never appear inside the copy-ready prompt.
- Every `<Picture N>`, `<Video N>`, and `<Audio N>` used inside the prompt has exactly one matching manifest entry.
- Every manifest label is used by the prompt; do not ask users to upload unused files.

## 6. Maintain cross-unit continuity

Carry forward the prior unit's ending state: identity, clothing, held objects, body position, screen direction, location, lighting, weather, damage state, UI values, dialogue state, ambience, and music phase.

When exact visual continuity is important, designate the previous output's final frame as the next unit's first-frame input and select the appropriate supported mode. Do not claim frame continuity unless that frame will actually be supplied.

## 7. Validate before delivery

Reject the document when any of these conditions is true:

- Target runtime exceeds 15 seconds but there is only one copy-ready prompt.
- A request duration is outside 4–15 seconds.
- A unit contains a cut timestamp equal to or greater than its duration.
- A later unit continues timestamps from the episode timeline instead of resetting locally.
- A unit omits required fields for its selected mode.
- A Ref2VA unit exceeds its per-request asset budget.
- Shared labels are used without definitions in the same prompt block.
- A copy-ready block contains a local path, filename, file extension, or platform instruction.
- A prompt media label is missing from the manifest, duplicated, or mapped to the wrong file type.
- Unit ending and next-unit opening states contradict each other.
