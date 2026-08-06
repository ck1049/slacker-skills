# Valid multi-unit fixture

- Target total duration: 20 seconds

## H3 Generation Unit 01

- Episode range: 00:00.000–00:10.000
- Request duration: 10
- Mode: T2VA
- Aspect ratio: 9:16
- Input assets: 0 images, 0 videos, 0 audio, 0 total

### Copy-ready prompt — copy everything inside this block

```text
integrated_multimodal_description: [Shot 1] 2D animation. A woman enters a dark corridor. [Shot 2] At 00:05.000, the camera cuts to her hand reaching for a metal door.
overall_soundscape: Footsteps echo through the corridor and the door handle clicks.
non_diegetic_music: Low sustained strings at a slow tempo.
```

## H3 Generation Unit 02

- Episode range: 00:10.000–00:20.000
- Request duration: 10
- Mode: Ref2VA
- Aspect ratio: 9:16
- Input assets: 2 images, 0 videos, 1 audio, 3 total

### Reference asset binding manifest — do not copy into the prompt

- <Picture 1> | CHAR-WOMAN | D:\project\woman.png | image | character identity
- <Picture 2> | SCENE-ROOM | D:\project\room.png | image | room environment
- <Audio 1> | VOICE-WOMAN | D:\project\woman.mp3 | audio | voice timbre

### Copy-ready prompt — copy everything inside this block

```text
subject_definitions:
<Subject 1> is the woman defined by Picture 1.
summary:
[reference generation + audio reference] The woman from <Picture 1> opens the door into the room from <Picture 2> and reacts while <Audio 1> guides her voice timbre.
retention_analysis:
<Subject 1>: fully_preserved - identity and clothing from <Picture 1> remain unchanged.
detailed_description:
[Shot 1] The woman from <Picture 1> opens the metal door toward the room established by <Picture 2>. [Shot 2] At 00:06.000, the camera cuts inside the room as she freezes at the threshold while <Audio 1> guides her audible gasp.
overall_soundscape: The hinges scrape and her breathing becomes audible.
non_diegetic_music: A low pulse stops as the room is revealed.
```
