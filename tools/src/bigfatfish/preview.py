# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 BigFatFish contributors
"""生成主题预览图（纯标准库，自己写 PNG）。

预览图**只由本仓库的主题渲染**：像素来自转换时解析出的素材帧（直通 alpha），
不引用上游图片、视频截图或外部工具，因此需要时随时可以重新生成：

    python -m bigfatfish build --all

布局是确定的：每个角色一列，列内是该角色被采样到的若干帧（首帧 / 中间帧 / 末帧），
因此同一主题每次生成的 PNG 完全一致。
"""

from __future__ import annotations

import struct
import zlib
from typing import Sequence

from .ani import Frame

#: 画布底色与列分隔线（深色在 GitHub 的浅色/深色两种主题下都清楚）
BACKGROUND = (38, 38, 38)
SEPARATOR = (64, 64, 64)

#: 每个角色采样几帧（多则取首/中/末，少则有多少用多少）
MAX_SAMPLED_FRAMES = 3

_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class PreviewError(ValueError):
    """预览图渲染参数非法。"""


def sample_frames(frames: Sequence[Frame]) -> tuple[Frame, ...]:
    """从动画帧里挑出用于预览的少数几帧：首帧、中间帧、末帧。"""
    if not frames:
        raise PreviewError("没有可渲染的帧")
    if len(frames) <= MAX_SAMPLED_FRAMES:
        return tuple(frames)
    indexes = [0, len(frames) // 2, len(frames) - 1]
    seen: list[Frame] = []
    for index in indexes:
        if frames[index] not in seen:
            seen.append(frames[index])
    return tuple(seen)


def render(columns: Sequence[Sequence[Frame]], cell: int) -> tuple[int, int, list[bytearray]]:
    """把每列的帧渲染成一张不透明 RGB 画布，返回 ``(宽, 高, 每行字节)``。"""
    if cell <= 0:
        raise PreviewError(f"单元格边长非法：{cell}")
    if not columns:
        raise PreviewError("没有要渲染的角色")

    rows_count = max(len(frames) for frames in columns)
    width = len(columns) * cell
    height = rows_count * cell

    canvas: list[bytearray] = []
    for y in range(height):
        row = bytearray(width * 3)
        row_color = SEPARATOR if y and y % cell == 0 else BACKGROUND
        for x in range(width):
            # 分隔线只画在单元格之间，画布最外圈不留边线
            r, g, b = SEPARATOR if x and x % cell == 0 else row_color
            row[x * 3] = r
            row[x * 3 + 1] = g
            row[x * 3 + 2] = b
        canvas.append(row)

    for column_index, frames in enumerate(columns):
        for row_index, frame in enumerate(frames):
            _blit(canvas, frame, column_index * cell, row_index * cell, cell)

    return width, height, canvas


def _blit(
    canvas: list[bytearray], frame: Frame, origin_x: int, origin_y: int, cell: int
) -> None:
    """把一帧按左上对齐（并居中）画进单元格；直通 alpha 与底色混合。"""
    width, height = frame.width, frame.height
    if width > cell or height > cell:
        raise PreviewError(f"帧 {width}x{height} 大于单元格 {cell}")
    pad_x = (cell - width) // 2
    pad_y = (cell - height) // 2
    rgba = frame.rgba

    for y in range(height):
        row = canvas[origin_y + pad_y + y]
        src = y * width * 4
        for x in range(width):
            r, g, b, a = rgba[src + 4 * x : src + 4 * x + 4]
            if a == 0:
                continue
            offset = (origin_x + pad_x + x) * 3
            if a == 255:
                row[offset], row[offset + 1], row[offset + 2] = r, g, b
            else:
                inverse = 255 - a
                row[offset] = (r * a + row[offset] * inverse + 127) // 255
                row[offset + 1] = (g * a + row[offset + 1] * inverse + 127) // 255
                row[offset + 2] = (b * a + row[offset + 2] * inverse + 127) // 255


def _chunk(tag: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + tag
        + payload
        + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)
    )


def encode_png(width: int, height: int, rows: Sequence[bytearray]) -> bytes:
    """把 RGB 行编码为 8 位真彩 PNG（无 alpha：底色已是不透明）。"""
    if len(rows) != height:
        raise PreviewError(f"行数 {len(rows)} 与高度 {height} 不符")
    for row in rows:
        if len(row) != width * 3:
            raise PreviewError(f"行长度 {len(row)} 与宽度 {width} 不符")

    raw = b"".join(b"\x00" + bytes(row) for row in rows)
    return (
        _PNG_SIGNATURE
        + _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + _chunk(b"IDAT", zlib.compress(raw, 9))
        + _chunk(b"IEND", b"")
    )


def build_preview(columns: Sequence[Sequence[Frame]], cell: int) -> bytes:
    width, height, rows = render(columns, cell)
    return encode_png(width, height, rows)
