# CLI 与配置

以下CLIENT替换为本技能scripts/agnes_generate.py的绝对路径。只保留一份固定脚本；JSON、提示词和输出放各自项目。

```powershell
python -X utf8 CLIENT plan --config "任务.json"
python -X utf8 CLIENT submit --config "任务.json"
python -X utf8 CLIENT wait --run-dir "输出目录"
python -X utf8 CLIENT download --run-dir "输出目录"
```

图片无需wait。submit不隐式等待或下载。wait默认最多600秒、每30秒查询；可改--max-wait、--poll-interval、--timeout。下载失败后继续download，不重新生成。

## 视频四图参考

```json
{
  "kind": "video",
  "model": "agnes-video-2.5-flash",
  "prompt_file": "提示词.txt",
  "images": ["素材/角色.png", "素材/对手.png", "素材/场景.png", "素材/宝剑.png"],
  "parameters": {"mode":"reference", "seconds":"12", "size":"720P", "aspect_ratio":"16:9", "n":1},
  "transport": {"format":"jpeg", "max_edge":2560, "quality":94},
  "output_dir": "输出/第01次",
  "output_name": "战斗视频",
  "timeout": 180, "poll_interval": 30, "max_wait": 600
}
```

图片输入可以是本地路径、HTTPS URL或PNG/JPEG/WebP Data URI；顺序就是Picture序号。transport只处理本地/内嵌图片；不下载重编码HTTPS素材。省略transport保留原图，max_edge=0不缩小。

文生视频：mode=text，不填素材。首尾帧：mode=keyframe，顶层first_frame/last_frame至少一个，不填images/audios/videos。

音频：顶层audios为HTTPS URL数组，不支持本地音频直传。标准版视频参考：顶层videos填对象数组，例如[{"url":"https://...","start_seconds":0,"require_audio":false}]。调用前另行核对时长、大小、FPS。Flash不支持视频参考，不把本地媒体自动上传公共图床。

## 图片生成与编辑

```json
{
  "kind":"image", "model":"agnes-image-2.1-flash",
  "prompt_file":"图片提示词.txt", "images":["素材/参考.png"],
  "parameters":{"size":"2K", "ratio":"16:9"},
  "response_format":"url",
  "output_dir":"输出/图片01", "output_name":"宝剑参考", "timeout":360
}
```

文生图省略images。response_format支持url/b64_json。客户端构造extra_body.image和extra_body.response_format；文生图Base64另设置return_base64=true。输出按实际格式命名png/jpg/webp，多张自动加序号。

## 外部参数

- --config可省略，直接给--kind、--model、--prompt-file、--output-dir等。
- --prompt与--prompt-file二选一，覆盖配置中的提示词来源。
- --image可重复，整体替换配置images并保持顺序；--first-frame和--last-frame覆盖对应字段。
- --seconds、--size、--aspect-ratio、--mode、--seed覆盖parameters；图片的aspect-ratio转为ratio。
- --parameters-json读取JSON对象合并到parameters，普通CLI参数优先。可选模型参数通过该对象传入，不修改脚本；model/prompt/素材/凭据有独立字段。
- --image-format original|png|jpeg|webp、--max-edge、--jpeg-quality覆盖传输配置；quality对JPEG/WebP生效。
- --base-url或配置base_url优先，其次AGNES_BASE_URL，默认国际主入口。入口必须匹配用户选择的服务，不自动跨域。
- --api-key-env指定环境变量名，绝不在JSON/CLI放密钥值。
- --output-name是无目录无扩展名的基础文件名。新的生成使用新的output_dir。

配置文件内相对路径相对于配置文件；CLI路径相对于当前工作目录。支持UTF-8和UTF-8 BOM。Windows提示词优先用文件，不拼接未经转义的Shell文本。

```powershell
python -X utf8 CLIENT plan --config "任务.json" --seconds 8 --prompt-file "新版.txt" --output-dir "输出/第02次"
```

## 跨会话和旧任务恢复

```powershell
python -X utf8 CLIENT status --run-dir "原输出目录"
python -X utf8 CLIENT wait --run-dir "原输出目录" --max-wait 600
```

旧任务有确切video_id但没有通用task.json：

```powershell
python -X utf8 CLIENT attach --run-dir "恢复目录" --video-id "已确认ID" --model "agnes-video-2.5-flash" --output-name "恢复视频"
python -X utf8 CLIENT status --run-dir "恢复目录"
python -X utf8 CLIENT download --run-dir "恢复目录"
```

attach只写恢复记录，不联网不生成。submission_unknown先核对平台记录，不能猜ID或删除提交锁。

## 记录与检查

plan.json是离线预检；task.json存提交锁、模型、入口、ID和状态；preflight.json存提交摘要与图像哈希；prompt.txt是实际提示词快照；response.json是创建响应；result.json是最后一次成功查询；downloads.json存文件路径、大小和SHA256。

请求摘要不含图像Base64，密钥不入文件。图片response.json可能含服务返回的b64_json用于恢复下载，不打印到终端。返回URL与媒体按本地项目素材管理。

```powershell
python -X utf8 INSPECT --input "视频.mp4" --kind video --output-dir "验收" --sample-interval 0.5
python -X utf8 INSPECT --input "图片.png" --kind image --output-dir "图片验收"
```

INSPECT替换为scripts/inspect_media.py。视频全帧解码并生成抽帧表；不自动评价动作、不确认声轨，不代替看视频听音。检查目录按任务独立。

退出码：0操作成功（status可能仍在排队）；2输入/网络/本地错误；3视频failed/cancelled；4等待到上限。网络中断不意味着生成失败。
