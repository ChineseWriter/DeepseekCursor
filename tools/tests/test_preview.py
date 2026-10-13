# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 BigFatFish contributors
"""预览图渲染测试：PNG 编码、网格布局、alpha 混合与采样规则。"""

from __future__ import annotations

import struct
import sys
import unittest
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bigfatfish.ani import Frame  # noqa: E402
from bigfatfish.preview import (  # noqa: E402
    BACKGROUND,
    SEPARATOR,
    MAX_SAMPLED_FRAMES,
    PreviewError,
    build_preview,
    encode_png,
    render,
    sample_frames,
)


def frame(width: int, height: int, rgba: bytes) -> Frame:
    return Frame(width=width, height=height, hotspot_x=0, hotspot_y=0, rgba=rgba)


def solid(width: int, height: int, color: tuple[int, int, int, int]) -> Frame:
    return frame(width, height, bytes(color) * (width * height))


def decode_png(blob: bytes) -> tuple[int, int, list[bytes]]:
    """只支持本模块写出的形式（8 位真彩、filter 0），够用来交叉验证。"""
    assert blob[:8] == b"\x89PNG\r\n\x1a\n"
    offset = 8
    width = height = 0
    data = b""
    while offset < len(blob):
        (length,) = struct.unpack_from(">I", blob, offset)
        tag = blob[offset + 4 : offset + 8]
        payload = blob[offset + 8 : offset + 8 + length]
        offset += 12 + length
        if tag == b"IHDR":
            width, height, depth, color_type = struct.unpack(">IIBB", payload[:10])
            assert (depth, color_type) == (8, 2)
        elif tag == b"IDAT":
            data += payload
    raw = zlib.decompress(data)
    stride = width * 3
    rows = []
    for y in range(height):
        chunk = raw[y * (stride + 1) : (y + 1) * (stride + 1)]
        assert chunk[0] == 0, "只写了 filter 0"
        rows.append(chunk[1:])
    return width, height, rows


class SampleFramesTests(unittest.TestCase):
    def test_short_animations_use_all_frames(self):
        frames = [solid(2, 2, (1, 2, 3, 255)) for _ in range(2)]
        self.assertEqual(sample_frames(frames), tuple(frames))

    def test_long_animations_use_first_middle_last(self):
        frames = [solid(2, 2, (i, 0, 0, 255)) for i in range(6)]
        picked = sample_frames(frames)
        self.assertEqual(len(picked), MAX_SAMPLED_FRAMES)
        self.assertEqual([f.rgba[0] for f in picked], [0, 3, 5])

    def test_empty_animation_is_rejected(self):
        with self.assertRaises(PreviewError):
            sample_frames([])


class RenderTests(unittest.TestCase):
    def test_grid_size_is_columns_by_rows(self):
        columns = [
            [solid(2, 2, (255, 0, 0, 255)), solid(2, 2, (0, 255, 0, 255))],
            [solid(2, 2, (0, 0, 255, 255))],
        ]
        width, height, rows = render(columns, cell=4)
        self.assertEqual((width, height), (8, 8))
        self.assertEqual(len(rows), 8)

    def test_background_and_separators_are_painted(self):
        # 透明帧留下底色（2x2 帧居中在 4x4 单元格里，左上角是留白）
        _w, _h, rows = render([[solid(2, 2, (255, 255, 255, 0))]], cell=4)
        self.assertEqual(rows[0][:3], bytes(BACKGROUND))
        # 两列时，第二列的起始像素是分隔线（[[帧],[帧]] 才是两列）
        transparent = solid(2, 2, (0, 0, 0, 0))
        _w, _h, wide = render([[transparent], [transparent]], cell=4)
        self.assertEqual(wide[1][4 * 3 : 4 * 3 + 3], bytes(SEPARATOR))
        self.assertEqual(wide[1][5 * 3 : 5 * 3 + 3], bytes(BACKGROUND))

    def test_transparent_pixels_leave_background(self):
        _w, _h, rows = render([[solid(4, 4, (255, 255, 255, 0))]], cell=4)
        self.assertEqual(rows[2][3 * 3 : 3 * 3 + 3], bytes(BACKGROUND))

    def test_opaque_pixel_is_written_and_centered(self):
        # 2x2 的白点放进 4x4 单元格：应落在偏移 (1,1)
        _w, _h, rows = render([[solid(2, 2, (255, 255, 255, 255))]], cell=4)
        self.assertEqual(rows[1][1 * 3 : 1 * 3 + 3], b"\xff\xff\xff")

    def test_frame_larger_than_cell_is_rejected(self):
        with self.assertRaises(PreviewError):
            render([[solid(8, 8, (1, 1, 1, 255))]], cell=4)

    def test_no_columns_is_rejected(self):
        with self.assertRaises(PreviewError):
            render([], cell=4)


class PngTests(unittest.TestCase):
    def test_encoded_png_decodes_to_the_same_pixels(self):
        columns = [[solid(2, 2, (10, 20, 30, 255))], [solid(2, 2, (40, 50, 60, 255))]]
        blob = build_preview(columns, cell=2)
        width, height, rows = decode_png(blob)
        self.assertEqual((width, height), (4, 2))
        self.assertEqual(rows[0][2 * 3 : 2 * 3 + 3], bytes((40, 50, 60)))

    def test_row_count_mismatch_is_rejected(self):
        with self.assertRaises(PreviewError):
            encode_png(2, 2, [bytearray(6)])

    def test_row_length_mismatch_is_rejected(self):
        with self.assertRaises(PreviewError):
            encode_png(2, 1, [bytearray(3)])

    def test_preview_is_deterministic(self):
        columns = [[solid(2, 2, (7, 8, 9, 128))]]
        self.assertEqual(build_preview(columns, cell=2), build_preview(columns, cell=2))


if __name__ == "__main__":
    unittest.main()
