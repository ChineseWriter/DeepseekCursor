# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 BigFatFish contributors
"""测试用：独立的 XCursor 读取器（按格式规范另写一份，用于交叉验证）。"""

from __future__ import annotations

import struct

IMAGE_TYPE = 0xFFFD0002


class RefParseError(AssertionError):
    pass


def parse(blob: bytes) -> dict:
    if len(blob) < 16:
        raise RefParseError("文件短于 16 字节")
    magic, header_size, version, ntoc = struct.unpack_from("<4sIII", blob, 0)
    if magic != b"Xcur":
        raise RefParseError(f"magic 不是 Xcur：{magic!r}")
    if header_size != 16:
        raise RefParseError(f"headerSize 应为 16，实为 {header_size}")
    if version != 0x10000:
        raise RefParseError(f"version 应为 1.0，实为 {version:#x}")
    if 16 + ntoc * 12 > len(blob):
        raise RefParseError("TOC 越界")

    toc = []
    images = []
    for index in range(ntoc):
        entry_type, subtype, position = struct.unpack_from("<III", blob, 16 + index * 12)
        if entry_type != IMAGE_TYPE:
            raise RefParseError(f"TOC[{index}] type 应为图像类型，实为 {entry_type:#x}")
        if position + 36 > len(blob):
            raise RefParseError(f"TOC[{index}] 偏移越界")
        size, img_type, img_subtype, img_version, width, height, xhot, yhot, delay = (
            struct.unpack_from("<9I", blob, position)
        )
        if size != 36:
            raise RefParseError(f"图像头长度应为 36，实为 {size}")
        if img_type != IMAGE_TYPE or img_version != 1:
            raise RefParseError("图像头 type/version 异常")
        if img_subtype != subtype:
            raise RefParseError("TOC subtype 与图像头不一致")
        pixels = blob[position + 36 : position + 36 + width * height * 4]
        if len(pixels) != width * height * 4:
            raise RefParseError("像素数据越界")
        toc.append((entry_type, subtype, position))
        images.append(
            {
                "nominal": subtype,
                "width": width,
                "height": height,
                "xhot": xhot,
                "yhot": yhot,
                "delay": delay,
                "pixels": pixels,
                "position": position,
            }
        )

    return {"ntoc": ntoc, "version": version, "toc": toc, "images": images}


def frames_of(parsed: dict, nominal: int) -> list[dict]:
    """按 TOC 顺序返回某标称尺寸下的全部动画帧。"""
    return [image for image in parsed["images"] if image["nominal"] == nominal]
