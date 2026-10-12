# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 BigFatFish contributors
"""命令行入口：``python -m bigfatfish build|list``。"""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .ani import AniError
from .theme import CURSORS, THEME_NAME, ThemeError, build_theme
from .xcursor import XcursorError

DEFAULT_ASSETS = "assets/BigFatFish"
DEFAULT_OUT = f"themes/{THEME_NAME}"


def _parse_sizes(text: str) -> tuple[int, ...]:
    try:
        sizes = tuple(sorted({int(part) for part in text.split(",") if part.strip()}))
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"尺寸列表非法：{text!r}") from exc
    if not sizes or any(size <= 0 for size in sizes):
        raise argparse.ArgumentTypeError("尺寸必须是正整数")
    return sizes


def _cmd_list(_args: argparse.Namespace) -> int:
    print(f"{'源文件':<14}{'XCursor 主名':<22}{'Windows 角色':<22}别名")
    for spec in CURSORS:
        print(
            f"{spec.source:<14}{spec.canonical:<22}{spec.windows_role:<22}"
            + ",".join(spec.aliases)
        )
    return 0


def _cmd_build(args: argparse.Namespace) -> int:
    report = build_theme(
        asset_dir=args.assets,
        out_dir=args.out,
        sizes=args.sizes,
        force=args.force,
    )
    for cursor in report.cursors:
        print(
            f"  {cursor.canonical:<22} <- {cursor.source:<12} "
            f"帧={cursor.frames:<3} 尺寸={','.join(map(str, cursor.sizes)):<12} "
            f"{cursor.bytes_written:>8} 字节  别名={len(cursor.aliases)}"
        )
    print(
        f"完成：{len(report.cursors)} 个光标，"
        f"{sum(len(c.aliases) for c in report.cursors)} 个别名，"
        f"共 {report.total_bytes} 字节 -> {report.out_dir}"
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
    build.add_argument("--assets", default=DEFAULT_ASSETS, help=f"素材目录（默认 {DEFAULT_ASSETS}）")
    build.add_argument("--out", default=DEFAULT_OUT, help=f"输出目录（默认 {DEFAULT_OUT}）")
    build.add_argument(
        "--sizes",
        type=_parse_sizes,
        default=None,
        help="只输出指定标称尺寸，逗号分隔（默认使用素材自带的全部尺寸）",
    )
    build.add_argument("--force", action="store_true", help="允许写入非本工具生成的已有目录")
    build.set_defaults(func=_cmd_build)

    listing = sub.add_parser("list", help="显示角色映射表")
    listing.set_defaults(func=_cmd_list)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (ThemeError, AniError, XcursorError, OSError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
