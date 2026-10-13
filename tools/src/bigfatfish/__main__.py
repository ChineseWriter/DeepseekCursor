# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 BigFatFish contributors
"""命令行入口：``python -m bigfatfish build|list|themes``。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .ani import AniError
from .catalog import THEMES, ThemeSpec, theme_by_name, theme_names
from .theme import BuildReport, ThemeError, build_theme
from .xcursor import XcursorError

#: 本工具位于 <repo>/tools/ 下。默认路径按仓库根目录解析，
#: 这样在任何工作目录下运行都不需要额外参数（仍可用 --assets/--out 覆盖）。
_REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ASSETS = str(_REPO_ROOT / "assets")


def _parse_sizes(text: str) -> tuple[int, ...]:
    try:
        sizes = tuple(sorted({int(part) for part in text.split(",") if part.strip()}))
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"尺寸列表非法：{text!r}") from exc
    if not sizes or any(size <= 0 for size in sizes):
        raise argparse.ArgumentTypeError("尺寸必须是正整数")
    return sizes


def _pick_theme(name: str) -> ThemeSpec:
    try:
        return theme_by_name(name)
    except KeyError:
        raise ThemeError(
            f"未知主题 {name!r}；可用：" + "、".join(theme_names())
        ) from None


def _print_report(report: BuildReport) -> None:
    for cursor in report.cursors:
        print(
            f"  {cursor.canonical:<18} <- {cursor.source:<16} "
            f"帧={cursor.frames:<3} 尺寸={','.join(map(str, cursor.sizes)):<12} "
            f"{cursor.bytes_written:>8} 字节  别名={len(cursor.aliases)}"
        )
    print(
        f"完成：{report.name} —— {len(report.cursors)} 个光标，"
        f"{report.alias_count} 个别名，共 {report.total_bytes} 字节 -> {report.out_dir}"
    )
    if report.preview_bytes:
        width, height = report.preview_size
        print(f"      预览图 preview.png：{width}x{height}，{report.preview_bytes} 字节")


def _cmd_themes(_args: argparse.Namespace) -> int:
    print(f"{'主题':<16}{'入库档位':<12}{'角色数':<8}{'许可':<16}来源")
    for spec in THEMES:
        source = f"https://github.com/{spec.repo}" if spec.repo else f"B 站 {spec.video}"
        print(
            f"{spec.name:<16}"
            f"{','.join(map(str, spec.sizes)):<12}"
            f"{len(spec.cursors):<8}"
            f"{spec.license_id:<16}"
            f"{source}"
        )
    return 0


def _cmd_list(args: argparse.Namespace) -> int:
    specs = [_pick_theme(args.theme)] if args.theme else list(THEMES)
    for spec in specs:
        source = f"https://github.com/{spec.repo}" if spec.repo else f"B 站 {spec.video}"
        print(f"== {spec.name}  （{spec.title}；{source}）")
        print(f"{'源文件':<18}{'XCursor 主名':<18}{'Windows 角色':<22}别名")
        for cursor in spec.cursors:
            print(
                f"{cursor.source:<18}{cursor.canonical:<18}{cursor.windows_role:<22}"
                + ",".join(cursor.aliases)
            )
    return 0


def _cmd_build(args: argparse.Namespace) -> int:
    specs = list(THEMES) if args.all else [_pick_theme(args.theme)]
    if args.out and len(specs) != 1:
        raise ThemeError("--out 只能与单个 --theme 一起使用")

    reports: list[BuildReport] = []
    for spec in specs:
        out_dir = Path(args.out) if args.out else _REPO_ROOT / spec.out_dir
        reports.append(
            build_theme(
                spec,
                assets_root=args.assets,
                out_dir=out_dir,
                sizes=args.sizes,
                force=args.force,
            )
        )
        _print_report(reports[-1])
    if len(reports) > 1:
        print(
            f"合计：{len(reports)} 个主题，"
            f"{sum(len(r.cursors) for r in reports)} 个光标，"
            f"{sum(r.total_bytes for r in reports)} 字节"
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bigfatfish",
        description="把 Windows 动画光标包 (.ani) 转换为 XCursor 主题",
    )
    parser.add_argument("--version", action="version", version=f"bigfatfish {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="构建 XCursor 主题")
    pick = build.add_mutually_exclusive_group(required=True)
    pick.add_argument("--theme", help="只构建指定主题")
    pick.add_argument("--all", action="store_true", help="构建全部主题")
    build.add_argument("--assets", default=DEFAULT_ASSETS, help=f"素材根目录（默认 {DEFAULT_ASSETS}）")
    build.add_argument("--out", default=None, help="输出目录（仅限单个 --theme；默认 <仓库>/<主题目录>）")
    build.add_argument(
        "--sizes",
        type=_parse_sizes,
        default=None,
        help="只输出指定标称尺寸，逗号分隔（默认使用该主题的入库档位）",
    )
    build.add_argument("--force", action="store_true", help="允许写入非本工具生成的已有目录")
    build.set_defaults(func=_cmd_build)

    listing = sub.add_parser("list", help="显示角色映射表")
    listing.add_argument("--theme", default=None, help="只看指定主题（默认全部）")
    listing.set_defaults(func=_cmd_list)

    themes = sub.add_parser("themes", help="列出全部主题")
    themes.set_defaults(func=_cmd_themes)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (ThemeError, AniError, XcursorError, OSError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
