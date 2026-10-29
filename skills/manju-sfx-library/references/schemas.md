# 素材与时间轴规范 v1

## 本地入库 manifest

```json
{
  "schema_version": 1,
  "batch_id": "recording-door-001",
  "source_kind": "self_recorded",
  "author": "实际录音者或权利拥有者",
  "source_url": "urn:self-recorded:recording-door-001",
  "license": "LicenseRef-Self-Owned",
  "license_url": "urn:license:self-owned",
  "license_verified": true,
  "rights_confirmed": true,
  "verified_by": "实际核对人",
  "verified_at": "实际核对日期时间",
  "evidence_files": ["rights.txt"],
  "assets": [{
    "file": "door.wav",
    "name": "木门轻关",
    "category": "门与机关",
    "tags": ["关门", "木门", "近距离"],
    "recording_metadata": {
      "recorded_by": "实际录音者",
      "recorded_at": "实际录音时间",
      "rights_note": "实际权利依据与使用范围；核对有无第三方声音",
      "device": "可选设备信息",
      "location": "可选非敏感场景描述"
    }
  }]
}
```

示例不是预先给予的授权；必须换成真实声明和证据，未核对前不能把 verified 填成 true。

下载素材改为 `source_kind=downloaded`、`license=CC0-1.0`，source_url 填实际来源，license_url 填 CC0 官方许可地址，保存许可正文和来源快照；`recording_metadata` 可省略。参数合成可使用 `procedural`，但只有输出确有 CC0 依据时才通过当前准入工具，不能仅因生成器开源就声称输出为 CC0。

路径相对 manifest 所在目录；版权证据须为 UTF-8 文本，可包含 HTML 源码。batch_id 为 3—64 位小写字母/数字/连字符，必须唯一。当前一次 1—200 条，单音频 ≤100 MiB、总音频 ≤500 MiB，用于限制意外导入；不代表音质上限。

## catalog.json

顶层 `schema_version=1`、`count`、`assets`。条目由工具生成：

- 身份与检索：id、name、category、tags、tag_basis、source_kind、可选 recording_metadata。
- 来源与权利：author、pack、source_url、license、license_url、commercial_use、attribution_required、license_verified、license_files、source_receipt。
- 文件与验证：source_path、source_sha256、path、sha256、duration_seconds、sample_rate、channels、encoding、peak_dbfs、conversion。
- 状态：technical_status、listening_status、fit_status，可选 review_records。

库内路径全部相对库根。ID 绑定入库路径，不因库整体移动而变化。旧 Kenney 素材保留原 KEN- ID；通用导入使用 SFX- ID。已存在剪辑副本 SHA 改变时拒绝重建；音频修订应使用新 batch_id。

来源回执保存逐文件路径与 SHA；许可正文和原音频都须绑定在回执内。导出时再次比对。许可核对与作者声明仍需人工负责，哈希只能证明证据一致。

## 时间轴方案

```json
{
  "schema_version": 1,
  "duration_seconds": 8,
  "events": [{
    "asset_id": "从 search 结果取得实际 ID",
    "at_seconds": 1.2,
    "trim_start_seconds": 0,
    "gain_db": -12,
    "fade_in_seconds": 0,
    "fade_out_seconds": 0.02,
    "note": "按实际剪辑定位的第一步"
  }]
}
```

事件支持可选 duration_seconds，省略则保留裁切起点之后的完整声音；超出总片长会报错。各时间单位为秒，定位精度为 48 kHz 样本。允许事件重叠，脚步通过多条事件轮换变体，不自动推断或循环。

gain_db 默认 -12、范围 -96 到 +12，需按真实音量调整；淡化默认 0，保护瞬态。淡入淡出不能交叠。未知字段拒绝执行。总轨最长 4 小时、最多 200 个事件；更长作品按场景分轨。

输出为 PCM16 48 kHz 双声道 WAV 和同名 request.json、receipt.json，不覆盖已有文件。回执含来源许可正文、原音与剪辑 SHA、时间轴、FFmpeg 参数、输出 SHA、技术与听审状态。限制器为约 -1 dBFS 样本峰值且不自动放大，不等于真峰值母带处理或成片听审通过。
