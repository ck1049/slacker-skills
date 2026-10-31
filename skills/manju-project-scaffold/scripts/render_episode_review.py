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


def input_reference_panel(item: dict, base: Path, page_dir: Path) -> str:
    """Render explicitly bound inputs, never infer them from global assets."""
    refs = item.get('input_references')
    if refs is None:
        return '<p class="small">本镜实际输入参考尚未记录，需从任务回执补齐。</p>'
    if not isinstance(refs, list):
        raise ValueError('input_references 须为数组')
    if not refs:
        return '<p class="small">已记录本镜无图片、音频或视频参考输入。</p>'
    entries = []
    for ref in refs:
        if not isinstance(ref, dict) or ref.get('kind') not in ('image', 'audio', 'video', 'record'):
            raise ValueError('参考输入须指定 image、audio、video 或 record')
        path = local_file(ref.get('path'), base)
        url = link_to(path, page_dir)
        label = escape(ref.get('label', '参考输入'))
        role = escape(ref.get('role', ''))
        digest = escape(ref.get('sha256', '未记录'))
        preview = (f'<a href="{url}"><img loading="lazy" src="{url}" '
                   f'alt="{label}" style="max-width:190px;max-height:240px;object-fit:contain"></a>'
                   if ref['kind'] == 'image' else '')
        if ref['kind'] == 'audio':
            preview = f'<audio controls preload="none" src="{url}"></audio>'
        elif ref['kind'] == 'video':
            preview = f'<video controls preload="none" playsinline src="{url}"></video>'
        entries.append(f'<div data-reference-kind="{escape(ref["kind"])}">{preview}<p><a href="{url}">{label}</a> · {role} '
                       f'<small>SHA-256：{digest}</small></p></div>')
    return ('<details class="input-references"><summary>查看本镜实际绑定的参考图与音色（全部图片、音频及视频）</summary>'
            '<p>输入绑定不等于输出或听审通过；点击图片查看原图。</p>'
            + ''.join(entries) + '</details>')


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
        if 'stale' in item and type(item['stale']) is not bool:
            raise ValueError('stale 须为布尔值')
        if not any(status in item['status'] for status in EXCLUDED) and not item.get('stale', False):
            selected.append(item)
    return selected


def render_adoption(data: dict, finals: list[dict], base: Path, output: Path) -> str:
    """Show only the exported cut's explicit provenance, never every downloaded take."""
    adoption = data.get('adoption')
    if adoption is None or not finals:
        return ''
    if not isinstance(adoption, dict) or len(finals) != 1:
        raise ValueError('采用清单须绑定一个当前完整候选')
    final = finals[0]
    if (adoption.get('version') != final['version'] or not final.get('sha256')
            or adoption.get('final_sha256') != final['sha256']):
        raise ValueError('采用清单与当前成片版本或指纹不符')
    fps = adoption.get('fps')
    if type(fps) not in (int, float) or not 0 < fps <= 240:
        raise ValueError('采用清单须声明有效 fps')
    clips, assets = adoption.get('clips'), adoption.get('assets', [])
    if not isinstance(clips, list) or not clips or not isinstance(assets, list):
        raise ValueError('采用清单 clips 须为非空数组，assets 须为数组')

    def file_url(record: dict) -> str:
        if not isinstance(record, dict):
            raise ValueError('采用来源须为对象')
        path = local_file(record.get('path'), base)
        if path == output:
            raise ValueError('HTML 输出不能覆盖采用素材')
        return link_to(path, output.parent)

    def timecode(frame: int) -> str:
        millis = round(frame / fps * 1000)
        minutes, rest = divmod(millis, 60000)
        seconds, fraction = divmod(rest, 1000)
        return f'{minutes:02}:{seconds:02}.{fraction:03}'

    def frame_range(value: object) -> tuple[int, int]:
        if (not isinstance(value, list) or len(value) != 2
                or any(type(v) is not int for v in value) or not 0 <= value[0] < value[1]):
            raise ValueError('采用区间须为 [起帧, 结束帧)，不能为空或倒置')
        return value[0], value[1]

    cards = []
    for i, clip in enumerate(clips, 1):
        if not isinstance(clip, dict) or not isinstance(clip.get('id'), str):
            raise ValueError('采用镜头须声明 id')
        start, end = frame_range(clip.get('timeline_frame_range'))
        first, last = frame_range(clip.get('source_frame_range'))
        video = clip.get('source_video')
        url = file_url(video)
        links = [f'<a class="link" href="{url}">超分源片</a>']
        native = clip.get('native_video')
        if native:
            links.append(f'<a class="link" href="{file_url(native)}">原生采样与原声</a>')
        for record in clip.get('records', []):
            links.append(f'<a class="link" href="{file_url(record)}">{escape(record.get("label", "制作记录"))}</a>')
        reference = clip.get('reference')
        image = ''
        if reference:
            ref_url = file_url(reference)
            image = (f'<div><h4>历史单张参考图</h4><a href="{ref_url}"><img loading="lazy" '
                     f'src="{ref_url}" alt="{escape(clip["id"])} 的实际绑定参考图"></a>'
                     '<p class="small">静态参考正确不等于视频已通过。</p></div>')
        if 'input_references' in clip:
            image = input_reference_panel(clip, base, output.parent)
        else:
            image += '<p class="small">历史回执仅登记单张参考，完整输入未记录；须回查实际任务配置，不代表只绑定了这一张。</p>'
        voices = clip.get('voices', [])
        if not isinstance(voices, list):
            raise ValueError('voices 须为数组')
        voice_links = ', '.join(f'<a href="{file_url(v)}">{escape(v.get("label", "音色锚点"))}</a>' for v in voices)
        evidence = {'source_unit': clip.get('source_unit'), 'prompt_id': clip.get('prompt_id'),
                    'source_video_sha256': video.get('sha256'),
                    'native_video_sha256': (native or {}).get('sha256'),
                    'reference_sha256': (reference or {}).get('sha256')}
        cards.append(
            f'<article class="adoption-clip"><h3>{i:02} · {escape(clip["id"])} · {escape(clip.get("label", "采用镜头"))}</h3>'
            f'<p><strong>成片 {timecode(start)}—{timecode(end)}</strong> · '
            f'源帧 [{first}, {last}) · 源片 {timecode(first)}—{timecode(last)}</p>'
            f'<p>{escape(clip.get("note", ""))}</p>'
            f'<p class="small">生成时音色锚点：{voice_links or "无音色锚点"}。输入绑定不证明输出音色与轮次正确。</p>'
            f'<details><summary>查看本镜视频、参考图和来源记录</summary><div class="adoption-media">'
            f'<div><h4>超分源片（完整源片；采用范围见上）</h4><video controls preload="none" playsinline src="{url}"></video></div>{image}</div>'
            f'<div class="links">{"".join(links)}{folder_links(local_file(video["path"], base).parent, output.parent, f"adopted-{i}-folder")}</div>'
            f'<details><summary>任务身份与源指纹</summary><pre>{escape(json.dumps(evidence, ensure_ascii=False, indent=2))}</pre></details></details></article>'
        )
    asset_cards = []
    for i, asset in enumerate(assets):
        url = file_url(asset)
        kind = asset.get('kind')
        if kind not in ('script', 'subtitles', 'music', 'audio', 'record'):
            raise ValueError('未知采用附件类别')
        media = f'<audio controls preload="none" src="{url}"></audio>' if kind in ('music', 'audio') else ''
        asset_cards.append(f'<article><h3>{escape(asset.get("label", "采用附件"))}</h3><p>{escape(asset.get("note", ""))}</p>{media}'
                           f'<div class="links"><a class="link" href="{url}">打开原文件</a><a class="link" href="{url}" download>下载</a>'
                           f'{folder_links(local_file(asset["path"], base).parent, output.parent, f"adopted-asset-{i}")}</div></article>')
    return (f'<section id="adoption"><h2>本版采用素材与时间线</h2>'
            f'<p>与上方 {escape(final["version"])} 成片逐段对应：共 {len(clips)} 段。仅列本版实际采用来源，已弃用版本不在此列。</p>'
            '<details class="adoption-list"><summary>展开采用镜头、剪辑区间与绑定参考</summary>'
            f'<p class="small">时间码对应上方成片；源区间含起帧、不含结束帧，按 {fps:g} 帧/秒记录。源片播放器显示完整原片，可能包含未采用的头尾。</p>{"".join(cards)}</details>'
            '<details class="adoption-list"><summary>展开剧本、字幕、配乐、混音与生成时音色</summary>'
            f'<p class="small">音色文件是生成时输入锚点，并非后配对白。当前制作稿与任务文本共同留存；字幕定位和混音仍需实际视听核对。</p><div class="grid">{"".join(asset_cards)}</div></details></section>')


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
    review_mode = data.get('review_mode', 'complete')
    if review_mode not in ('complete', 'materials'):
        raise ValueError('review_mode 须为 complete 或 materials')
    if review_mode == 'complete':
        selected = [item for item in selected if item['category'] == 'final']
        if len(selected) > 1:
            raise ValueError('整集审阅只能选择一个当前完整候选')
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
            if category == 'video':
                media += input_reference_panel(item, manifest.parent, output.parent)
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
    adoption_html = render_adoption(data, [i for i in selected if i['category'] == 'final'], manifest.parent, output)
    if adoption_html:
        nav.append('<a href="#adoption">本版采用素材与时间线</a>')
    tasks = data.get('tasks', [])
    if not isinstance(tasks, list) or any(not isinstance(t, dict) or not all(isinstance(t.get(k), str) for k in ('name', 'status')) for t in tasks):
        raise ValueError('tasks 须为含 name/status 字符串的任务数组')
    task_html = ''
    if tasks:
        rows = ''.join(f'<tr><td>{escape(t["name"])}</td><td>{escape(t["status"])}</td><td>{escape(t.get("note", ""))}</td></tr>' for t in tasks)
        task_html = f'<section class="tasks"><h2>任务进度</h2><div class="table-wrap"><table><thead><tr><th>任务</th><th>实际状态</th><th>说明</th></tr></thead><tbody>{rows}</tbody></table></div></section>'
    related = data.get('related_pages', [])
    if not isinstance(related, list):
        raise ValueError('related_pages 须为数组')
    related_links = []
    for entry in related:
        if not isinstance(entry, dict) or not isinstance(entry.get('label'), str):
            raise ValueError('related_pages 须包含 label 和本地 path')
        target = local_file(entry.get('path'), manifest.parent)
        if target.suffix.lower() != '.html':
            raise ValueError('关联审阅入口须为本地 HTML')
        related_links.append(f'<a class="link" href="{link_to(target, output.parent)}">{escape(entry["label"])}</a>')
    values = {
        'TITLE': escape(data.get('title', '本集制作总览')),
        'SUMMARY': escape(data.get('summary', '尚未登记制作状态')),
        'UPDATED': escape(data.get('updated_at') or '尚未登记'),
        'RENDERED': escape(datetime.now().astimezone().isoformat(timespec='seconds')),
        'MANIFEST_LINK': f'<a class="link" href="{link_to(manifest, output.parent)}">查看素材清单</a>' + ''.join(related_links),
        'NAV': ''.join(nav), 'TASKS': task_html, 'ADOPTION': adoption_html,
        'SECTIONS': ''.join(sections) or ('<section class="empty">最新完整候选正在制作或导出，请查看任务进度；旧版未作为当前成片展示。</section>' if review_mode == 'complete' else '<section class="empty">尚无当前素材；生成或登记后更新本页。</section>'),
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
            json.dump({'title': f'{episode.name} · 制作总览', 'review_mode': 'complete', 'summary': '准备中', 'updated_at': '', 'items': [], 'tasks': []}, stream, ensure_ascii=False, indent=2)
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
