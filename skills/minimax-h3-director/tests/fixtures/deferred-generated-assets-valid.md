# Valid deferred generated image and audio fixture

- Target total duration: 10 seconds

## Planned asset requests

```yaml
asset_request_id: CHAR-HERO-01
required_capability: image_generation
status: planned
---
asset_request_id: VOICE-HERO-01
required_capability: voice_reference_creation
status: planned
```

## H3 Generation Unit 01

- Episode range: 00:00.000–00:10.000
- Request duration: 10
- Mode: Ref2VA
- Aspect ratio: 9:16
- Input assets: 1 image, 0 videos, 1 audio, 2 total
- Prompt status: text_ready
- Asset binding status: pending_generation
- Execution status: blocked_until_verified

### Reference asset binding manifest — do not copy into the prompt

- <Picture 1> | CHAR-HERO | asset-request://CHAR-HERO-01 | image | pending_generation | protagonist identity
- <Audio 1> | VOICE-HERO | asset-request://VOICE-HERO-01 | audio | pending_generation | protagonist voice timbre

### Prewritten prompt — asset binding pending

```text
subject_definitions:
<Subject 1> is the protagonist defined by <Picture 1> and voiced with the timbre in <Audio 1>.
summary:
[reference generation + audio reference] The protagonist enters a silent hall and calls for an answer.
retention_analysis:
<Subject 1>: fully_preserved - preserve identity and clothing from <Picture 1>; use <Audio 1> only as voice-timbre reference.
detailed_description:
[Shot 1] The protagonist from <Picture 1> enters the hall. [Shot 2] At 00:05.000, the camera pushes close as the protagonist calls “有人吗？” using the voice timbre referenced by <Audio 1>.
overall_soundscape: Footsteps echo through the empty hall beneath the spoken line.
non_diegetic_music: A sparse low string drone sustains quietly.
```
