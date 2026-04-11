# 多 IDE 安装路径（Agent Skills / `SKILL.md`）

本技能目录名应为 **`slacker-data-security`**，且内含根文件 **`SKILL.md`**（及可选的 `references/`、`scripts/`、`assets/`）。

> **免责声明**：各产品路径与 CLI 可能随版本变更。下表依据公开文档与社区资料整理；安装前请在对应 IDE 官方文档中复核。若某产品不支持 Agent Skills，可将本目录作为普通参考文档使用。

## 推荐安装方式（通用）

将本技能**整个文件夹**复制到目标 IDE 的 **用户级（全局）** 或 **项目级** skills 目录，使最终路径形如：

`.../skills/slacker-data-security/SKILL.md`

Windows 下将 `~` 理解为 `%USERPROFILE%`。

## 从 GitHub 安装（官方仓库 `ck1049/slacker-skills`）

- **SSH（推荐）**：`git@github.com:ck1049/slacker-skills.git`
- **HTTPS**：`https://github.com/ck1049/slacker-skills.git`

### 仓库内技能路径（二选一，以你仓库实际结构为准）

| 布局 | 克隆后技能目录相对仓库根的路径 |
|------|--------------------------------|
| 单技能仓库（根下直接放技能） | `slacker-data-security/` |
| 多技能仓库（常见 monorepo） | `skills/slacker-data-security/` |

下文用 **`SKILL_SRC`** 表示上表中选定的相对路径（例如 `slacker-data-security` 或 `skills/slacker-data-security`）。

安装前请确认目标目录下 **`slacker-data-security/SKILL.md`** 存在；若已存在旧版，先删除再复制，避免嵌套错乱。

---

### Bash（macOS / Linux / Git Bash）— 安装到 **Cursor 全局**

```bash
export REPO_URL="git@github.com:ck1049/slacker-skills.git"
# 若使用 HTTPS：export REPO_URL="https://github.com/ck1049/slacker-skills.git"
export SKILL_SRC="slacker-data-security"   # 或改为 skills/slacker-data-security

tmpdir="$(mktemp -d)"
git clone --depth 1 "$REPO_URL" "$tmpdir/slacker-skills"
mkdir -p "$HOME/.cursor/skills"
rm -rf "$HOME/.cursor/skills/slacker-data-security"
cp -R "$tmpdir/slacker-skills/$SKILL_SRC" "$HOME/.cursor/skills/slacker-data-security"
rm -rf "$tmpdir"
```

### Bash — 安装到 **当前 Git 仓库的 Cursor 项目级**

```bash
export REPO_URL="git@github.com:ck1049/slacker-skills.git"
export SKILL_SRC="slacker-data-security"   # 或 skills/slacker-data-security

tmpdir="$(mktemp -d)"
git clone --depth 1 "$REPO_URL" "$tmpdir/slacker-skills"
mkdir -p ".cursor/skills"
rm -rf ".cursor/skills/slacker-data-security"
cp -R "$tmpdir/slacker-skills/$SKILL_SRC" ".cursor/skills/slacker-data-security"
rm -rf "$tmpdir"
```

### Bash — 安装到 **Claude Code 全局**

将上面命令中的目标目录替换为：

```bash
mkdir -p "$HOME/.claude/skills"
rm -rf "$HOME/.claude/skills/slacker-data-security"
cp -R "$tmpdir/slacker-skills/$SKILL_SRC" "$HOME/.claude/skills/slacker-data-security"
```

（克隆段与 `SKILL_SRC` 与 Cursor 示例相同。）

### Bash — 安装到 **Codex CLI 全局**（`~/.codex/skills`）

```bash
mkdir -p "$HOME/.codex/skills"
rm -rf "$HOME/.codex/skills/slacker-data-security"
cp -R "$tmpdir/slacker-skills/$SKILL_SRC" "$HOME/.codex/skills/slacker-data-security"
```

### Bash — **Trae / Qoder / OpenCode** 全局（按需替换目标根目录）

| 产品 | 全局 skills 根目录 |
|------|-------------------|
| Trae | `$HOME/.trae/skills` |
| Qoder | `$HOME/.qoder/skills` |
| OpenCode | `$HOME/.opencode/skills` |

```bash
export DEST_ROOT="$HOME/.trae/skills"   # 或 .qoder/skills / .opencode/skills
mkdir -p "$DEST_ROOT"
rm -rf "$DEST_ROOT/slacker-data-security"
cp -R "$tmpdir/slacker-skills/$SKILL_SRC" "$DEST_ROOT/slacker-data-security"
```

### Bash — **Google Antigravity 全局**

```bash
mkdir -p "$HOME/.gemini/antigravity/skills"
rm -rf "$HOME/.gemini/antigravity/skills/slacker-data-security"
cp -R "$tmpdir/slacker-skills/$SKILL_SRC" "$HOME/.gemini/antigravity/skills/slacker-data-security"
```

### Bash — **Gemini CLI 全局**（与 Antigravity 路径不同）

```bash
mkdir -p "$HOME/.gemini/skills"
rm -rf "$HOME/.gemini/skills/slacker-data-security"
cp -R "$tmpdir/slacker-skills/$SKILL_SRC" "$HOME/.gemini/skills/slacker-data-security"
```

---

### PowerShell（Windows）— **Cursor 全局**

```powershell
$RepoUrl = "git@github.com:ck1049/slacker-skills.git"
# 若使用 HTTPS：$RepoUrl = "https://github.com/ck1049/slacker-skills.git"
$SkillSrc = "slacker-data-security"   # 或 skills\slacker-data-security

$tmp = Join-Path $env:TEMP ("slacker-skills-" + [Guid]::NewGuid().ToString("N"))
git clone --depth 1 $RepoUrl $tmp
$dest = Join-Path $env:USERPROFILE ".cursor\skills\slacker-data-security"
Remove-Item -Recurse -Force $dest -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path (Split-Path $dest) | Out-Null
Copy-Item -Recurse -Force (Join-Path $tmp $SkillSrc) $dest
Remove-Item -Recurse -Force $tmp
```

### PowerShell — **当前项目 Cursor 目录**（在仓库根执行）

```powershell
$RepoUrl = "git@github.com:ck1049/slacker-skills.git"
$SkillSrc = "slacker-data-security"   # 或 skills\slacker-data-security

$tmp = Join-Path $env:TEMP ("slacker-skills-" + [Guid]::NewGuid().ToString("N"))
git clone --depth 1 $RepoUrl $tmp
$dest = Join-Path (Get-Location) ".cursor\skills\slacker-data-security"
Remove-Item -Recurse -Force $dest -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path (Split-Path $dest) | Out-Null
Copy-Item -Recurse -Force (Join-Path $tmp $SkillSrc) $dest
Remove-Item -Recurse -Force $tmp
```

将 `$dest` 改为 `$env:USERPROFILE\.claude\skills\...`、`.trae\skills`、`.qoder\skills`、`.codex\skills`、`.gemini\antigravity\skills` 等即可对应其它 IDE（路径见上表）。

---

### OpenAI Codex：`skill-installer` 脚本（若本机已安装 Codex 技能包）

```bash
python "$CODEX_HOME/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo ck1049/slacker-skills \
  --path slacker-data-security
```

若技能在子目录 `skills/slacker-data-security`，将 `--path` 改为 `skills/slacker-data-security`。

---

### 可选：`npx skills` / `npx agent-skills`（以各工具 README 为准）

```bash
# 示例（参数以你安装的 CLI 版本为准；安装后核对是否落在 ~/.cursor/skills）
npx skills add ck1049/slacker-skills --skill slacker-data-security -a cursor -y
```

若 CLI 将文件装到非 Cursor 目录，请按上文 **手动复制** 到 `~/.cursor/skills/slacker-data-security/`。

---

### 可选：sparse clone（仓库很大且只需本技能时）

```bash
git clone --filter=blob:none --sparse git@github.com:ck1049/slacker-skills.git
cd slacker-skills
git sparse-checkout set skills/slacker-data-security   # 按实际路径修改
# 再将 skills/slacker-data-security 复制到目标 IDE 的 skills 目录
```

## 路径对照表

| IDE / 工具 | 用户级（全局） | 项目级（仓库内） |
|-------------|----------------|------------------|
| **Cursor** | `~/.cursor/skills/slacker-data-security/` | `<repo>/.cursor/skills/slacker-data-security/` |
| **Claude Code** | `~/.claude/skills/slacker-data-security/` | `<repo>/.claude/skills/slacker-data-security/` |
| **OpenAI Codex CLI** | `~/.codex/skills/slacker-data-security/` | 以 Codex 文档为准（常见为仅用户级） |
| **Trae** | `~/.trae/skills/slacker-data-security/` | `<repo>/.trae/skills/slacker-data-security/` |
| **Qoder**（IDE / CLI） | `~/.qoder/skills/slacker-data-security/` | `<repo>/.qoder/skills/slacker-data-security/` |
| **Google Antigravity** | `~/.gemini/antigravity/skills/slacker-data-security/` | `<repo>/.agent/skills/slacker-data-security/` |
| **Gemini CLI**（与 Antigravity 全局路径不同） | `~/.gemini/skills/slacker-data-security/` | 以 Gemini CLI 文档为准 |
| **OpenCode** | `~/.opencode/skills/slacker-data-security/` | `<repo>/.opencode/skills/slacker-data-security/` |

CLI 安装注意事项已写在上方 **「可选：`npx skills`」** 小节。

## 单仓库多技能（供个人 skill 仓库使用）

若 Git 仓库根为：

```text
skills/
  slacker-data-security/
    SKILL.md
    references/
```

则安装时只复制 **`skills/slacker-data-security/`** 这一层到上表对应目录，**不要**多嵌套一层仓库根目录名。
