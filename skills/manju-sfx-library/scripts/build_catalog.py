"""Build an offline catalogue and 48 kHz editing copies from verified receipts."""
from __future__ import annotations

import argparse
import array
import csv
import hashlib
import json
import math
import re
import subprocess
import sys
import wave
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from runtime import add_arguments, settings, digest
from sfx import contained, ALLOWED_LICENSES
WORDS = {
    "footstep": "脚步 行走 落脚", "carpet": "地毯", "concrete": "水泥 硬地面",
    "grass": "草地", "snow": "雪地", "wood": "木头 木地板", "impact": "撞击 碰撞",
    "bell": "铃 金属鸣响", "generic": "通用", "glass": "玻璃", "metal": "金属",
    "mining": "凿击 挖掘", "plank": "木板", "plate": "板材", "punch": "拳击 打击",
    "soft": "柔软 闷响", "tin": "铁皮", "heavy": "重", "medium": "中", "light": "轻",
    "belt": "腰带", "handle": "拿取 摆弄", "book": "书本", "flip": "翻页",
    "close": "关闭", "open": "打开", "place": "放下", "chop": "劈砍",
    "cloth": "衣物 布料 摩擦", "creak": "吱呀", "door": "门", "draw": "拔出",
    "knife": "刀", "drop": "掉落", "leather": "皮革", "coins": "硬币 钱币",
    "small": "小", "slice": "挥动 切割", "click": "点击", "latch": "门闩 锁扣",
    "pot": "锅", "back": "返回", "bong": "咚 喜剧", "confirmation": "确认 成功",
    "error": "错误 失败", "glitch": "故障 电流", "maximize": "展开",
    "minimize": "收起", "pluck": "拨弦", "question": "疑问 困惑 喜剧",
    "scratch": "刮擦", "scroll": "滚动", "select": "选择", "switch": "切换 开关",
    "tick": "滴答", "toggle": "切换", "laser": "激光 科幻", "zap": "电击 科幻",
    "power": "能量", "up": "上升", "down": "下降", "high": "高音", "low": "低音",
    "tone": "电子 提示", "two": "双", "three": "三", "random": "随机",
    "pep": "活泼", "sound": "声音", "phase": "相位", "jump": "跳跃",
    "phaser": "科幻", "space": "太空", "trash": "杂音",
}


def label(path: Path, pack: str) -> tuple[str, list[str]]:
    words = re.sub(r"([a-z])([A-Z])", r"\1 \2", path.stem).lower()
    tokens = re.findall(r"[a-z]+", words)
    tags = list(dict.fromkeys(word for token in tokens for word in WORDS.get(token, token).split()))
    aliases = {
        ("door", "open"): ["开门"], ("door", "close"): ["关门"],
        ("book", "flip"): ["翻书"], ("book", "open"): ["打开书"],
        ("book", "close"): ["合书"], ("book", "place"): ["放书"],
        ("metal", "latch"): ["门锁"], ("punch",): ["拳头"],
        ("footstep", "wood"): ["木地板脚步"], ("confirmation",): ["提示音"],
    }
    for keys, values in aliases.items():
        if all(key in tokens for key in keys):
            tags.extend(values)
    if "footstep" in tokens:
        category = "脚步"
    elif pack == "interface-sounds":
        category = "界面与喜剧提示"
    elif pack == "digital-audio":
        category = "电子与科幻"
    elif "door" in tokens or "latch" in tokens or "creak" in tokens:
        category = "门与机关"
    elif "book" in tokens:
        category = "书本纸张"
    elif "cloth" in tokens or "leather" in tokens or "belt" in tokens:
        category = "衣物动作"
    elif "knife" in tokens or "chop" in tokens or "punch" in tokens:
        category = "动作打击"
    else:
        category = "物体碰撞与道具"
    return category, tags


def process(job: tuple[Path, Path, dict, dict]) -> dict:
    root, ffmpeg, record, file = job
    original = root / file["path"]
    if digest(original) != file["sha256"]:
        raise ValueError(f"Source hash mismatch: {original}")
    asset_id = ("KEN-" if record.get("source") == "Kenney" else "SFX-") + hashlib.sha256(file["path"].encode()).hexdigest()[:12]
    legacy = record.get("source") == "Kenney"
    target = contained(root, "剪辑素材/" + record["pack"] + "/" + (original.stem if legacy else asset_id) + ".wav")
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        subprocess.run([str(ffmpeg), "-hide_banner", "-loglevel", "error", "-nostdin", "-n",
                        "-i", str(original), "-vn", "-ar", "48000", "-ac", "2",
                        "-c:a", "pcm_s16le", str(target)], check=True, timeout=60, capture_output=True)
    with wave.open(str(target), "rb") as audio:
        frames, rate, channels = audio.getnframes(), audio.getframerate(), audio.getnchannels()
        if audio.getsampwidth() != 2 or rate != 48000 or channels != 2 or frames == 0:
            raise ValueError(f"Invalid editing copy: {target}")
        samples = array.array("h", audio.readframes(frames))
        if sys.byteorder != "little":
            samples.byteswap()
    peak = max(abs(sample) for sample in samples)
    if peak == 0:
        raise ValueError(f"Silent audio: {target}")
    category, tags = label(original, record["pack"])
    metadata = record.get("asset_metadata", {}).get(file["path"], {})
    category = metadata.get("category", category)
    tags = metadata.get("tags", tags)
    return {
        "id": asset_id, "name": metadata.get("name", original.stem), "category": category, "tags": tags,
        "tag_basis": "supplied_metadata_not_listening" if metadata else "source_filename_not_listening",
        "source_kind": record.get("source_kind", "downloaded"),
        "recording_metadata": metadata.get("recording_metadata", {}), "author": record["author"],
        "pack": record["pack"], "source_url": record["source_url"],
        "license": record["license"], "commercial_use": True, "attribution_required": False,
        "license_verified": True, "license_url": record["license_url"],
        "license_files": record["license_files"],
        "source_receipt": record["receipt_path"],
        "source_path": file["path"], "source_sha256": file["sha256"],
        "path": target.relative_to(root).as_posix(), "sha256": digest(target),
        "duration_seconds": frames / rate, "sample_rate": rate, "channels": channels,
        "encoding": "pcm_s16le", "peak_dbfs": round(20 * math.log10(peak / 32768), 2),
        "conversion": "FFmpeg: decode/resample to 48000 Hz stereo PCM16; no normalization or trimming",
        "technical_status": "decoded_nonempty_nonsilent", "listening_status": "unreviewed",
        "fit_status": "requires_scene_audition",
    }


def write_json(path: Path, value: object) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def build(root: Path, ffmpeg: Path) -> None:
    jobs = []
    for receipt in sorted((root / "来源与许可").rglob("receipt.json")):
        record = json.loads(receipt.read_text(encoding="utf-8"))
        record["receipt_path"] = receipt.relative_to(root).as_posix()
        if record["license"] not in ALLOWED_LICENSES or record["license_verified"] is not True:
            raise ValueError("Unverified license")
        if record["license"] == "LicenseRef-Self-Owned" and (record.get("source_kind") != "self_recorded" or record.get("rights_confirmed") is not True):
            raise ValueError("Missing recording ownership declaration")
        for file in record["files"]:
            path = (root / file["path"]).resolve()
            if not path.is_relative_to(root.resolve()) or digest(path) != file["sha256"]:
                raise ValueError(f"Evidence changed: {file['path']}")
            if path.suffix.lower() in {".ogg", ".wav", ".mp3", ".flac"} and path.stem.lower() != "preview":
                jobs.append((root, ffmpeg, record, file))
    with ThreadPoolExecutor(max_workers=4) as pool:
        assets = sorted(pool.map(process, jobs), key=lambda item: (item["category"], item["name"]))
    if len({item["id"] for item in assets}) != len(assets):
        raise ValueError("Duplicate asset IDs")
    if (root / "catalog.json").exists():
        previous = json.loads((root / "catalog.json").read_text(encoding="utf-8"))
        previous_by_id = {item["id"]: item for item in previous["assets"]}
        missing = set(previous_by_id) - {item["id"] for item in assets}
        if missing:
            raise ValueError(f"Rebuild would remove {len(missing)} assets; restore source receipts first")
        for item in assets:
            old = previous_by_id.get(item["id"])
            if old and old["sha256"] != item["sha256"]:
                raise ValueError(f"Editing copy changed: {item['id']}; use a new version")
            if old:
                for key in ("listening_status", "fit_status", "review_records"):
                    if key in old:
                        item[key] = old[key]
    catalogue = {"schema_version": 1, "created_at": datetime.now(timezone.utc).isoformat(),
                 "count": len(assets), "assets": assets}
    write_json(root / "catalog.json", catalogue)
    with (root / "素材清单.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["ID", "名称", "分类", "关键词", "秒", "许可", "作者", "来源", "路径", "SHA256", "听审状态"])
        for item in assets:
            writer.writerow([item["id"], item["name"], item["category"], " ".join(item["tags"]),
                             round(item["duration_seconds"], 3), item["license"], item["author"],
                             item["source_url"], item["path"], item["sha256"], item["listening_status"]])
    data = json.dumps(assets, ensure_ascii=False).replace("<", "\\u003c")
    page = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>漫剧公共音效库</title>
<meta name="viewport" content="width=device-width,initial-scale=1"><style>
body{font:16px system-ui;background:#111827;color:#e5e7eb;max-width:1200px;margin:32px auto;padding:0 20px}
h1{font-size:28px}p{color:#b9c6d8;line-height:1.7}input,select{font:inherit;padding:12px;background:#243247;color:white;border:1px solid #52627a;border-radius:8px;margin:5px}input{width:50%}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}.card{background:#1f2937;padding:18px;border-radius:12px;overflow-wrap:anywhere}.card h2{font-size:18px;margin-top:0}.meta{font-size:13px;color:#b9c6d8}audio{width:100%;margin:12px 0}a{color:#8dd9ee}button{background:#31516b;color:white;border:0;border-radius:5px;padding:7px;cursor:pointer}
</style><h1>漫剧公共音效库</h1><p>素材按条保存来源、许可或自有权利声明及 SHA-256。中文标签依据文件名或入库记录整理；用于成片前需结合实际镜头试听。48 kHz WAV 为剪辑副本，转换不增加原始录音质量。</p>
<input id="q" placeholder="搜索：脚步 木地板 / 翻页 / 关门 / 疑问" aria-label="搜索音效"><select id="category" aria-label="分类"><option value="">全部分类</option></select><p id="count"></p><div class="grid" id="results"></div>
<script>const assets=__DATA__;const q=document.querySelector('#q'),category=document.querySelector('#category');
for(const name of [...new Set(assets.map(x=>x.category))]){let o=document.createElement('option');o.value=name;o.textContent=name;category.append(o)}
function element(tag,text){let e=document.createElement(tag);if(text!==undefined)e.textContent=text;return e}
function render(){let terms=q.value.toLowerCase().trim().split(/\\s+/).filter(Boolean);let rows=assets.filter(x=>(!category.value||x.category===category.value)&&terms.every(t=>(x.name+' '+x.id+' '+x.category+' '+x.tags.join(' ')).toLowerCase().includes(t)));document.querySelector('#count').textContent=`${rows.length} / ${assets.length} 条 · 许可按条查看 · 场景适配需试听`;let grid=document.querySelector('#results');grid.replaceChildren();for(const x of rows){let card=element('article');card.className='card';card.append(element('h2',x.name));let info=element('div',x.category+' · '+x.license+' · '+x.listening_status+' · '+x.duration_seconds.toFixed(2)+' 秒 · '+x.id);info.className='meta';card.append(info,element('p',x.tags.join(' / ')));let audio=element('audio');audio.controls=true;audio.preload='none';audio.src=x.path;audio.onplay=()=>document.querySelectorAll('audio').forEach(a=>{if(a!==audio)a.pause()});card.append(audio);for(const [label,url] of [['WAV',x.path],['来源',x.source_url],['许可',x.license_files[0]]]){let a=element('a',label);a.href=url;a.target='_blank';a.rel='noopener';card.append(a,document.createTextNode('　'))}grid.append(card)}}q.oninput=render;category.onchange=render;render();</script></html>'''
    (root / "音效库.html").write_text(page.replace("__DATA__", data), encoding="utf-8")
    print(json.dumps({"count": len(assets), "categories": sorted({x["category"] for x in assets})}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    add_arguments(parser)
    args = parser.parse_args()
    root, ffmpeg = settings(args, require_ffmpeg=True)
    build(root, ffmpeg)
