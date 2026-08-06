# Multi-unit H3 episode template

- Target total duration: [seconds]
- Aspect ratio: [ratio]
- Generation-unit count: [count]

## Generation-unit table

| Unit | Episode range | Request duration | Mode | Primary beat | Opening state | Ending state | Next-unit handoff | Input assets |
| --- | --- | ---: | --- | --- | --- | --- | --- | --- |
| 01 | 00:00.000–00:15.000 | 15 | Ref2VA | [...] | [...] | [...] | [...] | 6 images, 0 videos, 2 audio, 8 total |

## H3 Generation Unit 01

- Episode range: 00:00.000–00:15.000
- Request duration: 15
- Mode: Ref2VA
- Aspect ratio: 9:16
- Input assets: 6 images, 0 videos, 2 audio, 8 total
- Opening state: [...]
- Ending state: [...]
- Next-unit handoff: [...]

### Reference asset binding manifest — do not copy into the prompt

- <Picture 1> | CHAR-MAIN | D:\project\characters\main.png | image | protagonist identity and clothing
- <Picture 2> | SCENE-MAIN | D:\project\scenes\main.png | image | environment and lighting
- <Audio 1> | VOICE-MAIN | D:\project\audio\main.mp3 | audio | voice timbre for <Subject 1> (S1)

### Subject-source bindings — do not copy into the prompt

- <Subject 1> <- <Picture 1> | protagonist identity
- <Subject 2> <- <Picture 2> | environment
- <Audio 1> -> <Subject 1> (S1) | voice timbre

### Unit-local shot plan

| Local time | Primary action | Camera | Continuity | Audio |
| --- | --- | --- | --- | --- |
| 0–6s | [...] | [...] | [...] | [...] |
| 6–15s | [...] | [...] | [...] | [...] |

### Copy-ready prompt — copy everything inside this block

```text
[Insert one complete official three-field or six-section prompt. Use only official labels for media; include no filenames or paths. All timestamps are local to this unit.]
```

Repeat the complete `H3 Generation Unit` section for every unit.
