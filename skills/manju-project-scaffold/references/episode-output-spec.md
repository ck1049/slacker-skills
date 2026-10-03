# Episode Output Spec

Create these files for chapter `XXXX` / episode `XX`.

## Source

`大纲/原文/第XXXX章_原文.txt`

Store the original novel text unchanged except for encoding normalization to UTF-8.

## Global Materials

Use one Markdown file or folder per reusable subject.

- `全局角色/<角色名>/角色卡.md`
- `全局场景/<场景名>/场景卡.md`
- `全局道具/<道具名>/道具卡.md`
- `全局音频/<音频类型>/<名称>.md`

Each card should include:

- 基础描述
- 视觉锚点
- 性格/功能/叙事作用
- 首次出现章节
- 后续一致性要求
- AI参考图提示词

## Episode Files

Create or update:

- `正片/第一季/XX/剧本/第XX集_剧情改编.md`
- `正片/第一季/XX/分镜/分镜脚本/第XX集_seedance2.5分镜脚本.md`
- `正片/第一季/XX/分镜/分镜图/第XX集_分镜图提示词.md`
- `正片/第一季/XX/角色/第XX集_角色资料.md`
- `正片/第一季/XX/场景/第XX集_场景资料.md`
- `正片/第一季/XX/道具/第XX集_道具资料.md`
- `正片/第一季/XX/音频/第XX集_音频设计.md`

## Adapted Script Format

Include:

- 基本信息: episode number, chapter source, target duration, style.
- 本集梗概: 120-250 Chinese characters.
- 情绪曲线: list the emotional beats in order.
- 场景剧本: scene heading, characters, visual action, dialogue/voiceover.
- 戏剧取舍: what was compressed, removed, or externalized visually.

## Storyboard Script Format

For each clip:

- Clip ID
- Execution channel and capability evidence: webpage / Canvas CLI / other explicitly selected channel; for CLI, record version, model-query date, canonical model, supported mode and relevant returned parameters
- Mode: 全能参考 / 智能编辑 / 超长视频 / 首尾帧 / 视频延长 / 视频无缝转场
- Duration: standard 4-30s; super-long mode 30-180s; extension increment 4-30s
- Source story beat
- Material map: identify every `@图片N` / `@视频N` / `@音频N` and its exact purpose
- One-line overview: subject + location + event + genre/style + special camera language
- Timecoded visual prompt: direct Seedance-ready segments containing image, action, camera, dialogue, SFX, emotional/directorial subtext, and local negative requirements; repeat the relevant `@素材N` inside a segment when stronger adherence is needed
- Global constraints: continuity anchors and whole-video negative requirements
- Camera: shot size, angle, movement
- Character performance: expression, gesture, body action
- Lighting and color
- Sound: music, SFX, voiceover/dialogue
- References: up to 30 images; up to 10 videos totaling <= 30s; up to 10 audio files totaling <= 30s
- Reference stability note: mark when the prompt exceeds the recommended stable ranges
- Seamless-transition note: when this mode is used, map source video A and source video B separately, state the transition trigger, and require both source clips to remain unchanged
- Storyboard image needed: yes/no and why

## Storyboard Image Prompt Format

For key clips, provide:

- Image ID
- Used by Clip IDs
- Composition
- Character appearance and pose
- Scene design
- Lighting/color
- Negative prompt
- Consistency notes

## Production Checklist

Before finishing, verify:

- Every standard clip duration is 4-30s; every super-long clip is 30-180s.
- The chosen execution channel supports each planned mode and duration. For Canvas CLI, verify live model/mode parameters; do not label multimodal video reference as extension or promise webpage-only modes without explicit capability evidence. Mark unverified/unavailable execution separately from a completed creative script.
- Video extension is used only from a source video no longer than 30s; each extension is 4-30s and the resulting video is no longer than 60s.
- Image references are <= 30; video references are <= 10 and total <= 30s; audio references are <= 10 and total <= 30s.
- Each prompt follows: material map + one-line overview + timecoded/storyline detail + global constraints.
- Every referenced material has a unique label and explicit purpose.
- Repeated `@素材N` references keep the same declared purpose and appear only in segments where they strengthen identity, composition, voice, or movement adherence.
- Each time segment states both the physical instruction and its intended emotion, dramatic meaning, or camera-directing subtext.
- Negative requirements such as no subtitles/no unrelated BGM are stated locally or globally when needed.
- New recurring characters/scenes/props are placed in global folders.
- Episode-local folders contain only one-off or episode-specific variants.
- The adapted script preserves the original chapter's turning points.
