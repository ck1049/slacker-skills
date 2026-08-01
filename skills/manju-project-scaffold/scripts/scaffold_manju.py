#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create long-form 漫剧 project directories."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT_SUBDIRS = [
    "db",
    "制作规则",
    "全局角色",
    "全局场景",
    "全局道具",
    "全局音频/音乐",
    "全局音频/音效",
    "全局音频/音色",
    "大纲/原文",
    "大纲/世界观",
    "大纲/分集规划",
    "正片",
]

EPISODE_SUBDIRS = [
    "分镜/分镜图",
    "分镜/分镜脚本",
    "分镜/分镜视频",
    "剧本",
    "场景",
    "角色",
    "道具",
    "音频/音乐",
    "音频/音效",
    "音频/音色",
]

SEASON_BLOCKS = ["01", "片头", "片尾"]


def safe_print(message: str) -> None:
    try:
        print(message)
    except UnicodeEncodeError:
        print("Created. Path contains non-ASCII characters.")


def ensure_dirs(base: Path, paths: list[str]) -> None:
    for item in paths:
        (base / item).mkdir(parents=True, exist_ok=True)


def create_episode_block(base: Path) -> None:
    ensure_dirs(base, EPISODE_SUBDIRS)


def create_project(name: str, base: Path) -> Path:
    root = (base / name).resolve()
    root.mkdir(parents=True, exist_ok=True)
    ensure_dirs(root, ROOT_SUBDIRS)
    create_season("第一季", root / "正片")
    safe_print(f"已创建工程目录: {root}")
    return root


def create_season(season_name: str, under: Path) -> Path:
    season_root = under.resolve() / season_name
    season_root.mkdir(parents=True, exist_ok=True)
    for block in SEASON_BLOCKS:
        create_episode_block(season_root / block)
    safe_print(f"已创建季目录: {season_root}")
    return season_root


def create_episodes(numbers: list[str], season_path: Path) -> None:
    season_root = season_path.resolve()
    season_root.mkdir(parents=True, exist_ok=True)
    for number in numbers:
        create_episode_block(season_root / number)
        safe_print(f"已创建集目录: {season_root / number}")


def main() -> None:
    parser = argparse.ArgumentParser(description="漫剧工程目录脚手架")
    sub = parser.add_subparsers(dest="command", required=True)

    project_cmd = sub.add_parser("project", help="创建新漫剧工程")
    project_cmd.add_argument("name", help="漫剧名")
    project_cmd.add_argument("--base", default=".", help="工程根目录的父路径")

    season_cmd = sub.add_parser("season", help="在正片下创建新一季")
    season_cmd.add_argument("season_name", help="季名，如 第二季")
    season_cmd.add_argument("--under", default=".", help="正片目录路径")

    episodes_cmd = sub.add_parser("episodes", help="在当前季下创建新剧集")
    episodes_cmd.add_argument("numbers", nargs="+", help="集号，如 02 03")
    episodes_cmd.add_argument("--season", default=".", help="当前季目录路径")

    args = parser.parse_args()
    cwd = Path.cwd()

    if args.command == "project":
        create_project(args.name, (cwd / args.base).resolve())
    elif args.command == "season":
        create_season(args.season_name, (cwd / args.under).resolve())
    elif args.command == "episodes":
        create_episodes(args.numbers, (cwd / args.season).resolve())
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
