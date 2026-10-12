# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 BigFatFish contributors
"""写出 XCursor 文件（``Xcur``），纯标准库。

布局（与 ``/usr/share/icons/*/cursors/`` 下的文件一致，已用 Adwaita 实测比对）：

* 文件头 16 字节：``Xcur`` / headerSize=16 / version=0x10000 / ntoc
* 目录项（TOC）每项 12 字节：type=0xFFFD0002 / subtype=标称尺寸 / 文件偏移
* 图像头 36 字节：size / type / subtype / version=1 / w / h / xhot / yhot / delay(ms)
* 像素：``w*h`` 个小端 u32，ARGB **预乘**（小端字节序即 B,G,R,A）

同一标称尺寸下出现多张图像即为动画帧，顺序由 TOC 顺序决定；TOC 先按标称尺寸
分组，组内保持帧序（Xcursor 加载器按 TOC 顺序收集同尺寸图像）。
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Sequence

from .ani import Frame

MAGIC = b"Xcur"
VERSION = 0x10000
HEADER_SIZE = 16
IMAGE_TYPE = 0xFFFD0002
IMAGE_HEADER_SIZE = 36
TOC_ENTRY_SIZE = 12


class XcursorError(ValueError):
    """XCursor 写出参数非法。"""


@dataclass(frozen=True)
class XImage:
    nominal: int
    width: int
    height: int
    hotspot_x: int
    hotspot_y: int
    delay_ms: int
    pixels_argb: bytes  # 小端 B,G,R,A，已预乘


def premultiply(rgba: bytes) -> bytes:
    """直通 alpha 的 RGBA8 -> XCursor 需要的预乘 BGRA8（小端 ARGB u32）。"""
    if len(rgba) % 4:
        raise XcursorError("RGBA 数据长度必须是 4 的倍数")

    out = bytearray(len(rgba))
    for i in range(0, len(rgba), 4):
        r = rgba[i]
        g = rgba[i + 1]
        b = rgba[i + 2]
        a = rgba[i + 3]
        if a == 0:
            continue  # 全零，预乘后仍是全零
        if a != 255:
            r = (r * a + 127) // 255
            g = (g * a + 127) // 255
            b = (b * a + 127) // 255
        out[i] = b
        out[i + 1] = g
        out[i + 2] = r
        out[i + 3] = a
    return bytes(out)


def image_from_frame(frame: Frame, nominal: int | None = None, delay_ms: int = 0) -> XImage:
    """把解析出的 :class:`~bigfatfish.ani.Frame` 转成 XCursor 图像。"""
    if nominal is None:
        nominal = max(frame.width, frame.height)
    if nominal <= 0:
        raise XcursorError(f"标称尺寸非法：{nominal}")
    if not (0 <= frame.hotspot_x < frame.width and 0 <= frame.hotspot_y < frame.height):
        raise XcursorError(
            f"热点 ({frame.hotspot_x}, {frame.hotspot_y}) 超出 {frame.width}x{frame.height}"
        )
    if not 0 <= delay_ms <= 0xFFFFFFFF:
        raise XcursorError(f"帧延迟超出 u32 范围：{delay_ms}")
    return XImage(
        nominal=nominal,
        width=frame.width,
        height=frame.height,
        hotspot_x=frame.hotspot_x,
        hotspot_y=frame.hotspot_y,
        delay_ms=delay_ms,
        pixels_argb=premultiply(frame.rgba),
    )


def build(images: Sequence[XImage]) -> bytes:
    """把一组图像打包成一个 XCursor 文件。"""
    if not images:
        raise XcursorError("没有可写出的图像")

    # 稳定排序：先按标称尺寸分组，组内保持传入的帧序
    ordered = sorted(images, key=lambda image: image.nominal)

    ntoc = len(ordered)
    position = HEADER_SIZE + ntoc * TOC_ENTRY_SIZE

    toc: list[tuple[int, int, int]] = []
    blobs: list[bytes] = []
    for image in ordered:
        expected = image.width * image.height * 4
        if len(image.pixels_argb) != expected:
            raise XcursorError(
                f"像素数据长度 {len(image.pixels_argb)} 与 {image.width}x{image.height} 不符"
            )
        if not (0 <= image.hotspot_x < image.width and 0 <= image.hotspot_y < image.height):
            raise XcursorError("热点超出图像范围")
        if not 0 < image.nominal <= 0xFFFF:
            raise XcursorError(f"标称尺寸非法：{image.nominal}")
        if not 0 <= image.delay_ms <= 0xFFFFFFFF:
            raise XcursorError(f"帧延迟超出 u32 范围：{image.delay_ms}")
        toc.append((IMAGE_TYPE, image.nominal, position))
        header = struct.pack(
            "<9I",
            IMAGE_HEADER_SIZE,
            IMAGE_TYPE,
            image.nominal,
            1,
            image.width,
            image.height,
            image.hotspot_x,
            image.hotspot_y,
            image.delay_ms,
        )
        blobs.append(header + image.pixels_argb)
        position += len(blobs[-1])

    out = bytearray()
    out += struct.pack("<4sIII", MAGIC, HEADER_SIZE, VERSION, ntoc)
    for entry_type, subtype, pos in toc:
        out += struct.pack("<III", entry_type, subtype, pos)
    for blob in blobs:
        out += blob
    return bytes(out)


def peek_header(blob: bytes) -> tuple[bytes, int, int, int]:
    """读取文件头，供写入后自检使用。"""
    if len(blob) < HEADER_SIZE:
        raise XcursorError("文件太短")
    return struct.unpack_from("<4sIII", blob, 0)
