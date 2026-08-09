# Valid deferred-binding fixture

- Target total duration: 20 seconds

## H3 Generation Unit 01

- Episode range: 00:00.000–00:10.000
- Request duration: 10
- Mode: T2VA
- Aspect ratio: 9:16
- Input assets: 0 images, 0 videos, 0 audio, 0 total

### Copy-ready prompt — copy everything inside this block

```text
integrated_multimodal_description: [Shot 1] 2D animation. A runner crosses a rain-soaked rooftop and leaps toward the next building.
overall_soundscape: Rain strikes concrete beneath rapid footsteps.
non_diegetic_music: Fast electronic percussion rises into the leap.
```

## H3 Generation Unit 02

- Episode range: 00:10.000–00:20.000
- Request duration: 10
- Mode: Ref2VA
- Aspect ratio: 9:16
- Input assets: 0 images, 1 video, 0 audio, 1 total
- Prompt status: text_ready
- Asset binding status: pending_upstream
- Execution status: blocked_until_verified

### Reference asset binding manifest — do not copy into the prompt

- <Video 1> | UNIT-01-VIDEO | unit://01/output/video | video | pending_upstream | direct visual and motion continuation

### Prewritten prompt — asset binding pending

```text
subject_definitions:
<Subject 1> is the runner established in <Video 1>.
summary:
[video continuation] Continue the rooftop leap from <Video 1> into the landing and recovery.
retention_analysis:
<Video 1>: fully_preserved - preserve the runner, clothing, rain, screen direction, and motion at the handoff.
detailed_description:
[Shot 1] Continue directly from <Video 1> as the runner lands on the next rooftop. [Shot 2] At 00:05.000, the camera swings beside the runner during the recovery sprint.
overall_soundscape: The landing thuds under heavy rain and accelerating footsteps.
non_diegetic_music: The electronic rhythm resumes at full intensity after the landing.
```
