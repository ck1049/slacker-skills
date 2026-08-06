# Asset binding and paste-ready prompts

Use this contract for every generation unit that submits images, videos, or audio to H3. It separates the operator-facing upload map from the model-facing prompt.

Evidence boundary: the meanings of `<Subject N>`, `<Picture N>`, `<Video N>`, and `<Audio N>` are `official_explicit` from the bundled Ref2VA guide. The external binding-manifest syntax, project asset IDs, copy boundary, and platform-neutral handoff are `project_experiment` conventions designed to make those official labels operational and portable; they are not claimed as MiniMax parser syntax.

## 1. Binding manifest outside the prompt

Before assigning any label, enumerate the files in the user-authorized scope and create an internal verified inventory containing the resolved path, media type, and intended role. A manifest entry may be created only from that inventory.

Hard rules:

- Confirm every manifest path exists and resolves to a readable regular file at generation time.
- Copy the actual filename/path from filesystem results; never compose one from a character name, scene name, script text, or naming convention.
- Treat a mentioned-but-unavailable asset as missing, not supplied. Do not create a label for it.
- Do not use examples such as `D:\project\characters\main.png`, `[character image]`, `TODO`, or guessed extensions in a deliverable.
- If the authorized directory cannot be inspected, state that asset binding is unverified and request access or an explicit file list. Do not emit a supposedly copy-ready media manifest.
- After writing the document, run the validator with existence checking enabled. The test-only `--skip-asset-existence` option must never be used for a user deliverable.

Place this section before the unit-local shot plan:

```markdown
### Reference asset binding manifest — do not copy into the prompt

- <Picture 1> | CHAR-YECUN | D:\project\characters\ye-cun.png | image | character identity and clothing
- <Picture 2> | SCENE-WHITE-FOG | D:\project\scenes\white-fog.png | image | environment and lighting
- <Audio 1> | VOICE-YECUN | D:\project\audio\ye-cun.mp3 | audio | voice timbre for <Subject 1> (S1)
```

Each line has five pipe-separated values:

1. Unit-local official upload label.
2. Stable project asset ID used only for production tracking.
3. Exact local filename or path used by the operator.
4. Asset type: `image`, `video`, or `audio`.
5. Human-readable binding role.

Use absolute paths when the document stays on the same workstation; use project-relative paths for a portable project package. Paths belong only in the manifest.

Resolve project-relative paths against the generated document's directory unless the validator is given an explicit `--asset-root`. The resolved target, not merely the written string, must exist.

Number `<Picture N>`, `<Video N>`, and `<Audio N>` independently, consecutively, and from 1 inside each generation unit. Upload or connect files in manifest order. If a platform displays its own ordering, make that order agree with the manifest before pasting the prompt.

## 2. Optional subject-source bindings

When helpful, add an operator-facing relationship list:

```markdown
### Subject-source bindings — do not copy into the prompt

- <Subject 1> <- <Picture 1> | Ye Cun identity
- <Subject 2> <- <Picture 2> | white-fog environment
- <Audio 1> -> <Subject 1> (S1) | voice timbre
```

This list explains production relationships but does not replace `subject_definitions` inside a Ref2VA prompt.

## 3. Exactly one paste-ready block

Use this boundary:

```markdown
### Copy-ready prompt — copy everything inside this block

```text
[complete official prompt]
```
```

Inside the block:

- Use only official media labels and derived subject labels.
- Write `<Subject 1> is the young man shown in <Picture 1>...` rather than naming the source file.
- Do not mention drive letters, folders, filenames, file extensions, project asset IDs, upload order, node names, platform names, or phrases such as “the file at”.
- Keep the complete official field structure for the selected mode.

The prompt is paste-ready after the user uploads or wires assets according to the manifest. No cross-platform text format can upload files automatically; platform-specific attachment or node wiring remains an operator step.

## 4. Label semantics

- `<Subject N>`: reusable visible content abstracted from one or more references; it is not an uploaded file slot.
- `<Picture N>`: an uploaded image or concrete frame/composition source.
- `<Video N>`: an uploaded video used for editing, continuation, camera, rhythm, or temporal structure.
- `<Audio N>`: an uploaded audio signal used by copy or reference.

An image used only to define a character can still be cited as the source of `<Subject N>` without creating a separate standalone picture definition line. The manifest remains responsible for mapping `<Picture N>` to the real file.

## 5. Platform-neutral handoff

- ComfyUI: load and connect media in manifest order; verify the workflow's media list corresponds to the labels before generation.
- MiniMax Hub or another creator platform: attach the manifest files to the unit in matching order, then paste only the copy-ready block.
- If a platform renumbers or rejects a media type, update the manifest and labels together before generation; never insert local paths into the prompt as a workaround.
