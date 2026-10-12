# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 BigFatFish contributors
"""ani 解析测试：合成边界用例 + 真实素材结构断言。"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bigfatfish.ani import AniError, parse_ico, read_ani  # noqa: E402
from _ani_fixture import make_ani, make_dib, make_ico, solid_rgba  # noqa: E402

ASSETS = Path(__file__).resolve().parents[2] / "assets" / "BigFatFish"

#: install.inf 中声明的 11 个角色及其帧数（取自素材实测）
EXPECTED = {
    "pointer.ani": 23,
    "work.ani": 25,
    "busy.ani": 22,
    "cross.ani": 26,
    "text.ani": 24,
    "vert.ani": 24,
    "horz.ani": 23,
    "dgn1.ani": 19,
    "dgn2.ani": 23,
    "move.ani": 18,
    "link.ani": 21,
}


def one_frame_ani(**kwargs) -> bytes:
    rgba = solid_rgba(4, 4, (10, 20, 30, 255))
    dib = make_dib(4, 4, rgba)
    ico = make_ico([(4, 4, (1, 2), dib)])
    return make_ani([ico], **kwargs)


class ParseAniTests(unittest.TestCase):
    def test_single_frame_hotspot_and_size(self):
        cursor = read_ani(one_frame_ani())
        self.assertEqual(cursor.frame_count, 1)
        self.assertEqual(cursor.sizes, (4,))
        frame = cursor.steps[0].frames[0]
        self.assertEqual((frame.width, frame.height), (4, 4))
        self.assertEqual((frame.hotspot_x, frame.hotspot_y), (1, 2))
        self.assertEqual(cursor.steps[0].delay_ms, 100)  # rate=6 jiffies

    def test_opaque_pixels_roundtrip(self):
        frame = read_ani(one_frame_ani()).steps[0].frames[0]
        self.assertEqual(frame.rgba[:4], bytes((10, 20, 30, 255)))

    def test_zero_alpha_channel_falls_back_to_and_mask(self):
        """32bpp 但 alpha 全 0 时，透明度必须来自 AND 掩码（历史 ICO 常见坑）。"""
        rgba = solid_rgba(4, 4, (200, 100, 50, 255))
        dib = make_dib(4, 4, rgba, force_zero_alpha=True, mask_transparent=((0, 0), (3, 3)))
        ico = make_ico([(4, 4, (0, 0), dib)])
        frame = read_ani(make_ani([ico])).steps[0].frames[0]
        self.assertEqual(frame.rgba[3], 0, "掩码标记的像素应为透明")
        self.assertEqual(frame.rgba[4 * 1 + 3], 255, "未被掩码标记的像素应不透明")
        self.assertEqual(frame.rgba[4 * 15 + 3], 0)
        self.assertEqual(frame.rgba[4 * 1], 200, "颜色通道不应被改写")

    def test_rate_chunk_overrides_anih_rate(self):
        rgba = solid_rgba(4, 4, (0, 0, 0, 255))
        ico = make_ico([(4, 4, (0, 0), make_dib(4, 4, rgba))])
        cursor = read_ani(make_ani([ico, ico], rate=6, rate_chunk=[3, 12]))
        self.assertEqual([step.delay_ms for step in cursor.steps], [50, 200])

    def test_seq_chunk_reorders_frames(self):
        red = make_ico([(4, 4, (0, 0), make_dib(4, 4, solid_rgba(4, 4, (255, 0, 0, 255))))])
        blue = make_ico([(4, 4, (0, 0), make_dib(4, 4, solid_rgba(4, 4, (0, 0, 255, 255))))])
        cursor = read_ani(make_ani([red, blue], attrs=3, seq=[1, 0, 1]))
        self.assertEqual(cursor.frame_count, 3)
        self.assertEqual(cursor.steps[0].frames[0].rgba[2], 255)  # 蓝
        self.assertEqual(cursor.steps[1].frames[0].rgba[0], 255)  # 红

    def test_rejects_non_riff(self):
        with self.assertRaises(AniError):
            read_ani(b"not an ani file at all")

    def test_rejects_truncated_chunk(self):
        blob = one_frame_ani()
        with self.assertRaises(AniError):
            read_ani(blob[: len(blob) - 40])

    def test_rejects_lie_about_frame_count(self):
        data = one_frame_ani(declared_frames=5)
        with self.assertRaises(AniError):
            read_ani(data)

    def test_rejects_missing_af_icon(self):
        with self.assertRaises(AniError) as ctx:
            read_ani(one_frame_ani(attrs=0))
        self.assertIn("AF_ICON", str(ctx.exception))

    def test_rejects_hotspot_out_of_range(self):
        dib = make_dib(4, 4, solid_rgba(4, 4, (0, 0, 0, 255)))
        ico = make_ico([(4, 4, (9, 0), dib)])
        with self.assertRaises(AniError):
            read_ani(make_ani([ico]))

    def test_ico_without_entries_rejected(self):
        with self.assertRaises(AniError):
            parse_ico(b"\x00\x00\x02\x00\x00\x00")


    def test_rejects_absurd_nsteps_without_allocating(self):
        """anih.nSteps 来自不可信文件：必须在展开显示序列之前拒绝。

        否则一个几百字节的小文件（nSteps=0xFFFFFFFF）就能让进程分配数十亿元素而 OOM。
        """
        with self.assertRaises(AniError):
            read_ani(one_frame_ani(declared_steps=0xFFFFFFFF))

    def test_rejects_zero_nsteps(self):
        with self.assertRaises(AniError):
            read_ani(one_frame_ani(declared_steps=0))

    def test_ignores_bytes_after_declared_riff_size(self):
        """RIFF 头声明的范围之外不应被当成块继续解析。"""
        blob = one_frame_ani()
        cursor = read_ani(blob + b"\x00" * 64)
        self.assertEqual(cursor.frame_count, 1)


@unittest.skipUnless(ASSETS.is_dir(), "本地素材不存在（assets/ 不入库，属预期）")
class RealAssetTests(unittest.TestCase):
    def test_frame_counts_match_install_inf(self):
        for name, expected_frames in EXPECTED.items():
            with self.subTest(cursor=name):
                cursor = read_ani((ASSETS / name).read_bytes())
                self.assertEqual(cursor.frame_count, expected_frames)

    def test_every_cursor_has_native_32_48_64(self):
        for name in EXPECTED:
            with self.subTest(cursor=name):
                self.assertEqual(read_ani((ASSETS / name).read_bytes()).sizes, (32, 48, 64))

    def test_hotspots_inside_every_frame(self):
        for name in EXPECTED:
            cursor = read_ani((ASSETS / name).read_bytes())
            for index, step in enumerate(cursor.steps):
                for frame in step.frames:
                    with self.subTest(cursor=name, frame=index, size=frame.width):
                        self.assertTrue(0 <= frame.hotspot_x < frame.width)
                        self.assertTrue(0 <= frame.hotspot_y < frame.height)

    def test_all_frames_are_100ms(self):
        for name in EXPECTED:
            with self.subTest(cursor=name):
                cursor = read_ani((ASSETS / name).read_bytes())
                self.assertEqual({step.delay_ms for step in cursor.steps}, {100})

    def test_frames_are_not_fully_transparent(self):
        for name in EXPECTED:
            with self.subTest(cursor=name):
                frame = read_ani((ASSETS / name).read_bytes()).steps[0].frames[0]
                self.assertTrue(any(frame.rgba[3::4]), "首帧 alpha 全 0，解码很可能有误")


if __name__ == "__main__":
    unittest.main()
