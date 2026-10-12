# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 BigFatFish contributors
"""把 .ani 素材组装成一个 XCursor 主题目录。

角色映射来自素材自带的 ``install.inf``（Windows 光标角色 -> .ani 文件），
再翻译成 X11/XCursor 通用名字；未在 ``install.inf`` 中出现的角色一律不臆造。
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from . import xcursor
from .ani import read_ani_file

THEME_NAME = "BigFatFish"
THEME_COMMENT = "大肥鱼 / BigFatFish 全动态光标主题（由 .ani 转换）"


class ThemeError(ValueError):
    """素材或输出目录不满足构建条件。"""


@dataclass(frozen=True)
class CursorSpec:
    """一个角色的映射：源 .ani 文件 -> XCursor 主名 + 别名（软链）。"""

    source: str
    canonical: str
    windows_role: str
    aliases: tuple[str, ...] = ()


#: 依据 install.inf 的权威映射（Arrow/AppStarting/Wait/crosshair+precisionhair/
#: IBeam/SizeNS/SizeWE/SizeNWSE/SizeNESW/Grab+SizeAll/Hand）。
CURSORS: tuple[CursorSpec, ...] = (
    CursorSpec("pointer.ani", "left_ptr", "Arrow", ("default", "arrow", "top_left_arrow", "left-arrow")),
    CursorSpec("work.ani", "left_ptr_watch", "AppStarting", ("progress", "half-busy")),
    CursorSpec("busy.ani", "watch", "Wait", ("wait", "busy")),
    CursorSpec("cross.ani", "crosshair", "crosshair/precisionhair", ("cross", "tcross")),
    CursorSpec("text.ani", "text", "IBeam", ("xterm", "ibeam")),
    CursorSpec("move.ani", "fleur", "Grab/SizeAll", ("move", "size_all", "all-scroll", "grabbing")),
    CursorSpec("link.ani", "hand2", "Hand", ("pointer", "hand", "hand1", "pointing_hand")),
    CursorSpec(
        "vert.ani",
        "sb_v_double_arrow",
        "SizeNS",
        ("size_ver", "ns-resize", "v_double_arrow", "row-resize"),
    ),
    CursorSpec(
        "horz.ani",
        "sb_h_double_arrow",
        "SizeWE",
        ("size_hor", "ew-resize", "h_double_arrow", "col-resize"),
    ),
    CursorSpec(
        "dgn1.ani",
        "size_fdiag",
        "SizeNWSE",
        ("nwse-resize", "top_left_corner", "bottom_right_corner"),
    ),
    CursorSpec(
        "dgn2.ani",
        "size_bdiag",
        "SizeNESW",
        ("nesw-resize", "top_right_corner", "bottom_left_corner"),
    ),
)


@dataclass(frozen=True)
class CursorReport:
    canonical: str
    source: str
    windows_role: str
    frames: int
    sizes: tuple[int, ...]
    bytes_written: int
    aliases: tuple[str, ...]


@dataclass(frozen=True)
class BuildReport:
    out_dir: Path
    cursors: tuple[CursorReport, ...]

    @property
    def total_bytes(self) -> int:
        return sum(c.bytes_written for c in self.cursors)


def build_theme(
    asset_dir: str | Path,
    out_dir: str | Path,
    sizes: tuple[int, ...] | None = None,
    force: bool = False,
) -> BuildReport:
    """构建主题目录：``<out>/index.theme`` + ``<out>/cursors/<name>``。

    ``sizes`` 为 ``None`` 时使用素材自带的全部标称尺寸（本项目为 32/48/64），
    不做任何放大或缩小，避免引入伪造像素。
    """
    asset_dir = Path(asset_dir)
    out_dir = Path(out_dir)

    if not asset_dir.is_dir():
        raise ThemeError(f"素材目录不存在：{asset_dir}")

    missing = [spec.source for spec in CURSORS if not (asset_dir / spec.source).is_file()]
    if missing:
        raise ThemeError("素材目录缺少文件：" + ", ".join(missing))

    if out_dir.is_symlink():
        raise ThemeError(f"{out_dir} 是符号链接，拒绝写入（可能被重定向到别处）")
    if out_dir.exists() and any(out_dir.iterdir()) and not force and not _is_our_theme(out_dir):
        raise ThemeError(f"{out_dir} 已存在且不是本工具生成的主题；确认覆盖请加 --force")

    # 先全部解析并编码，再统一落盘：任一素材有问题时不会留下新旧混合的半成品
    planned: list[tuple[CursorSpec, bytes, int, int, tuple[int, ...]]] = []
    for spec in CURSORS:
        _validate_name(spec.canonical)
        cursor = read_ani_file(asset_dir / spec.source)

        images: list[xcursor.XImage] = []
        written_sizes: set[int] = set()
        for step in cursor.steps:
            for frame in step.frames:
                nominal = max(frame.width, frame.height)
                if sizes is not None and nominal not in sizes:
                    continue
                images.append(xcursor.image_from_frame(frame, nominal, step.delay_ms))
                written_sizes.add(nominal)
        if not images:
            raise ThemeError(f"{spec.source}：没有匹配尺寸 {sizes} 的帧")

        planned.append(
            (
                spec,
                xcursor.build(images),
                len(cursor.steps),
                len(images),
                tuple(sorted(written_sizes)),
            )
        )

    cursors_dir = out_dir / "cursors"
    if cursors_dir.is_symlink():
        raise ThemeError(f"{cursors_dir} 是符号链接，拒绝写入（可能被重定向到别处）")
    cursors_dir.mkdir(parents=True, exist_ok=True)

    reports: list[CursorReport] = []
    for spec, blob, frames, image_count, written_sizes in planned:
        target = cursors_dir / spec.canonical
        # 规范名必须是普通文件：若是软链，就地写入会以本进程身份覆写链接目标，
        # 而且随后的 _selfcheck 会沿同一路径回读，护栏形同虚设。
        if target.is_symlink():
            raise ThemeError(f"{target} 是符号链接，拒绝写入（可能被重定向到别处）")
        _write_atomic(target, blob)
        _selfcheck(target, blob, image_count)

        aliases = tuple(sorted(spec.aliases))
        for alias in aliases:
            _validate_name(alias)
            link = cursors_dir / alias
            if link.is_symlink() or link.exists():
                link.unlink()
            os.symlink(spec.canonical, link)  # 相对软链，主题目录可整体搬移

        reports.append(
            CursorReport(
                canonical=spec.canonical,
                source=spec.source,
                windows_role=spec.windows_role,
                frames=frames,
                sizes=written_sizes,
                bytes_written=len(blob),
                aliases=aliases,
            )
        )

    (out_dir / "index.theme").write_text(
        "[Icon Theme]\n"
        f"Name={THEME_NAME}\n"
        f"Comment={THEME_COMMENT}\n",
        encoding="utf-8",
    )

    return BuildReport(out_dir=out_dir, cursors=tuple(reports))


def _validate_name(name: str) -> None:
    if not name or "/" in name or name in {".", ".."}:
        raise ThemeError(f"非法的光标名：{name!r}")


def _write_atomic(path: Path, data: bytes) -> None:
    """同目录临时文件 + ``os.replace``：不跟随符号链接，也不会留下半截文件。"""
    tmp = path.with_name(f".{path.name}.tmp")
    try:
        tmp.write_bytes(data)
        os.replace(tmp, path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def _selfcheck(path: Path, expected: bytes, images: int) -> None:
    """写完立刻回读文件头，确保落盘内容就是刚生成的字节。"""
    actual = path.read_bytes()
    if actual != expected:
        raise ThemeError(f"写入校验失败（内容不一致）：{path}")
    magic, header_size, version, ntoc = xcursor.peek_header(actual)
    if magic != xcursor.MAGIC:
        raise ThemeError(f"写入校验失败（magic={magic!r}）：{path}")
    if header_size != xcursor.HEADER_SIZE or version != xcursor.VERSION:
        raise ThemeError(f"写入校验失败（头字段异常）：{path}")
    if ntoc != images:
        raise ThemeError(f"写入校验失败（TOC {ntoc} != 图像 {images}）：{path}")


def _is_our_theme(out_dir: Path) -> bool:
    index = out_dir / "index.theme"
    if not index.is_file():
        return False
    try:
        return f"Name={THEME_NAME}" in index.read_text(encoding="utf-8")
    except OSError:
        return False
