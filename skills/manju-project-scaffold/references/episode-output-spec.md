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
- `正片/第一季/XX/制作审阅/素材清单.json`
- `正片/第一季/XX/制作审阅/本集制作总览.html`

The stable HTML entrypoint shows the current script, images, audio references/dialogue, video clips, SFX, music and final cuts when present. Follow [审阅页规范](episode-review-page.md); update the manifest and regenerate the same page after material or production-state changes, not only at delivery. Selection changes affect the overview, not historical evidence or the project's formal acceptance index.

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

## 正片登记与发布副本

用户明确满意并要求登记某个具体版本为正片时，默认同时保留**存档母版＋发布副本**。审阅候选、局部认可或生成成功不触发正式登记；另存副本也不构成上传发布授权。

- **存档母版**：固定用户认可的实际文件与 SHA-256，保留原始生成素材、工作流、提示词、任务回执、采用区间及来源记录；这些资料可作为独立侧车文件归档，不要求全部嵌入母版。不得覆盖认可源。
- **发布副本**：从认可版本本地另存，保持画面、声音、字幕、时长、同步及“AI生成”等必要可见标识。仅为整理元数据时优先不重新编码音视频，不重新生成画面；确需转码时记录原因和参数，另核对实际画质、声音及同步。
- **字段检查后再处理**：先检查文件级、音视频轨道级标签和工具可识别的来源/标识信息。非必要工程信息（例如工作流 JSON、提示词、内部文件路径和普通制作备注）经确认不承载规定标识或必要溯源信息后才移除。模型或服务商名称若属于规定的隐式标识，不作为普通工程备注删除；无法分类的字段先保留并记录待核。不得把一键清空全部元数据当成默认流程。
- **保留真实 AI 身份**：保留既有且适用的显式/隐式 AI 标识、数字水印和必要来源信息，不伪造 Seedance 或其他模型来源，不以绕过平台识别为交付目标；发布时仍使用平台的 AI 内容声明功能。涉及具体标识规范时查当前官方要求，不能仅凭“画面上有水印”就推定其他标识可删。
- **验证并留痕**：分别记录母版与发布副本路径、SHA-256、派生关系、实际清理字段及保留字段。重新读取发布文件验证预期字段；不转码时核对音视频码流，必要时核对解码帧/音频，检查时长、帧数、轨道与同步，确认字幕和可见标识未丢失。文件封装哈希不同本身不代表画面变化；技术一致性也不补写此前未完成的连续视听验收。
- **同步交付入口**：更新正片登记、素材清单、当前文件指针和稳定审阅 HTML，清楚区分“存档母版”与“发布副本”，两份均可追溯到同一认可版本。
- **准确表述效果**：只报告已检查范围内哪些工程字段已移除，不把常规标签未检出扩大为全部隐式信息已清空，不承诺“平台检测不出”“无法识别模型”或“保证不限流”。对 ComfyUI、非 Seedance 等工具/模型导致限流的传言，须另查可靠证据，不写成确定的平台规则。

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
