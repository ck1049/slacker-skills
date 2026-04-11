# slacker-skills

本仓库用于发布个人整理的 Agent 技能（`SKILL.md` 及相关参考文档）。技能按目录放在 `skills/<skill-name>/` 下，便于通过 `skills` CLI 一键拉取安装。

**声明**：仓库内技能均由作者个人整理与维护，与任何厂商或社区的「官方技能集合」均无隶属、合作或背书关系；是否采用请自行评估风险与适用场景。

## 安装

在已安装 Node.js 的环境中执行其一即可：

```bash
npx skills add git@github.com:ck1049/slacker-skills.git
```

```bash
npx skills add https://github.com/ck1049/slacker-skills.git
```

安装完成后，按你所用工具（如 Cursor、Codex 等）的说明，将技能目录加入 Agent 可读取的技能路径。

## 当前技能一览

| 技能 ID | 说明 |
| -------- | ---- |
| `slacker-data-security` | 与编程语言无关的分层数据安全规范：业务 RSA/AES、通信 RSA、OAEP 分段、AES-GCM、口令慢哈希与通信密钥失效错误码等，适用于设计与评审多端敏感数据方案。 |

## 仓库地址

- GitHub：<https://github.com/ck1049/slacker-skills>

## 许可与贡献

技能内容以仓库内各 `SKILL.md` 及附带文件为准。若你发现描述或示例有误，欢迎通过 Issue 或 Pull Request 反馈。
