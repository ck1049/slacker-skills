# slacker-skills

个人维护的 Agent Skills 合集，覆盖数据安全、账单分析、AI 漫剧生产和 Tripo 3D 资产工作流。

每个技能位于 `skills/<skill-name>/`，以 `SKILL.md` 作为入口，并可附带脚本、参考规范和 Agent 配置。仓库可通过 `skills` CLI 安装到支持 Agent Skills 的工具中。

> [!IMPORTANT]
> 本仓库中的技能均由作者个人整理和维护，与任何厂商或社区的官方技能集合无隶属、合作或背书关系。使用前请自行评估适用性、数据安全、平台规则和费用风险。

## 安装

需要预先安装 Node.js，然后任选一种地址执行：

```bash
npx skills add https://github.com/ck1049/slacker-skills.git
```

或使用 SSH：

```bash
npx skills add git@github.com:ck1049/slacker-skills.git
```

安装过程中按 CLI 提示选择目标 Agent 和技能。完成后，请根据 Cursor、Codex 等宿主工具的说明确认技能目录已加入其可发现路径。

## 技能一览

| 技能 ID | 用途 | 主要依赖或限制 |
| --- | --- | --- |
| [`slacker-data-security`](skills/slacker-data-security/SKILL.md) | 分层数据安全方案：业务 RSA/AES、通信 RSA、OAEP 分段、AES-GCM、口令慢哈希及密钥轮换 | 语言无关；Java 示例仅供 JVM 技术栈参考 |
| [`alipay-mihoyo-analysis`](skills/alipay-mihoyo-analysis/SKILL.md) | 从支付宝账单 PDF 提取米哈游交易，区分《原神》和《崩坏：星穹铁道》，生成 Excel 报告 | Python、`pdfplumber`、`openpyxl`；仅支持未加密的文本型 PDF |
| [`jimeng-agent-workflow`](skills/jimeng-agent-workflow/SKILL.md) | 驱动即梦 Agent 完成漫剧需求、质量评估、角色/场景图、视频生成和进度监控 | `agent-browser` v0.23+、即梦账号，并配合漫剧脚手架 |
| [`manju-project-scaffold`](skills/manju-project-scaffold/SKILL.md) | 创建和维护长篇漫剧工程，组织季度、剧集、全局素材及 Seedance 2.0/2.5 规范 | Python 3；自带目录脚手架脚本 |
| [`tripo-3d-pipeline`](skills/tripo-3d-pipeline/SKILL.md) | 规划并执行 Tripo 3D 生成、纹理、拓扑、分割、绑定、动画、转换和归档 | Tripo CLI；付费任务必须先核价并获得明确批准 |

## 快速使用

安装后可以直接用自然语言描述任务，也可以明确指定技能 ID：

```text
使用 slacker-data-security 评审这个服务的敏感字段加密方案。
使用 alipay-mihoyo-analysis 分析这个目录中的支付宝账单 PDF，并生成 Excel 报告。
使用 manju-project-scaffold 为《项目名》创建第一季漫剧工程。
使用 tripo-3d-pipeline 评估把这张角色图做成 Unity 可用 GLB 的成本，先不要消耗积分。
```

## 随附脚本

### 支付宝米哈游账单分析

```bash
pip install pdfplumber openpyxl
python skills/alipay-mihoyo-analysis/scripts/alipay_mihoyo_analysis.py "<支付宝 PDF 所在目录>"
```

脚本扫描目录内所有 `.pdf`，并生成 `米哈游账单分析报告.xlsx`，包含年度汇总、月卡统计、游戏分类明细、全部交易明细和总结五个工作表。

### 漫剧工程脚手架

```bash
# 创建新工程
python skills/manju-project-scaffold/scripts/scaffold_manju.py project "<项目名>"

# 添加新一季
python skills/manju-project-scaffold/scripts/scaffold_manju.py season "第二季" --under "<项目目录>/正片"

# 添加剧集
python skills/manju-project-scaffold/scripts/scaffold_manju.py episodes 02 03 --season "<项目目录>/正片/第一季"
```

## 仓库结构

```text
skills/
├─ <skill-name>/
│  ├─ SKILL.md       # 技能入口、触发条件和执行流程
│  ├─ scripts/       # 可选：辅助脚本
│  ├─ references/    # 可选：详细规范与参考资料
│  └─ agents/        # 可选：宿主 Agent 展示配置
└─ ...
```

## 安全与费用说明

- 账单 PDF 可能包含姓名、账号和交易号，请只在可信环境处理，不要提交到公开 Issue。
- 数据安全技能提供架构规范和示例，不能替代针对具体实现的安全审计。
- 即梦、Seedance、Tripo 的能力、价格、积分规则和页面结构可能变化，应以当前官方信息为准。
- Tripo 技能将费用确认作为强制门禁：先查询余额和价格、列出预计消耗，得到明确批准后才提交付费任务。

## 贡献与反馈

技能内容以各目录中的 `SKILL.md` 和随附文件为准。如发现描述过时、示例错误或兼容性问题，欢迎提交 [Issue](https://github.com/ck1049/slacker-skills/issues) 或 Pull Request。

仓库地址：[github.com/ck1049/slacker-skills](https://github.com/ck1049/slacker-skills)
