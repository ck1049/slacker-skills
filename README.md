# slacker-skills

个人维护的 Agent Skills 合集，覆盖软件架构初期设计、分语言与领域代码质量、数据安全、账单分析、原创网文小说、AI 漫剧生产、MiniMax H3、Agnes 图片与视频生成及导演、Tripo 3D 资产工作流。

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
| [`web-novel-writer`](skills/web-novel-writer/SKILL.md) | 多题材原创网文：先冻结世界观、人物与因果大纲，再写多线章节，维护连续性/伏笔并逐章审改 | 无必装运行依赖；参考只提炼技法，不复制剧情；编辑验收不保证商业成绩 |
| [`video-drama-director`](skills/video-drama-director/SKILL.md) | 跨模型编排剧情、表演及武侠/仙侠/现代动作，按角色与器械设计招式、特效展开、声音和摄影，并检查状态连续性 | Python 3.10+ 可选计划检查器；配合所选模型导演技能，生成与收费沿用用户授权 |
| [`minimax-h3-director`](skills/minimax-h3-director/SKILL.md) | 将创意、剧本和多模态参考转成 MiniMax H3 的 T2VA、I2VA、FL2VA、L2VA 或 Ref2VA 分镜与官方格式提示词 | 自包含官方格式指南；真实成片仍需 MiniMax H3 服务或应用 |
| [agnes-video-director](skills/agnes-video-director/SKILL.md) | 为 Agnes Video 2.5 Flash / 2.5 编写中文视频提示词，处理角色参考、首尾帧、镜头节奏与成片检查 | 官方约束摘要与参考示例；真实生成需 Agnes 服务，收费操作需授权 |
| [agnes-generate](skills/agnes-generate/SKILL.md) | 通过固定脚本与外部 JSON/CLI 参数执行 Agnes 图片和视频生成、多图参考、首尾帧、任务续查及下载 | Python 3.10+、Pillow；视频检查另需 opencv-python；密钥从环境变量读取 |
| [agnes-ai-models](skills/agnes-ai-models/SKILL.md) | Agnes API 认证、区域路由、SDK 集成与 Agent 接入排障 | 接入层；视频提示词由 agnes-video-director 负责，实际任务由 agnes-generate 执行 |
| [`tripo-3d-pipeline`](skills/tripo-3d-pipeline/SKILL.md) | 规划并执行 Tripo 3D 生成、纹理、拓扑、分割、绑定、动画、转换和归档 | Tripo CLI；付费任务必须先核价并获得明确批准 |
| [`software-architecture-design`](skills/software-architecture-design/SKILL.md) | 主动分轮澄清软件项目需求，形成技术选型、架构、验收与发布方案，并提示可复用规范更新 | 技术栈中立；默认仅设计，实施、收费与发布沿用明确授权 |

## 快速使用

### 官方即梦画布 CLI

`dreamina-canvas-cli` 由即梦官方安装器维护，不作为本仓库的自维护技能内置。按[官方安装页](https://jimeng.jianying.com/ai-tool/install)和[官方指南](https://bytedance.larkoffice.com/wiki/QO66wGahSiakEHkJbxIcNBtDnAc)安装到实际执行环境；WSL 内的安装不等于 Windows Codex 已能发现技能，需另外确认宿主技能目录。

使用 Canvas CLI 时先查询当前模型/模式能力；网页端 Seedance 的超长、延长、编辑等功能不自动成为 CLI 能力。保留用户选择的生成平台，普通提示词请求不自动提交生成。官方升级后也应复核宿主的本地触发边界适配。

### 通用代码质量技能

以下技能可分别安装和使用，没有相互强制依赖，也不要求某个项目布局、操作系统、作者身份或框架。每次使用先识别宿主项目规则、版本和工具，再应用对应领域的检查；已有明确约定优先，缺失工具与未验环境会如实报告。安装 Skill 不会自动配置 formatter、Git 钩子或远端 CI，也不能保证未经验证即适配所有项目。

| 技能 ID | 适用范围 | 关键内容 |
| --- | --- | --- |
| [java-code-quality](skills/java-code-quality/SKILL.md) | Java 库、服务、工具 | 注解位置区别、可读格式、职责、明确类型与资源管理 |
| [typescript-code-quality](skills/typescript-code-quality/SKILL.md) | 浏览器、服务端、工具 TypeScript | 类型与运行时验证、异步控制流、模块边界 |
| [frontend-interaction-quality](skills/frontend-interaction-quality/SKILL.md) | Web 前端交互 | 草稿、导航、身份隔离、在途状态、可访问性和视口验收 |
| [backend-api-quality](skills/backend-api-quality/SKILL.md) | 后端服务接口 | 契约、集中错误映射、事务、权限、幂等与未知结果 |
| [database-change-quality](skills/database-change-quality/SKILL.md) | 关系数据库 | 注释就近、真实方言验证、迁移与数据恢复 |
| [python-maintenance-quality](skills/python-maintenance-quality/SKILL.md) | Python 工具与维护脚本 | 类型边界、子进程、路径、失败处理和恢复 |
| [game-code-quality](skills/game-code-quality/SKILL.md) | 游戏运行时 | 生命周期、场景切换、资源引用、存档与实测性能 |
| [code-review-feedback](skills/code-review-feedback/SKILL.md) | 跨语言变更审查 | 证据分级、范围内修复、复测复查和实际版本对应 |

同一任务按需组合语言和领域技能，例如 Java + 后端接口 + 数据库；不要对每次修改都加载全部技能。游戏技能按实际引擎核对资料，不把 Web 项目经验直接当成游戏引擎运行证据。需要项目初期设计时使用已有的 `software-architecture-design`；本组技能负责实现与审查，不替代需求决策。

```text
使用 java-code-quality 添加这个方法，保持现有 Gradle、JPA 与格式配置，不重排旧代码。
使用 frontend-interaction-quality 修复切页后上传状态提前清零，保留当前 Vue 和 Biome 配置。
使用 code-review-feedback 审查暂存变更，只报告有证据的问题，暂不修改代码。
```

### 其他工作流

安装后可以直接用自然语言描述任务，也可以明确指定技能 ID：

```text
使用 slacker-data-security 评审这个服务的敏感字段加密方案。
使用 alipay-mihoyo-analysis 分析这个目录中的支付宝账单 PDF，并生成 Excel 报告。
使用 manju-project-scaffold 为《项目名》创建第一季漫剧工程。
使用 web-novel-writer 为 16—35 岁男性读者创作第一部原创网文，题材和书名自主，先完成规划与冻结，再写开篇并逐章评审。
使用 video-drama-director 把这部长篇剧情设计成有多人互动、情绪变化和状态连续性的镜头组，再按所选模型编写提示词。
使用 minimax-h3-director 把这段 15 秒动漫剧情整理成可直接提交给 MiniMax H3 的 T2VA 提示词。
使用 agnes-generate 根据任务 JSON 和参考图生成图片或视频，复用固定脚本并保存任务记录。
使用 tripo-3d-pipeline 评估把这张角色图做成 Unity 可用 GLB 的成本，先不要消耗积分。
```

## 随附工作流与脚本

### 原创网文小说写作

[`web-novel-writer`](skills/web-novel-writer/SKILL.md) 覆盖男频、女频、武侠、玄幻、修真、都市、悬疑、科幻、历史、言情、轻喜剧及混合题材。准备世界规则、人物弧线、全书因果大纲与主要谜题答案，冻结核心后进入正文；每章围绕主推进交织关系、生活或支线，维护人物认知、物件状态和伏笔兑现。

随附[参考指南](skills/web-novel-writer/references/quality-review.md)、[故事工程](skills/web-novel-writer/templates/story-bible.md)、[章节卡](skills/web-novel-writer/templates/chapter-card.md)、[连续性台账](skills/web-novel-writer/templates/continuity-ledger.md)、[章评](skills/web-novel-writer/templates/chapter-review.md)及[新工程布局](skills/web-novel-writer/templates/project-layout.md)。词库按情境使用，避免形容词拼贴；质量验收先查阻断项，再改因果、人物、节奏与语言。纯文档流程，无需安装脚本或调用外部生成 API。

针对没有文学经验的作者，还提供[人物与长篇续航](skills/web-novel-writer/references/characters-and-longform.md)、[资料核查与阅读体验](skills/web-novel-writer/references/research-and-reader-experience.md)和[稿件流程与稳定维护](skills/web-novel-writer/references/workflow-and-maintenance.md)：覆盖成长回报、情绪变化、开篇信息负荷、专业事实、版本/备份恢复和副业节奏。按任务读取，不每章机械填完全部表；作品特例留在作品工程，减少通用 skill 的频繁改动。版本变化见 [CHANGELOG](skills/web-novel-writer/CHANGELOG.md)。

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
