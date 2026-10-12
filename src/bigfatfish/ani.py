# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 BigFatFish contributors
"""解析 Windows 动画光标 (.ani) 及其 ICO/CUR 帧。纯标准库。

格式要点（实测自本项目素材，见 docs/PROVENANCE.md）：

* 容器是 RIFF/ACON，内含 ``anih``（头）、可选 ``rate``（每步时长）、
  可选 ``seq ``（显示顺序），以及 ``LIST fram`` 里的多个 ``icon`` 块。
* ``anih.bfAttributes`` 置 ``AF_ICON`` 时，每个 ``icon`` 块是一个完整的多分辨率
  ICO/CUR 文件（本项目素材每帧含 32/48/64 三档）。
* CUR 的热点存放在目录项里：``wXHotspot``/``wYHotspot`` 覆盖 ICO 的
  ``wPlanes``/``wBitCount`` 两个字段。
* 帧像素是未压缩 DIB（``BI_RGB``），在 ICO 中高度为图像的两倍：
  上半是 XOR 位图，下半是 1bpp 的 AND 掩码。
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path

#: anih.bfAttributes 位：帧数据是 ICO/CUR 格式
AF_ICON = 0x1
#: anih.bfAttributes 位：帧按 seq 块给出的顺序显示
AF_SEQUENCE = 0x2

#: .ani 的速率单位是 jiffies（1/60 秒）
JIFFIES_PER_SECOND = 60

_ANIH_FIELDS = 9
_ICONDIR_SIZE = 6
_ICONDIRENTRY_SIZE = 16
_DIB_HEADER_SIZE = 40


class AniError(ValueError):
    """素材不是受支持的 .ani / ICO 结构。"""


@dataclass(frozen=True)
class Frame:
    """一帧在某分辨率下的位图。

    ``rgba`` 为自顶向下、**直通**（非预乘）alpha 的 RGBA8 字节串。
    """

    width: int
    height: int
    hotspot_x: int
    hotspot_y: int
    rgba: bytes


@dataclass(frozen=True)
class Step:
    """一个显示步骤：同一步骤包含同一帧的各分辨率版本。"""

    delay_ms: int
    frames: tuple[Frame, ...]


@dataclass(frozen=True)
class AnimatedCursor:
    steps: tuple[Step, ...]

    @property
    def sizes(self) -> tuple[int, ...]:
        """素材中出现的全部标称尺寸（升序、去重）。"""
        seen = {max(f.width, f.height) for step in self.steps for f in step.frames}
        return tuple(sorted(seen))

    @property
    def frame_count(self) -> int:
        return len(self.steps)


def _iter_chunks(buf: bytes, start: int, end: int):
    """遍历 ``[start, end)`` 内的 RIFF 块，产出 ``(id, payload_start, payload_end)``。"""
    off = start
    while off + 8 <= end:
        cid = buf[off : off + 4]
        size = struct.unpack_from("<I", buf, off + 4)[0]
        payload_start = off + 8
        payload_end = payload_start + size
        if payload_end > len(buf):
            raise AniError(f"块 {cid!r} 长度越界（声明 {size} 字节）")
        yield cid, payload_start, payload_end
        off = payload_end + (size & 1)  # 块按偶数字节对齐


def _u32_array(buf: bytes, start: int, end: int) -> list[int]:
    count = (end - start) // 4
    if count == 0:
        return []
    return list(struct.unpack_from(f"<{count}I", buf, start))


def read_ani(data: bytes) -> AnimatedCursor:
    """解析 .ani 字节串。结构非法时抛 :class:`AniError`。"""
    if len(data) < 12 or data[:4] != b"RIFF" or data[8:12] != b"ACON":
        raise AniError("不是 RIFF/ACON 格式的 .ani")

    declared = struct.unpack_from("<I", data, 4)[0]
    if declared + 8 > len(data):
        raise AniError("RIFF 头声明的长度超过文件实际大小")

    anih: tuple[int, ...] | None = None
    rates: list[int] = []
    seq: list[int] = []
    icons: list[bytes] = []

    for cid, start, end in _iter_chunks(data, 12, len(data)):
        if cid == b"anih":
            if end - start < _ANIH_FIELDS * 4:
                raise AniError("anih 块不足 36 字节")
            anih = struct.unpack_from(f"<{_ANIH_FIELDS}I", data, start)
        elif cid == b"rate":
            rates = _u32_array(data, start, end)
        elif cid == b"seq ":
            seq = _u32_array(data, start, end)
        elif cid == b"LIST" and data[start : start + 4] == b"fram":
            for sub_id, sub_start, sub_end in _iter_chunks(data, start + 4, end):
                if sub_id == b"icon":
                    icons.append(data[sub_start:sub_end])

    if anih is None:
        raise AniError("缺少 anih 头块")

    _cb, n_frames, n_steps, _w, _h, _bpp, _planes, disp_rate, attrs = anih

    if not attrs & AF_ICON:
        raise AniError("anih.bfAttributes 未置 AF_ICON：帧数据不是 ICO/CUR，暂不支持")
    if n_frames != len(icons):
        raise AniError(f"anih 声明 {n_frames} 帧，实际找到 {len(icons)} 个 icon 块")
    if n_frames == 0:
        raise AniError("素材没有任何帧")

    frames = [parse_ico(blob) for blob in icons]

    order = seq if seq else list(range(n_steps))
    if len(order) != n_steps:
        raise AniError(f"显示顺序长度 {len(order)} 与 anih.nSteps={n_steps} 不一致")

    steps: list[Step] = []
    for index, frame_index in enumerate(order):
        if not 0 <= frame_index < len(frames):
            raise AniError(f"seq 引用了不存在的帧 {frame_index}")
        jiffies = rates[index] if index < len(rates) else disp_rate
        steps.append(
            Step(
                delay_ms=round(jiffies * 1000 / JIFFIES_PER_SECOND),
                frames=frames[frame_index],
            )
        )

    return AnimatedCursor(steps=tuple(steps))


def read_ani_file(path: str | Path) -> AnimatedCursor:
    return read_ani(Path(path).read_bytes())


def parse_ico(data: bytes) -> tuple[Frame, ...]:
    """解析一个 ICO/CUR 容器，返回其中每个目录项对应的 :class:`Frame`。"""
    if len(data) < _ICONDIR_SIZE:
        raise AniError("ICO 头不足 6 字节")

    reserved, image_type, count = struct.unpack_from("<3H", data, 0)
    if reserved != 0 or image_type not in (1, 2):
        raise AniError(f"不是 ICO/CUR（reserved={reserved} type={image_type}）")
    if count == 0:
        raise AniError("ICO 目录项数量为 0")

    frames: list[Frame] = []
    for index in range(count):
        base = _ICONDIR_SIZE + index * _ICONDIRENTRY_SIZE
        if base + _ICONDIRENTRY_SIZE > len(data):
            raise AniError("ICO 目录项越界")

        width, height, _ncolors, _reserved, hot_x, hot_y, size, offset = struct.unpack_from(
            "<4B2H2I", data, base
        )
        if image_type == 1:  # .ico 没有热点概念
            hot_x = hot_y = 0

        width = width or 256
        height = height or 256

        blob = data[offset : offset + size]
        if len(blob) != size:
            raise AniError("ICO 图像数据越界")
        if blob[:8] == b"\x89PNG\r\n\x1a\n":
            raise AniError("暂不支持 PNG 压缩的 ICO 帧（本项目素材为 BI_RGB DIB）")

        rgba, real_w, real_h = _decode_dib(blob)
        if (real_w, real_h) != (width, height):
            # 目录项声明的尺寸不可信时，以 DIB 头为准
            width, height = real_w, real_h
        if not (0 <= hot_x < width and 0 <= hot_y < height):
            raise AniError(f"热点 ({hot_x}, {hot_y}) 超出 {width}x{height}")

        frames.append(
            Frame(width=width, height=height, hotspot_x=hot_x, hotspot_y=hot_y, rgba=rgba)
        )

    return tuple(frames)


def _decode_dib(dib: bytes) -> tuple[bytes, int, int]:
    """把未压缩 DIB 解码为自顶向下的直通 alpha RGBA8，返回 ``(rgba, w, h)``。"""
    if len(dib) < _DIB_HEADER_SIZE:
        raise AniError("DIB 头不足 40 字节")

    header_size, width, height, _planes, bpp, compression = struct.unpack_from("<IiiHHI", dib, 0)

    if header_size < _DIB_HEADER_SIZE:
        raise AniError(f"不支持的 DIB 头长度 {header_size}")
    if compression != 0:
        raise AniError(f"仅支持 BI_RGB 未压缩 DIB，实际 compression={compression}")
    if bpp not in (24, 32):
        raise AniError(f"仅支持 24/32bpp，实际 {bpp}bpp")
    if width <= 0 or height == 0:
        raise AniError("DIB 尺寸非法")

    total_height = abs(height)
    bottoms_up = height > 0
    row_stride = ((width * bpp + 31) // 32) * 4
    mask_stride = ((width + 31) // 32) * 4
    payload = len(dib) - header_size

    # ICO 约定：高度是图像的两倍（XOR 位图 + AND 掩码）；纯 DIB 则高度即图像高度。
    xor_height = None
    if total_height % 2 == 0:
        candidate = total_height // 2
        if row_stride * candidate + mask_stride * candidate <= payload:
            xor_height = candidate
    if xor_height is None:
        if row_stride * total_height <= payload:
            xor_height = total_height
        else:
            raise AniError("DIB 像素数据长度不足")

    xor = dib[header_size : header_size + row_stride * xor_height]
    mask: bytes | None = None
    mask_start = header_size + row_stride * xor_height
    if mask_start + mask_stride * xor_height <= len(dib):
        mask = dib[mask_start : mask_start + mask_stride * xor_height]

    pixels = bytearray(width * xor_height * 4)
    has_alpha = False
    for y in range(xor_height):
        src_y = (xor_height - 1 - y) if bottoms_up else y
        src = src_y * row_stride
        dst = y * width * 4
        if bpp == 32:
            for x in range(width):
                b, g, r, a = xor[src + 4 * x : src + 4 * x + 4]
                has_alpha = has_alpha or a != 0
                o = dst + 4 * x
                pixels[o] = r
                pixels[o + 1] = g
                pixels[o + 2] = b
                pixels[o + 3] = a
        else:
            for x in range(width):
                b, g, r = xor[src + 3 * x : src + 3 * x + 3]
                o = dst + 4 * x
                pixels[o] = r
                pixels[o + 1] = g
                pixels[o + 2] = b
                pixels[o + 3] = 255

    # 32bpp 但 alpha 通道全为 0（历史遗留 ICO 很常见）：透明度只能来自 AND 掩码。
    if not has_alpha:
        pixels[3::4] = b"\xff" * (width * xor_height)

    if mask is not None:
        for y in range(xor_height):
            src_y = (xor_height - 1 - y) if bottoms_up else y
            src = src_y * mask_stride
            dst = y * width * 4
            for x in range(width):
                if (mask[src + (x >> 3)] >> (7 - (x & 7))) & 1:
                    pixels[dst + 4 * x + 3] = 0

    return bytes(pixels), width, xor_height
