# 官方约束与接入

核验日期：2026-09-12。以下是接口事实摘要，不是完整文档镜像。官方网页后续变更时以实时页面为准。

## Flash 快照

来源：[Agnes Video 2.5 Flash 官方文档](https://wiki.agnes-ai.com/en/docs/agnes-video-25-flash)。

- 模型 `agnes-video-2.5-flash`；`seconds` 为字符串，4—12 秒，默认 5；`size` 仅 `720P`，`n` 仅 1。
- 支持 `text`、`keyframe`、`reference`；参考图片最多 5 张，音频最多 3 段，不接受非空视频参考。
- 画幅可选 21:9、16:9、4:3、1:1、3:4、9:16；实际输出尺寸须检查文件。
- 核验时官方显示限时免费，不代表永久免费或第三方站点免费。

## 公共接入要点

来源：[Agnes Video 2.5 官方文档](https://wiki.agnes-ai.com/en/docs/agnes-video-25)。

- `POST https://apihub.agnes-ai.com/v1/videos` 创建任务；保存 `video_id`。查询使用根路径 `/agnesapi`，携带 `video_id` 和对应的 `model_name`。
- `text` 不带素材；`keyframe` 使用 `first_frame` / `last_frame`，至少一个；`reference` 使用 `images` / `audios` 等数组，不混入首尾帧字段。标准版的 `videos` 不能直接照搬给 Flash。
- 素材必须能被服务端访问。提示词里的 `<Picture N>`、`<Audio N>` 按各数组从 1 独立编号。本地路径不等于可访问 URL；仅给提示词不需要公开上传。
- 完成以 `status=completed` 为准。2026-09-25 核验 Flash 官方文档已明确从顶层 `url` 获取成片；标准版文档仍示例 `metadata.url`。Flash 的 `internal_status` / `internal_progress` 可能仍为 pending / 0，应使用 `status` / `progress`，不能因此重复提交。详细尺寸、媒体大小、请求示例和标准版费用使用原文，不在此维护第二套完整表格。

## 本地工作流建议

这些是可靠性设计建议，不是官方接口新增功能：

1. 提交前核对实际模式、素材可访问性、时间范围和费用。HTTP JSON 使用文档字段；SDK 的扩展参数容器不等于 HTTP JSON 应额外嵌套一层。
2. 遇到网站自定义字段，核对其转换逻辑，不能把社区封装参数当官方字段。只发送有文档支持的字段。
3. 保存创建响应与脱敏请求摘要。POST 超时可能已创建任务，不自动重复提交；先检查是否已有任务记录。不要猜测 `task_id` 可以代替 `video_id`。
4. 查询遇到 429/临时网络错误时遵循 Retry-After 或退避；建议单任务最多等待 10 分钟，超时保存 ID，后续继续查询，不另建重复任务。这个等待上限是本技能建议，可按任务调整。
5. 400 检查字段；401/403 检查权限；404 先核对 ID 与查询路径；failed 留存原因。不要盲目换域名、遍历凭据或无限重试。
6. 密钥仅从用户授权的凭据机制读取，不输出或写入提示词、样例及报告。报告状态必须区分“参数检查通过”“已提交”“已完成”“已看过成片”。
