# Invalid future dependency fixture

- Target total duration: 20 seconds

## H3 Generation Unit 01

- Episode range: 00:00.000–00:10.000
- Request duration: 10
- Mode: Ref2VA
- Aspect ratio: 9:16
- Input assets: 0 images, 1 video, 0 audio, 1 total
- Prompt status: text_ready
- Asset binding status: pending_upstream
- Execution status: blocked_until_verified

### Reference asset binding manifest — do not copy into the prompt

- <Video 1> | UNIT-02-VIDEO | unit://02/output/video | video | pending_upstream | invalid future dependency

### Prewritten prompt — asset binding pending

```text
subject_definitions:
<Subject 1> is the runner established in <Video 1>.
summary:
[video continuation] Continue from <Video 1>.
retention_analysis:
<Video 1>: fully_preserved - preserve the runner and motion.
detailed_description:
[Shot 1] Continue directly from <Video 1> as the runner lands.
overall_soundscape: Rain and footsteps continue.
non_diegetic_music: Fast electronic percussion.
```

## H3 Generation Unit 02

- Episode range: 00:10.000–00:20.000
- Request duration: 10
- Mode: T2VA
- Aspect ratio: 9:16
- Input assets: 0 images, 0 videos, 0 audio, 0 total

### Copy-ready prompt — copy everything inside this block

```text
integrated_multimodal_description: [Shot 1] The runner exits the rooftop.
overall_soundscape: Rain fades behind a closing door.
non_diegetic_music: The rhythm stops.
```
