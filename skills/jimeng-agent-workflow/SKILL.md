---
name: jimeng-agent-workflow
description: 通过 agent-browser 浏览器自动化工具，全程驱动即梦（Jimeng）AI 创作平台的 Agent 模式完成漫剧全流程创作。涵盖：项目初始化→提交创意需求→质量评估与迭代反馈→素材生成（角色/场景图）→视频生成→持续进度监控。当用户需要创作新漫剧项目、在即梦上生成 AI 素材、使用即梦 Agent 模式进行全流程短视频创作时调用。触发词包括：即梦创作、在即梦上做漫剧、用即梦Agent生成、即梦全流程、浏览器操作即梦、自动化即梦创作。
---

# 即梦 Agent 全流程自动化创作工作流

通过 agent-browser CLI 工具操作即梦网页版 Agent 模式，完成从需求输入到视频生成的完整创作流程。

## 前置依赖

- `agent-browser` CLI（v0.23+），安装：`npm i -g agent-browser`
- 即梦账号（支持抖音扫码登录）
- 工作区须有 `manju-project-scaffold` skill（用于创建项目目录）

## 核心原则

### 1. 持续主动推进，不等待用户确认

**这是最重要的原则。** 每一步操作完成后，立即用轮询检查 Agent 是否完成，一旦完成就立刻推进下一步。永远不要停下来等用户说"继续"。只有遇到以下情况才暂停：

- 需要抖音扫码登录
- Agent 弹出积分消耗确认框
- Agent 产出质量确实无法判断需要人工看画面
- 浏览器会话彻底断连无法恢复

### 2. 轮询节奏

| 任务类型 | 轮询间隔 | 超时容忍 |
|---------|---------|---------|
| 文字输出（大纲/角色/脚本） | 15-20s | 2分钟 |
| 图片生成（角色/场景图） | 20-30s | 5分钟 |
| 视频片段生成 | 45-60s | 15分钟 |

### 3. 浏览器会话管理

```bash
# 启动时必须用带持久化会话名的 headed 模式
agent-browser --headed --session-name jimeng open https://jimeng.jianying.com/ai-tool/home

# 之后所有命令都要带 --session-name
agent-browser --session-name jimeng <command>

# 会话超时时恢复
agent-browser close --all
agent-browser --headed --session-name jimeng open https://jimeng.jianying.com/ai-tool/home
```

**注意事项：**
- PowerShell 不支持 `&&` 串联，改用 `;`
- ref 引用（如 `@e24`）在页面导航后会失效，每次页面变化后重新 `snapshot -i`
- 长时间 wait 后 CDP 可能断连，连接失败时执行 `close --all` 再重新 `open`

---

## 阶段 0：项目初始化

### 步骤 0.1：创建项目目录
使用 `manju-project-scaffold` skill 创建项目结构：

```bash
python ".cursor/skills/manju-project-scaffold/scripts/scaffold_manju.py" project <项目名>
```

### 步骤 0.2：起草 Agent 初始需求

向用户确认核心方向后，起草需求文档保存到 `<项目>/大纲/即梦Agent初始需求.md`。需求必须包含：

```markdown
- 主题/类型
- 叙事方式
- 视觉风格
- 平台与格式（抖音竖屏 9:16 或横屏 16:9）
- 时长范围（90-180s）
- 故事核心（一句话概括）
- 情感基调（情绪弧线）
- 请Agent完成的6项任务：故事大纲、角色设计、场景设计、分镜脚本、AI生图提示词、AI视频提示词
- 特殊要求（Seedance格式、非写实、中国神话风格等）
```

### 步骤 0.3：起草质量评估框架

保存到 `<项目>/大纲/质量评估框架.md`，定义5个评估阶段的标准。（详见 [references/quality-assessment-framework.md](references/quality-assessment-framework.md)）

---

## 阶段 1：启动浏览器并登录即梦

### 1.1 打开即梦

```bash
agent-browser --headed --session-name jimeng open https://jimeng.jianying.com/ai-tool/home
agent-browser --session-name jimeng wait --load networkidle
```

### 1.2 检查登录状态

```bash
agent-browser --session-name jimeng snapshot -i
```

在输出中查找 `"高级会员"` 关键词 —— 如果出现说明已登录。如果看到 `"登录"` 按钮，点击：

```bash
agent-browser --session-name jimeng click '<登录按钮ref>'
agent-browser --session-name jimeng wait 2000
agent-browser --session-name jimeng click '<抖音登录ref>'
```

然后会出现用户协议弹窗，点击 "同意"：
```bash
agent-browser --session-name jimeng click '<同意按钮ref>'
```

**告知用户在浏览器窗口中完成扫码。**

### 1.3 确认为 Agent 模式

登录后 snapshot 检查：搜索 `textbox` 元素（输入框），确认其 placeholder 包含"Agent"字样。如果进入的是其他页面，点击导航栏的"生成"或首页的"Agent 模式"卡片。

---

## 阶段 2：提交创意需求

### 2.1 定位输入框并填入需求

```bash
agent-browser --session-name jimeng snapshot -i
# 找到 textbox 的 ref，例如 @e61
```

读取需求文件，将内容精简后填入（即梦输入框有字符限制）：

```bash
agent-browser --session-name jimeng click '<textbox_ref>'
agent-browser --session-name jimeng fill '<textbox_ref>' "<精简后的需求描述>"
agent-browser --session-name jimeng press Enter
```

需求精简原则：保留核心要素（主题、风格、平台、时长、叙事结构、情感基调、6项任务），去掉 Markdown 格式符号。

### 2.2 监控 Agent 开始处理

```bash
agent-browser --session-name jimeng wait 15000
agent-browser --session-name jimeng get text body
```

检查输出中是否出现"认真思考中"或"使用技能"——确认 Agent 已接收任务。

---

## 阶段 3：质量评估与迭代反馈

### 3.1 持续轮询获取完整产出

Agent 产出文字内容时，每隔 15-20s 执行：

```bash
agent-browser --session-name jimeng wait 20000
agent-browser --session-name jimeng scroll down 3000
agent-browser --session-name jimeng get text body
```

检查产出完整性：确认是否已包含大纲、角色设计、场景设计、分镜脚本、生图提示词、视频提示词、配乐建议、制作建议共约8-9个模块。

### 3.2 首轮质量评估

对照质量评估框架进行逐项评估。评估报告保存到 `<项目>/大纲/第一轮质量评估.md`（或综合质量评估报告.md）。

**评估重点：**

| 模块 | 关键检查项 |
|------|-----------|
| 故事大纲 | 三幕结构是否完整，情感曲线是否匹配需求 |
| 角色设计 | 维度表是否齐全（体型/面部/发型/服饰/武器/色彩/气质），生图关键词是否包含"非写实真人" |
| 场景设计 | 元素表是否齐全（空间/光线/材质/氛围/视觉重点），关键词是否完整 |
| 分镜脚本 | 分镜数量（建议15-18个），景别多样性，单Clip≤15s，总时长在约束内 |
| 生图提示词 | 是否有统一风格前缀 + 负面约束，每条是否包含构图信息 |
| 视频提示词 | 是否每个Clip有独立提示词，时长≤15s，是否使用@素材引用 |

### 3.3 提交修改反馈

如果产出合格（评分≥4/5），跳过此步直接进入阶段4。

如果需要修改，将反馈填入输入框并发送：

```bash
agent-browser --session-name jimeng click '<textbox_ref>'
agent-browser --session-name jimeng fill '<textbox_ref>' "<修改意见>"
agent-browser --session-name jimeng press Enter
```

修改意见应具体、可执行、以"请"开头。示例格式：
```
整体非常好，请按以下意见微调：
1.【模块名】具体修改内容。
2.【模块名】具体修改内容。
以上，其他内容出色，请修改后输出最终版。
```

然后回到阶段3.1继续轮询，直到产出通过。

**迭代最多2轮**。2轮后如仍不通过，只再次强调未解决的1-2个关键问题。

---

## 阶段 4：素材生成

### 4.1 角色设定图（3张）

产出通过后，立即提交角色图指令，**不等用户确认**：

```bash
agent-browser --session-name jimeng click '<textbox_ref>'
agent-browser --session-name jimeng fill '<textbox_ref>' "方案已确认。现在执行制作建议的【阶段1】：生成角色设定图。请按以下顺序逐一生成：1.盘古角色设定图 2.女娲角色设定图 3.初生人类群像图。使用最终版提示词，一次性生成。"
agent-browser --session-name jimeng press Enter
```

轮询间隔 20-30s，检查是否出现 `(3/3) 图片生成完成`。

### 4.2 场景参考图（5张）

角色图完成后立即提交场景图：

```bash
agent-browser --session-name jimeng fill '<textbox_ref>' "角色图已确认。现在执行【阶段2】生成场景参考图：1.混沌虚空 2.初开天地 3.洪荒大地 4.造人河畔 5.结尾长卷定格。一次性生成。"
agent-browser --session-name jimeng press Enter
```

### 4.3 图片质量速查

图片生成完成后 `screenshot --annotate` 检查是否存在明显问题（角色肢体变形、场景元素缺失等）。如果没有明显问题，直接推进到视频生成，不做精细评估。

---

## 阶段 5：视频生成

### 5.1 提交视频生成指令

```bash
agent-browser --session-name jimeng fill '<textbox_ref>' "图片素材已全部确认。现在执行【阶段4】逐条生成视频。Clip数量共16个，每段4-10秒。请使用最终版的视频提示词和@素材引用一次性提交生成。"
agent-browser --session-name jimeng press Enter
```

### 5.2 处理积分确认

如果 Agent 弹出积分消耗确认框，点击"继续生成"：

```bash
agent-browser --session-name jimeng click '<继续生成按钮ref>'
```

### 5.3 视频生成监控

轮询间隔 45-60s，检查进度百分比（如 `36%造梦中`）。视频生成是后台任务，**即梦服务端独立运行，浏览器断连不影响生成**。

进度达 100% 或出现视频缩略图后，截图记录成果。

---

## 阶段 6：收尾

所有素材生成完成后：

1. `screenshot` 保存最终成果截图到项目目录
2. 汇总各阶段产出清单（大纲、角色图×3、场景图×5、视频×16-18）
3. 提醒用户后续工作：剪辑合成、添加旁白/配乐/音效、二次精修

---

## 常见问题处理

### 浏览器会话断连

```
错误: CDP error / Session with given id not found
→ agent-browser close --all
→ agent-browser --headed --session-name jimeng open https://jimeng.jianying.com/ai-tool/home
→ 重新登录（可能丢失登录态）
→ 登录后 Agent 对话历史会恢复，素材和视频在"生成"标签中
```

### click 失败 "Missing arguments"

PowerShell 中 `@` 符号需加引号：`click '@e24'` 而不是 `click @e24`。

### fill 后文本未出现

文本过长可能被截断。精简内容后重试。如果输入框已有旧文本，先 `click` 再 `fill`。

### Agent 输出被截断

输出过长时 `get text body` 会截断。使用 `scroll down 5000` 后重新获取。如果内容在折叠的"展开"按钮后，先 `click '<展开ref>'`。

### 用户中途打断

如果用户在等待过程中发了新消息，立即响应。响应后回到刚才中断的轮询步骤继续。

---

## 参考资源

- [质量评估框架详细标准](references/quality-assessment-framework.md)
- `manju-project-scaffold` skill — 项目目录脚手架
- `seedance-storyboard` skill — Seedance 2.0 提示词规范（可参考，本skill中由即梦Agent自行生成提示词）
