# 执行与恢复

## 环境与命令

选择已安装的解释器；不安装/升级环境。脚本以 8 MiB 块流式处理，Zstd 默认 level 3、128 MiB 窗口、长距离匹配及帧校验；这组参数来自含重复图片/工具数据的旧实例，不保证所有聊天都有相同压缩率。gzip level 1 是无 Zstd 时的兼容选择。

下面 $py、$tool、$source、$threadId、$out 都是需核实的本机变量，不能沿用其他用户或旧任务的值。PowerShell：

```powershell
# 先设置变量；需要时另传 --codex-home。
& $py -B -X utf8 $tool inspect --source $source --thread-id $threadId
& $py -B -X utf8 $tool snapshot --source $source --thread-id $threadId --output $out
& $py -B -X utf8 $tool verify --archive $out
```

`snapshot` 不删除源文件，目标必须新建或为空。它复制自包含 `archive_session.py` 到归档目录，以后技能路径改变仍可恢复。将填好的 `handoff.md` 另存该目录；脚本不会生成工程事实。归档内 `.gitignore` 防止意外提交，仍需检查上层 Git 或云同步设置；压缩本身不是加密。

回执 `archive.manifest.json` 中包含：原身份与文件 ID、快照边界、相对分卷名及顺序、每卷压缩/解压大小与 SHA、拼接后大小/SHA、收尾与删除状态。分卷名必须是目录内普通文件；拒绝链接、目录逃逸及未知格式。整体目录搬家后 `verify`、`restore` 按相对分卷名工作；`seal` 仍需原位置、原文件身份，搬过源文件应重新检查而不是改回执绕过。

## 退出后收尾

不要通过当前 Codex 执行真正删除。用户**完全退出应用/托盘及 Codex CLI**后，在普通终端运行归档内脚本。先确保没有还需运行的任务；此脚本不终止应用，也不操作租赁。

```powershell
$archivedTool = Join-Path $out 'archive_session.py'
# 默认：补齐并核验最终尾部，仍保留原日志。
& $py -B -X utf8 $archivedTool seal --archive $out

# 仅已有明确删除授权时，交付下面这条命令。
& $py -B -X utf8 $archivedTool seal --archive $out --delete-source --confirm-thread $threadId
```

删除只在 Windows 实现，使用独占句柄核验并标记**同一个文件**删除；原路径不可替换为泛配符。验证过程包括原压缩卷、全部解压内容、原文件前缀与最终全文件。成功前先保存 `SEALED_VERIFIED` 回执，删除成功后更新为 `SOURCE_DELETED`。断电或权限问题发生在两者之间时，可能只有前者；先核实源文件是否仍存在，不能凭输出缺失推测，也不自动删归档。

`.archive-operation.lock` 防止并发运行同一归档；异常中断留下锁时先查对应进程及回执，确认没有活跃归档操作后才可清除这个任务锁。不删除 `.partial` 来掩盖失败，它们与真实完成卷不同；后续清理也需按授权精确处理。

## 恢复

```powershell
& $py -B -X utf8 $archivedTool restore --archive $out --to $newJsonl
```

只写**新文件**，位于原 Codex 状态外；提前检查未压缩大小所需空间。边解压边核验各卷及合并 SHA，成功后才把 `.partial` 发布为指定文件。发布通过同目录硬链接避免覆盖已有文件，因此恢复目标文件系统必须支持硬链接；不支持时保留已核验临时文件并明确报错，不静默改用覆盖写。单聊天原始证据可恢复，不包含共享数据库、账号与完整 UI 状态。

## 研究旧格式

旧回执可能叫 `备份校验回执.json`、`退出后完整备份校验.json`、`原日志删除完成.json`，部分路径为旧绝对目录。优先读最终删除/封存回执的 `backup_parts_in_restore_order`，逐卷以当前目录下 basename 核对尺寸与压缩 SHA，再按明确格式完整解压拼接，核对 `full_source_bytes`、`full_source_sha256`。只有首卷快照回执时，覆盖范围仅限 `snapshot_complete_record_bytes`。

现有 helper 不自动迁移或改写旧回执；不要直接运行旧目录脚本，它们可能写死另一个人的线程和删除目标。需要实际恢复旧格式时先准备新的适配器及新输出路径，并在夹具验证后执行。归档迁移不包含恢复旧自动任务或重建旧聊天。

## 本机行为检查

```powershell
& $py -B -X utf8 -m unittest discover -s '<skill>/scripts' -p 'test_archive_session.py' -v
```

这些测试只删除 `TemporaryDirectory` 内的假日志，Windows 文件占用与独占句柄行为使用真实系统调用。应用存活检查在夹具用 mock；实际 CLI 在 Codex 内必须拒绝 `seal`，即使默认不删除。不要为跑测试退出用户应用。
