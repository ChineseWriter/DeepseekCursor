# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 BigFatFish contributors
"""把 .ani 素材组装成 XCursor 主题目录。

素材布局与角色映射由 :mod:`bigfatfish.catalog` 的 :class:`~bigfatfish.catalog.ThemeSpec`
描述；本模块只负责构建与护栏：不臆造素材里没有的角色、尺寸或动画。
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from . import preview, xcursor
from .ani import AnimatedCursor, Frame, read_ani_file
from .catalog import CursorSpec, ThemeSpec


class ThemeError(ValueError):
    """素材或输出目录不满足构建条件。"""


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
    name: str
    out_dir: Path
    cursors: tuple[CursorReport, ...]
    preview_bytes: int = 0
    preview_size: tuple[int, int] = (0, 0)

    @property
    def total_bytes(self) -> int:
        return sum(c.bytes_written for c in self.cursors)

    @property
    def alias_count(self) -> int:
        return sum(len(c.aliases) for c in self.cursors)


def _path_for(spec: ThemeSpec, assets_root: Path, cursor: CursorSpec, size: int | None) -> Path:
    return assets_root / spec.pattern.format(source=cursor.source, size=size)


def _frames_for(cursor: AnimatedCursor, sizes: tuple[int, ...]) -> list[tuple[Frame, int]]:
    """取出指定标称尺寸的 (帧, 延迟) 序列，保持素材里的帧序（不做任何缩放）。"""
    out: list[tuple[Frame, int]] = []
    for step in cursor.steps:
        for frame in step.frames:
            if max(frame.width, frame.height) in sizes:
                out.append((frame, step.delay_ms))
    return out


def _missing_assets(
    spec: ThemeSpec, assets_root: Path, sizes: tuple[int, ...]
) -> list[str]:
    """列出缺失的素材文件（相对 assets 根，便于给出可执行的提示）。"""
    missing: list[str] = []
    per_size = "{size}" in spec.pattern
    for cursor in spec.cursors:
        if per_size:
            for size in sizes:
                path = _path_for(spec, assets_root, cursor, size)
                if not path.is_file():
                    missing.append(f"{path.relative_to(assets_root)}")
        else:
            path = _path_for(spec, assets_root, cursor, None)
            if not path.is_file():
                missing.append(f"{path.relative_to(assets_root)}")
    return missing


def build_theme(
    spec: ThemeSpec,
    assets_root: str | Path,
    out_dir: str | Path,
    sizes: tuple[int, ...] | None = None,
    force: bool = False,
) -> BuildReport:
    """构建主题目录：``<out>/index.theme`` + ``<out>/cursors/<name>``。

    ``sizes`` 为 ``None`` 时使用主题自带的**入库档位**（合集为 32/48/64）；
    显式传入可在素材具备时额外构建 128/256 等更大档。任何档位都不做插值放大。
    """
    assets_root = Path(assets_root)
    out_dir = Path(out_dir)

    if not assets_root.is_dir():
        raise ThemeError(f"素材根目录不存在：{assets_root}")

    use_sizes = tuple(sorted(set(spec.sizes if sizes is None else sizes)))
    if not use_sizes:
        raise ThemeError("没有要输出的尺寸")

    missing = _missing_assets(spec, assets_root, use_sizes)
    if missing:
        shown = "、".join(missing[:3])
        more = f" 等共 {len(missing)} 个" if len(missing) > 3 else ""
        raise ThemeError(
            f"{spec.name}：素材缺少文件 {shown}{more}"
            "（更小的档位可能尚未按需拉取，见 docs/PROVENANCE.md）"
        )

    if out_dir.is_symlink():
        raise ThemeError(f"{out_dir} 是符号链接，拒绝写入（可能被重定向到别处）")
    if (
        out_dir.exists()
        and any(out_dir.iterdir())
        and not force
        and not _is_our_theme(out_dir, spec.name)
    ):
        raise ThemeError(f"{out_dir} 已存在且不是本工具生成的主题；确认覆盖请加 --force")

    per_size = "{size}" in spec.pattern
    preview_cell = max(use_sizes)

    # 先全部解析并编码，再统一落盘：任一素材有问题时不会留下新旧混合的半成品
    planned: list[tuple[CursorSpec, bytes, int, int, tuple[int, ...]]] = []
    preview_columns: list[tuple[Frame, ...]] = []
    for cursor in spec.cursors:
        _validate_name(cursor.canonical)

        pairs: list[tuple[Frame, int]] = []
        frame_counts: set[int] = set()
        if per_size:
            for size in use_sizes:
                parsed = read_ani_file(_path_for(spec, assets_root, cursor, size))
                frame_counts.add(len(parsed.steps))
                pairs.extend(_frames_for(parsed, (size,)))
        else:
            parsed = read_ani_file(_path_for(spec, assets_root, cursor, None))
            frame_counts.add(len(parsed.steps))
            pairs.extend(_frames_for(parsed, use_sizes))

        if len(frame_counts) != 1:
            # 各档帧数不同则动画无法逐帧对齐：宁可报错，也不静默凑一个长度
            raise ThemeError(
                f"{cursor.source}：各档帧数不一致 {sorted(frame_counts)}，动画无法对齐"
            )
        if not pairs:
            raise ThemeError(f"{cursor.source}：没有匹配尺寸 {use_sizes} 的帧")

        images = [
            xcursor.image_from_frame(frame, max(frame.width, frame.height), delay)
            for frame, delay in pairs
        ]
        written_sizes = tuple(sorted({image.nominal for image in images}))
        preview_columns.append(
            preview.sample_frames(
                [frame for frame, _delay in pairs if max(frame.width, frame.height) == preview_cell]
            )
        )
        planned.append(
            (
                cursor,
                xcursor.build(images),
                frame_counts.pop(),
                len(images),
                written_sizes,
            )
        )

    cursors_dir = out_dir / "cursors"
    if cursors_dir.is_symlink():
        raise ThemeError(f"{cursors_dir} 是符号链接，拒绝写入（可能被重定向到别处）")
    cursors_dir.mkdir(parents=True, exist_ok=True)

    reports: list[CursorReport] = []
    for cursor, blob, frames, image_count, written_sizes in planned:
        target = cursors_dir / cursor.canonical
        # 规范名必须是普通文件：若是软链，就地写入会以本进程身份覆写链接目标，
        # 而且随后的 _selfcheck 会沿同一路径回读，护栏形同虚设。
        if target.is_symlink():
            raise ThemeError(f"{target} 是符号链接，拒绝写入（可能被重定向到别处）")
        _write_atomic(target, blob)
        _selfcheck(target, blob, image_count)

        aliases = tuple(sorted(cursor.aliases))
        for alias in aliases:
            _validate_name(alias)
            link = cursors_dir / alias
            if link.is_symlink() or link.exists():
                link.unlink()
            os.symlink(cursor.canonical, link)  # 相对软链，主题目录可整体搬移

        reports.append(
            CursorReport(
                canonical=cursor.canonical,
                source=cursor.source,
                windows_role=cursor.windows_role,
                frames=frames,
                sizes=written_sizes,
                bytes_written=len(blob),
                aliases=aliases,
            )
        )

    # 生成型配置文件也要带 SPDX 头（AGENTS.md §8.2.1）；key file 允许 `#` 注释，
    # 已用 GLib 的 GKeyFile（GNOME 读 index.theme 的同一实现）实读验证。
    (out_dir / "index.theme").write_text(
        "# SPDX-License-Identifier: CC-BY-NC-SA-4.0\n"
        "# Copyright (C) 2026 BigFatFish contributors\n"
        "# 主题美术的来源与许可义务见同目录 ATTRIBUTION.md\n"
        "[Icon Theme]\n"
        f"Name={spec.name}\n"
        f"Comment={spec.comment}\n",
        encoding="utf-8",
    )

    # 预览图只由本主题自己的帧渲染，随构建一起重新生成（见 preview.py）
    preview_png = preview.build_preview(preview_columns, preview_cell)
    _write_atomic(out_dir / "preview.png", preview_png)

    return BuildReport(
        name=spec.name,
        out_dir=out_dir,
        cursors=tuple(reports),
        preview_bytes=len(preview_png),
        preview_size=(preview_cell * len(preview_columns), preview_cell * max(
            len(column) for column in preview_columns
        )),
    )


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


def _is_our_theme(out_dir: Path, name: str) -> bool:
    index = out_dir / "index.theme"
    if not index.is_file():
        return False
    try:
        return f"Name={name}" in index.read_text(encoding="utf-8")
    except OSError:
        return False
