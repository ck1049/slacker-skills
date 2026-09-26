# 接口契约与验证边界

官方核对日期：2026-09-13。执行前核对当前价格和能力，不把免费状态固定在程序里。

- [图片2.1 Flash](https://wiki.agnes-ai.com/en/docs/agnes-image-21-flash)：POST /v1/images/generations。采用请求示例的extra_body.image与extra_body.response_format，后者不放顶层；文生图Base64输出用return_base64。返回data数组内url/b64_json。
- [视频2.5 Flash](https://wiki.agnes-ai.com/en/docs/agnes-video-25-flash)：POST /v1/videos，GET /agnesapi?video_id=...&model_name=...。4—12秒字符串，720P，最多5图、3段音频，无视频参考。
- [视频2.5](https://wiki.agnes-ai.com/en/docs/agnes-video-25)：支持720P/1080P/1K/2K，最多8图、1段视频。图像边长256—5760、小于15MB；视频2—12秒、小于50MB、24—60FPS；音频总长2—12秒、每个小于15MB。脚本校验本地图像及请求体大小，远程音视频另行检查。

模型限制存在video-profiles.json；普通参数从任务配置传入。未知model不做专属范围验证，不能因此宣称官方支持。

2026-09-25核验：上方链接的Flash官方文档现已明确完成结果使用顶层url，状态使用status/progress；internal_status/internal_progress可能仍为pending/0，不用于完成判断。标准版文档仍示例metadata.url，现有下载器兼容两者，无需修改客户端。2026-09-13的两个Flash实测任务也曾返回顶层url。三图PNG Data URI与四图JPEG Data URI均已成功完成视频生成；这是reference.images的实测兼容性，官方视频页仍写URL。图像接口官方明确支持Data URI。

大图请求曾在上传阶段超时，按比例缩小/JPEG传输后成功。通用客户端把这些选项外置，不改原图。提交失败不自动重提，查询中断恢复同一ID。

验证包括离线行为测试，以及已有任务的实时查询、下载、解码；安装验收不新建生成任务。创作质量和保真仍须逐次检查，通用客户端不消除模型质量波动。
