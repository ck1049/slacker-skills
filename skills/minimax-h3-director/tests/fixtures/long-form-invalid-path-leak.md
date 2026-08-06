# Invalid path-leak fixture

- Target total duration: 10 seconds

## H3 Generation Unit 01

- Episode range: 00:00.000–00:10.000
- Request duration: 10
- Mode: Ref2VA
- Aspect ratio: 9:16
- Input assets: 1 image, 0 videos, 0 audio, 1 total

### Reference asset binding manifest — do not copy into the prompt

- <Picture 1> | CHAR-WOMAN | D:\project\woman.png | image | character identity

### Copy-ready prompt — copy everything inside this block

```text
subject_definitions:
<Subject 1> is the woman from D:\project\woman.png and <Picture 1>.
summary:
[reference generation] <Subject 1> enters a room.
retention_analysis:
<Subject 1>: fully_preserved - identity remains unchanged.
detailed_description:
[Shot 1] <Subject 1> enters a room.
overall_soundscape: Her footsteps echo.
non_diegetic_music: N/A
```
