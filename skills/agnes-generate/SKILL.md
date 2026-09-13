---
name: agnes-generate
description: 使用固定参数化脚本执行 Agnes 图片与视频生成，包括参考图编辑、多图参考视频、首尾帧、任务续查和下载。用户要求实际调用 Agnes 生成或恢复已有任务时使用；视频提示词创作可配合 agnes-video-director，通用模型接入说明使用 agnes-ai-models。
---

# Agnes 图片与视频生成

使用本技能固定脚本 scripts/agnes_generate.py。路径、提示词、模型、素材、尺寸、时长、传输选项和输出目录均从 JSON 或 CLI 传入；不要为每个项目复制、改写客户端，不把角色或工程路径写入脚本。只有接口契约变化或修复缺陷时才修改技能代码。

## 工作方式

1. 查看用户实际参考图，编写任务的提示词文件和 JSON 配置。视频参考图按数组顺序绑定 <Picture 1> 等。格式与命令见 [CLI与配置](references/cli.md)。
2. 先执行 plan --config：无需密钥、不联网、不生成，检查模式、素材顺序、尺寸及请求大小。配置中相对路径相对于配置文件，CLI路径相对于当前目录。
3. 提交前核对当前官方能力、价格与本次授权。涉及收费时核对数量、总额并取得授权，既有授权范围内不重复询问。仅安装或调试技能时不创建生成任务，用离线测试或已有任务查询验证。
4. submit --config 提交一次。密钥只从 AGNES_API_KEY 或 api_key_env 指定的环境变量读取。图片和视频使用各自接口，不用聊天视觉代替传图。
5. 视频用 wait --run-dir 续查，完成后 download --run-dir；图片同步返回后也用 download。换会话继续使用原输出目录的 task.json，无需原提示词或参考图。
6. scripts/inspect_media.py 做本地技术检查，然后查看实际结果；解码和抽帧不等于动作流畅、保真通过。报告实际规格及观察到的限制。

## 传图与恢复

- 本地 PNG/JPEG/WebP 自动编码为 Data URI，无需公共图床。图像接口官方支持；视频接口文档只写URL，但2026-09-13的3图和4图任务已实测成功，区分文档保证与实测兼容性。
- 默认保留原图内容（EXIF方向纠正除外）；大图可配置 transport 的 format=jpeg、max_edge=2560、quality=94。按比例缩小、不裁切、不改原图；JPEG将透明区域合成白色，透明素材优先 original/png/webp。
- task.json 是提交锁和恢复记录，存在就拒绝再次提交，不删除它来重试。提交超时或缺少 video_id 标记 submission_unknown，先核对平台任务，不能用 task_id 猜 video_id。找到确切ID后用 attach 建立新恢复目录。
- 仅查询允许有限退避重试。401/403等权限错误停止；等待到上限保留ID，后续继续wait。POST永不自动重试，不自行切换模型、区域或域名。
- task.json 固定保存提交时的base_url，续查不受新会话环境变量漂移影响。API重定向被拒绝，资产下载不携带API密钥。
- 每次新生成使用独立output_dir。下载不覆盖内容不同的文件。文件名通过output_name设置，不改脚本。

## 环境与维护

Python 3.10+；传图/图片检查需要Pillow；视频解码抽帧另需opencv-python。先检查可用运行时，缺依赖再安装。客户端不依赖OpenAI SDK。

[接口契约](references/contracts.md)记录官方来源和实测边界；模型限制保存在references/video-profiles.json。参数通过JSON中的parameters扩展；普通任务不改代码或模型限制文件。新协议不能假装已经支持。

离线回归：python -X utf8 scripts/test_agnes_generate.py。技能安装包不得包含密钥、真实参考图、项目绝对路径或角色专属创意。
