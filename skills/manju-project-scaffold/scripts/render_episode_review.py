#!/usr/bin/env python3
"""Render a local current-selection overview. No network or production side effects."""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

CATEGORIES = {
    'script': '剧本', 'images': '图片素材', 'audio': '音频素材',
    'video': '视频片段', 'sfx': '音效', 'music': '音乐', 'final': '成片',
}
EXCLUDED = {'已退回', '已废弃', '已替换'}
TEMPLATE = Path(__file__).resolve().parents[1] / 'assets' / 'episode-review.html'


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def local_file(value: object, base: Path) -> Path:
    if not isinstance(value, str) or not value.strip() or '://' in value:
        raise ValueError('素材须使用非空本地路径')
    path = (base / value).resolve()
    if not path.is_file():
        raise ValueError(f'当前素材不存在: {path}')
    return path


def link_to(path: Path, page_dir: Path, directory: bool = False) -> str:
    try:
        value = quote(Path(os.path.relpath(path, page_dir)).as_posix(), safe='/')
    except ValueError:  # Windows cross-drive resources cannot use a relative path.
        value = path.as_uri()
    return escape(value + ('/' if directory and not value.endswith('/') else ''))


def folder_links(folder: Path, page_dir: Path, key: str) -> str:
    return (
        f'<a class="link" href="{link_to(folder, page_dir, True)}">打开所在文件夹</a>'
        f'<button type="button" data-copy="{key}">复制文件夹路径</button>'
        f'<details><summary>文件夹路径</summary><input class="path" id="{key}" '
        f'aria-label="文件夹路径" readonly value="{escape(folder)}"></details>'
    )


def current_items(data: dict) -> list[dict]:
    items = data.get('items', [])
    if not isinstance(items, list):
        raise ValueError('items 须为数组')
    seen: set[tuple[str, str]] = set()
    selected = []
    for item in items:
        if not isinstance(item, dict) or type(item.get('current')) is not bool:
            raise ValueError('每项素材须明确声明布尔 current')
        if not item['current']:
            continue
        for key in ('id', 'category', 'version', 'status', 'path'):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise ValueError(f'当前素材缺少非空字段: {key}')
        category = item['category']
        if category not in CATEGORIES:
            raise ValueError(f'未知素材类别: {category}')
        identity = (category, item['id'])
        if identity in seen:
            raise ValueError(f'同一素材存在多个当前版本: {identity}')
        seen.add(identity)
        if item['status'] not in EXCLUDED:
            selected.append(item)
    return selected


def render(manifest: Path, output: Path | None = None) -> Path:
    manifest = manifest.resolve()
    output = output.resolve() if output else manifest.with_name('本集制作总览.html')
    if output == manifest:
        raise ValueError('HTML 输出不能覆盖素材清单')
    if output.suffix.lower() != '.html' or output == TEMPLATE.resolve():
        raise ValueError('输出须为独立 HTML，不能覆盖技能模板')
    data = json.loads(manifest.read_text(encoding='utf-8-sig'))
    if not isinstance(data, dict):
        raise ValueError('素材清单须为 JSON 对象')
    selected = current_items(data)
    groups: dict[str, list[tuple[dict, Path, Path]]] = {key: [] for key in CATEGORIES}
    for item in selected:
        source = local_file(item['path'], manifest.parent)
        preview = local_file(item.get('preview', item['path']), manifest.parent)
        if output in (source, preview):
            raise ValueError('HTML 输出不能覆盖当前素材')
        groups[item['category']].append((item, source, preview))
    sections, nav = [], []
    for category, title in CATEGORIES.items():
        rows = groups[category]
        if not rows:
            continue
        nav.append(f'<a href="#{category}">{title} · {len(rows)}</a>')
        folders = list(dict.fromkeys(source.parent for _, source, _ in rows))
        header_links = ''.join(folder_links(folder, output.parent, f'{category}-folder-{i}') for i, folder in enumerate(folders))
        cards = []
        for i, (item, source, preview) in enumerate(rows):
            url = link_to(source, output.parent)
            if category == 'script':
                media = f'<pre>{escape(source.read_text(encoding="utf-8-sig"))}</pre>'
            elif category == 'images':
                media = f'<a href="{url}"><img loading="lazy" src="{link_to(preview, output.parent)}" alt="{escape(item.get("label", item["id"]))}"></a>'
            elif category in ('video', 'final'):
                media = f'<video controls preload="none" playsinline src="{url}"></video>'
            else:
                media = f'<audio controls preload="none" src="{url}"></audio>'
            cards.append(
                f'<article class="{"script-card" if category == "script" else "media-card"}">'
                f'<h3>{escape(item.get("label", item["id"]))}</h3>'
                f'<span class="version">{escape(item["version"])}</span>'
                f'<span class="status">{escape(item["status"])}</span>'
                f'<p>{escape(item.get("note", ""))}</p>{media}<div class="links">'
                f'<a class="link" href="{url}">打开原文件</a>'
                f'<a class="link" href="{url}" download>下载原文件</a>'
                f'{folder_links(source.parent, output.parent, f"{category}-item-{i}")}</div></article>'
            )
        sections.append(f'<section id="{category}"><div class="section-head"><h2>{title}</h2><div class="links">{header_links}</div></div><div class="grid">{"".join(cards)}</div></section>')
    tasks = data.get('tasks', [])
    if not isinstance(tasks, list) or any(not isinstance(t, dict) or not all(isinstance(t.get(k), str) for k in ('name', 'status')) for t in tasks):
        raise ValueError('tasks 须为含 name/status 字符串的任务数组')
    task_html = ''
    if tasks:
        rows = ''.join(f'<tr><td>{escape(t["name"])}</td><td>{escape(t["status"])}</td><td>{escape(t.get("note", ""))}</td></tr>' for t in tasks)
        task_html = f'<section class="tasks"><h2>任务进度</h2><div class="table-wrap"><table><thead><tr><th>任务</th><th>实际状态</th><th>说明</th></tr></thead><tbody>{rows}</tbody></table></div></section>'
    values = {
        'TITLE': escape(data.get('title', '本集制作总览')),
        'SUMMARY': escape(data.get('summary', '尚未登记制作状态')),
        'UPDATED': escape(data.get('updated_at') or '尚未登记'),
        'RENDERED': escape(datetime.now().astimezone().isoformat(timespec='seconds')),
        'MANIFEST_LINK': f'<a class="link" href="{link_to(manifest, output.parent)}">查看素材清单</a>',
        'NAV': ''.join(nav), 'TASKS': task_html,
        'SECTIONS': ''.join(sections) or '<section class="empty">尚无当前素材；生成或登记后更新本页。</section>',
    }
    page = TEMPLATE.read_text(encoding='utf-8')
    # One pass avoids interpreting template-like text inside a user's script as markup.
    page = re.sub(r'@@([A-Z_]+)@@', lambda match: values[match.group(1)], page)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=output.parent, suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(page)
        temporary.replace(output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return output


def initialize_review(episode: Path) -> None:
    folder = episode / '制作审阅'
    folder.mkdir(parents=True, exist_ok=True)
    manifest = folder / '素材清单.json'
    if not manifest.exists():
        with manifest.open('x', encoding='utf-8') as stream:
            json.dump({'title': f'{episode.name} · 制作总览', 'summary': '准备中', 'updated_at': '', 'items': [], 'tasks': []}, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
    if not (folder / '本集制作总览.html').exists():
        render(manifest)


def main() -> None:
    parser = argparse.ArgumentParser(description='按明确的当前素材选择刷新本集 HTML；不执行生成或上传')
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        print(render(args.manifest, args.output))
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f'审阅页未更新: {error}\n')


if __name__ == '__main__':
    main()
