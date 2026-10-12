# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 BigFatFish contributors
"""测试用：独立的 ANI/ICO 构造器（用于造边界用例）。

刻意不复用 ``src/bigfatfish`` 的任何代码，避免"用被测代码造测试数据"。
"""

from __future__ import annotations

import struct


def make_dib(
    width: int,
    height: int,
    rgba_topdown: bytes,
    *,
    force_zero_alpha: bool = False,
    mask_transparent: tuple[tuple[int, int], ...] = (),
) -> bytes:
    """构造 32bpp BI_RGB 的 ICO 用 DIB（高度为图像的 2 倍：XOR + AND）。"""
    assert len(rgba_topdown) == width * height * 4
    xor_row = width * 4
    xor = bytearray()
    for y in range(height - 1, -1, -1):  # DIB 自下而上
        for x in range(width):
            i = (y * width + x) * 4
            r, g, b, a = rgba_topdown[i : i + 4]
            xor += bytes((b, g, r, 0 if force_zero_alpha else a))

    mask_row = ((width + 31) // 32) * 4
    mask = bytearray(mask_row * height)
    for x, y in mask_transparent:
        src_y = height - 1 - y
        mask[src_y * mask_row + (x >> 3)] |= 0x80 >> (x & 7)

    header = struct.pack(
        "<IiiHHIIiiII",
        40,
        width,
        2 * height,
        1,
        32,
        0,
        len(xor) + len(mask),
        0,
        0,
        0,
        0,
    )
    return header + bytes(xor) + bytes(mask)


def make_ico(entries: list[tuple[int, int, tuple[int, int], bytes]]) -> bytes:
    """把 ``(w, h, (hotx, hoty), dib)`` 列表打成 CUR 容器。"""
    directory = bytearray()
    offset = 6 + 16 * len(entries)
    blobs = bytearray()
    for width, height, (hot_x, hot_y), dib in entries:
        directory += struct.pack(
            "<4B2H2I", width & 0xFF, height & 0xFF, 0, 0, hot_x, hot_y, len(dib), offset
        )
        offset += len(dib)
        blobs += dib
    return struct.pack("<3H", 0, 2, len(entries)) + bytes(directory) + bytes(blobs)


def make_ani(
    frames: list[bytes],
    *,
    rate: int = 6,
    attrs: int = 1,
    seq: list[int] | None = None,
    declared_frames: int | None = None,
    declared_steps: int | None = None,
    rate_chunk: list[int] | None = None,
) -> bytes:
    """构造 RIFF/ACON 容器。``frames`` 是若干 CUR 容器的字节。"""
    n_frames = len(frames) if declared_frames is None else declared_frames
    n_steps = (len(seq) if seq else len(frames)) if declared_steps is None else declared_steps
    anih = struct.pack("<9I", 36, n_frames, n_steps, 0, 0, 0, 0, rate, attrs)

    body = b"anih" + struct.pack("<I", len(anih)) + anih

    if rate_chunk is not None:
        payload = struct.pack(f"<{len(rate_chunk)}I", *rate_chunk)
        body += b"rate" + struct.pack("<I", len(payload)) + payload
    if seq is not None:
        payload = struct.pack(f"<{len(seq)}I", *seq)
        body += b"seq " + struct.pack("<I", len(payload)) + payload

    icon_chunks = bytearray()
    for frame in frames:
        icon_chunks += b"icon" + struct.pack("<I", len(frame)) + frame
        if len(frame) % 2:
            icon_chunks += b"\x00"
    body += b"LIST" + struct.pack("<I", 4 + len(icon_chunks)) + b"fram" + bytes(icon_chunks)

    return b"RIFF" + struct.pack("<I", 4 + len(body)) + b"ACON" + body


def solid_rgba(width: int, height: int, rgba: tuple[int, int, int, int]) -> bytes:
    return bytes(rgba) * (width * height)
