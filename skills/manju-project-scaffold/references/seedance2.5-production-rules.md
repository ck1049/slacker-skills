# Seedance 2.5 Production Rules

Use these rules by default for 即梦 Seedance 2.5 漫剧 production. Keep the 2.0 reference only for explicitly requested legacy work.

## Contents

- Mode selection
- Platform limits and stable ranges
- Canonical prompt structure and mode-specific templates
- Character, multi-person, and multi-panel guidance
- Clip continuity and validation checklist

## Mode Selection

- **全能参考**: generate a standard 4-30s clip from text plus image/video/audio references; audio-only input is supported.
- **首尾帧**: use when the opening and ending composition must be locked.
- **智能编辑 / 高级编辑 / 视频编辑**: change, remove, or add local elements while preserving the rest of an existing video. For precise work, include the marked region and timestamp.
- **视频延长**: extend a source video whose duration is no longer than 30s. Each extension adds 4-30s and affects only the added segment. Repeated extension is allowed while the newest source remains no longer than 30s; the maximum final result is 60s.
- **超长视频**: generate one continuous 30-180s video. Use an explicit timecoded script and reserve this mode for sequences whose continuity benefits from one generation.

## Platform Limits

### Standard output

- Duration: 4-30 seconds (`97-721` frames; `-1` may be available for automatic duration).
- Resolution: 480p or 720p.

### Input images

- Up to 30 images per request.
- Formats: jpeg, png, webp, bmp, tiff, gif, heic, heif.
- Aspect ratio: greater than 0.4 and less than 2.5.
- Width and height: greater than 300px and less than 6000px.
- Each image must be under 30MB; image/audio request body must remain within 64MB. Avoid Base64 for large files.

### Input videos

- Up to 10 videos; combined video duration <= 30s (practical boundary may accept approximately 30.2s).
- Each video: 2-30s; mp4 or mov; 480p-4K; 24-60 FPS; <= 200MB.
- Aspect ratio: 0.4-2.5; width/height: 300-6000px; total pixels: 409600-8295044.

### Input audio

- Up to 10 audio files; combined audio duration <= 30s (practical boundary may accept approximately 30.2s).
- Each audio file: 2-30s; wav or mp3; <= 15MB.
- Audio-only reference input is supported in 2.5.

## Recommended Stable Ranges

Platform maxima are not quality recommendations. Flag likely “抽卡” risk when exceeding these ranges:

- Referenced subjects from video/audio: 1-5 preferred; 6-10 possible with lower stability.
- Subject video/audio duration: 5-10s preferred.
- Subject images: 1-8 preferred; 9-12 possible with lower stability.
- More than 5 subjects: separate multiple views into multiple images; multiple images with one view each are more stable than one composite multi-view image.
- Video editing source: <= 20s preferred.
- Reference images for video editing: 1-5 preferred; 6-8 possible with lower stability.

## Canonical Prompt Structure

Every production prompt should follow:

1. **素材描述**: map upload order to purpose. Example: `@图片1是角色面貌与服装参考；@视频1只参考动作节奏；@音频1只参考音色。`
2. **一句话概述**: subject + location + event + genre/style + special camera language.
3. **具体情节**: write by timestamp or story beat. Each segment should contain visual content + camera + action + dialogue + sound effects + local negative requirements.
4. **全局补充**: repeat continuity anchors, atmosphere, lighting, sound policy, and whole-video negative requirements.

### Standard clip template

```text
【素材描述】
@图片1：角色A的面孔、发型、服装与体型参考。
@图片2：场景布局与色彩参考。
@视频1：只参考动作节奏和镜头运动，不复制其中人物外貌。
@音频1：角色A的音色参考。

【一句话概述】
[主体]在[地点]完成[事件]，[题材/风格]，[特殊运镜]。

【时间轴】
0s-Xs：[画面与构图]；[人物动作/表情]；[景别、机位、运镜]；[台词]；[环境音/音效]；[本段禁止项]。
Xs-Ys：[画面与构图]；[人物动作/表情]；[景别、机位、运镜]；[台词]；[环境音/音效]；[本段禁止项]。

【全局补充】
全程保持[面孔/服装/体型/道具/空间方向]一致；[光影、色彩、氛围与声音要求]；不要字幕，不要Logo，不要无关BGM，不新增无关角色或物体。
```

### Super-long template (30-180s)

```text
【总述】[总时长]秒，[叙事形式与基调]。
【多模态参考层】逐一说明素材用途，并锁定不得改变的角色、场景、音色与动作特征。
【全局视听层】统一画幅、风格、色彩、光线、镜头节奏、对白和声音策略。
【分段时间轴】按连续区间写作；每段明确地点、人物站位、动作因果、镜头衔接、对白、音效和禁止项。
【连续性收束】锁定人物身份、服装、道具状态、轴线、时间、天气与空间关系；禁止跳帧、闪烁、黑屏、硬切、变脸和无关字幕/BGM。
```

### Video extension template

```text
仅生成原视频之后新增的[4-30]秒，不修改原视频内容。
延续原视频的角色面孔、服装、动作惯性、机位、光线、环境声和空间方向。
新增段落：[按时间描述动作、镜头、对白和声音]。
衔接处自然连续，不跳帧、不闪烁、不改变主体身份，不新增字幕、Logo或无关BGM。
```

### Smart/video edit template

```text
在[时间戳]标记区域，将[原元素]修改/移除/替换为[目标元素]。
修改在全片/指定时间段保持一致；除标记对象外，严格保留原视频的构图、人物、动作、镜头、光线、字幕和声音。
```

## Character Realism and Multi-person Consistency

For a realistic character anchor, specify:

`年龄/种族 + 肤色与真实皮肤纹理 + 至少3-4个面部辨识点 + 眼神与底层情绪 + 发型/发色/发丝状态 + 服装剪裁与材质 + 体型/气质 + 构图或动作要求`

For multiple people, assign one reference label and one appearance block per character. State who speaks, where each person stands, and prohibit face swapping or convergence into “twins”.

## Multi-panel Storyboard Input

- Explain what every panel represents before describing the story.
- Identify character/scene reference images separately from the panel grid.
- Fill the gaps between panels with timecoded shot descriptions: composition, shot size, camera movement, action, and transition.
- Simple line art or stick-figure boards are acceptable; prompt detail supplies the final style and rendering.

## Clip Design and Continuity

- Prefer one dramatic action or one emotional turn per standard clip.
- Prefer 8-15s for dense beats and 4-6s for reactions, UI flashes, countdowns, and transitions.
- Use longer 16-30s clips only when temporal continuity is more important than editability.
- Use global character cards for face, clothing, silhouette, voice, and color anchors.
- Reuse scene cards for layouts and screen direction.
- Track altered states such as injured, bloodstained, exhausted, transformed, or powered-up.
- State whether each character is in the default state or an episode-specific state.

## Validation Checklist

- Mode and duration are compatible.
- Material counts, durations, formats, and sizes remain within limits.
- Every `@素材N` label has one explicit purpose; conflicting references are avoided.
- Time ranges are continuous, ordered, and add up to the requested duration.
- Each time segment contains action and camera direction; dialogue and sound are included when relevant.
- Global identity, costume, prop, scene, spatial, lighting, and audio anchors are explicit.
- Negative requirements are precise; use `不要字幕` and `不要无关BGM` when a clean base video is required.
- Requests above the recommended stable ranges are called out as higher-variance before generation.
