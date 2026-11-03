# 接口契约与验证边界

官方核对日期：2026-09-13。执行前核对当前价格和能力，不把免费状态固定在程序里。

- [图片2.1 Flash](https://wiki.agnes-ai.com/en/docs/agnes-image-21-flash)：POST /v1/images/generations。采用请求示例的extra_body.image与extra_body.response_format，后者不放顶层；文生图Base64输出用return_base64。返回data数组内url/b64_json。
- [视频2.5 Flash](https://wiki.agnes-ai.com/en/docs/agnes-video-25-flash)：POST /v1/videos，GET /agnesapi?video_id=...&model_name=...。4—12秒字符串，720P，最多5图、3段音频，无视频参考。
- [视频2.5](https://wiki.agnes-ai.com/en/docs/agnes-video-25)：支持720P/1080P/1K/2K，最多8图、1段视频。图像边长256—5760、小于15MB；视频2—12秒、小于50MB、24—60FPS；音频总长2—12秒、每个小于15MB。脚本校验本地图像及请求体大小，远程音视频另行检查。

模型限制存在video-profiles.json；普通参数从任务配置传入。未知model不做专属范围验证，不能因此宣称官方支持。

2026-09-25核验：上方链接的Flash官方文档现已明确完成结果使用顶层url，状态使用status/progress；internal_status/internal_progress可能仍为pending/0，不用于完成判断。标准版文档仍示例metadata.url，现有下载器兼容两者，无需修改客户端。2026-09-13的两个Flash实测任务也曾返回顶层url。三图PNG Data URI与四图JPEG Data URI均已成功完成视频生成；这是reference.images的实测兼容性，官方视频页仍写URL。图像接口官方明确支持Data URI。

大图请求曾在上传阶段超时，按比例缩小/JPEG传输后成功。通用客户端把这些选项外置，不改原图。提交失败不自动重提，查询中断恢复同一ID。

验证包括离线行为测试，以及已有任务的实时查询、下载、解码；安装验收不新建生成任务。创作质量和保真仍须逐次检查，通用客户端不消除模型质量波动。

## 动态 RPM 政策（2026-10-30 核验）

来源：[官方 Token Plan FAQ](https://wiki.agnes-ai.com/en/docs/tokenplan)，生效日期 2026-10-29。免费/default 与企业认证/enterprise 的图片、视频 RPM 均改为动态调整，以控制台当前额度为准；不再按旧的免费视频 1 RPM、企业视频 2 RPM 或固定图片 RPM 安排批量任务。限时免费价格不代表固定吞吐量。

Token Plan 视频当前 allowed/effective RPM 为 6/5，视频日配额 500 秒、图片日配额 4000 张；RPM 与日配额同时适用。同类型密钥共享额度，增加密钥不能增加额度。提交前核对所用密钥类型的当前限制，遇限流按服务端提示退避；提交结果不确定时仍保留原任务记录，不自动重提。此变更不改变请求或响应协议，客户端无需修改，也不自动切换模型或密钥。

## Agent Plan 计费边界（2026-11-03 核验）

来源：[官方定价](https://wiki.agnes-ai.com/en/docs/pricing)与[订阅计划](https://wiki.agnes-ai.com/en/docs/tokenplan)。试用价与限时免费仅适用于 default 用户的模型试用；Agent Plan 按模型标价折算 Credits，再应用当前套餐折扣，不享受模型限时免费。Token Plan 仅可用于 Flash 模型，既有权益保留，不因新增 Agent Plan 自动迁移。

提交前确认本次使用的计费类型，不能仅看到 Flash 的零试用价就判定免费。Agent Plan 换算基准为 6600 Credits/USD（不是套餐购买单价）；超额参考图费用单独折算且不打折。套餐 Credits 受 5 小时窗口限制，不足时会扣充值 Credits；RPM 独立限制，实际余额、优惠和账单以控制台为准。不自动切换密钥或购买套餐。

费用示例：12 秒 720P Flash 视频标价为 0.30 USD；Agent Plan 按 1980 Credits 乘当前视频折扣计算，不能按 default 试用的 0 元估算。此为预算示例，不代表已授权调用。接口协议不因计费方案改变，固定客户端无需修改。
