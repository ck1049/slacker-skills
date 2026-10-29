# 本机配置与迁移

技能可安装在任意目录。音频库、输出项目、Python 和 FFmpeg 均为独立资源，不要求某个工程布局。Python 3.11+ 仅用标准库；本次在 Windows 验证，其他系统需实际验证后再宣称适配。

## 配置优先级

- 配置文件选择：`--config <文件>` → `MANJU_SFX_CONFIG` → `~/.config/manju-sfx-library/config.json`。
- 音效库：`--library` → `MANJU_SFX_LIBRARY` → 配置文件的 `library`；缺失会报错。
- FFmpeg：`--ffmpeg` → `MANJU_SFX_FFMPEG` → 配置文件的 `ffmpeg` → PATH 中的 `ffmpeg`。
- 配置内相对路径以配置文件目录为基准；CLI 和环境变量中的相对路径以当前工作目录为基准。
- 显式配置文件不存在或格式错误时直接报错，不能悄悄回退到另一套路径。

本机配置示例，具体路径由使用者填写；不得将真实个人路径提交进通用技能仓库：

```json
{
  "schema_version": 1,
  "library": "./sound-library",
  "ffmpeg": "ffmpeg"
}
```

从技能目录执行（配置参数放在子命令之前；render 也接受其后的 `--ffmpeg`）：

```text
python -X utf8 scripts/sfx.py --config /path/to/config.local.json doctor
python -X utf8 scripts/sfx.py --config /path/to/config.local.json search "脚步 木"
python -X utf8 scripts/sfx.py --config /path/to/config.local.json verify
python -X utf8 scripts/sfx.py --config /path/to/config.local.json export <素材ID> --out /project/sfx/step_v001.wav
python -X utf8 scripts/sfx.py --config /path/to/config.local.json render /project/sfx/plan_v001.json --out /project/sfx/stem_v001.wav
```

`doctor` 读取目录和 FFmpeg 版本，不下载、不加载模型，也不代替全库 `verify`。

新库的显式创建与入库：

```text
python -X utf8 scripts/sfx.py --library /path/to/new-library init
python -X utf8 scripts/import_assets.py --library /path/to/new-library /path/to/import-manifest.json
python -X utf8 scripts/build_catalog.py --library /path/to/new-library --ffmpeg /path/to/ffmpeg
```

`init` 不覆盖现有清单；导入脚本只读本地文件。Kenney 四个初始包的获取器 `fetch_kenney.py` 为可选适配器，仅在用户已授权下载该包时运行。它不在 init、doctor、搜索或渲染中自动调用。

## 迁移与维护

- 升级技能不移动素材库；迁移库时复制目录内原文件、剪辑副本、来源与许可、catalog.json，并修改本机配置。清单路径均相对库根，旧 root 信息不参与运行。
- 保留旧素材 ID 和 SHA，已有时间轴可继续使用。换源、改许可或重新加工时另建素材版本。
- 本机路径、音频、原包、项目回执不放入技能仓库。原始音频与许可证据需要独立备份。
- 源仓库、工作区安装副本和用户安装副本按实际安装位置同步代码；比对文件 SHA，不能把旧安装副本反向覆盖新源。
- 迁移验收：在新临时目录导入独立测试音频，验证搜索、导出和渲染；测试不能依赖某个现成音效 ID。

离线测试：`python -X utf8 tests/test_sfx.py --ffmpeg /path/to/ffmpeg`。测试音频在临时目录合成，不联网，不下载真实素材，不把合成夹具视为通过听审的生产音效。
