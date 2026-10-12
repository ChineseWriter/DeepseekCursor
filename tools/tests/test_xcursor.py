# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 BigFatFish contributors
"""xcursor 写出测试：用独立读取器交叉验证，并与系统自带主题比对格式。"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bigfatfish.ani import Frame  # noqa: E402
from bigfatfish.xcursor import (  # noqa: E402
    IMAGE_HEADER_SIZE,
    IMAGE_TYPE,
    VERSION,
    XcursorError,
    build,
    image_from_frame,
    premultiply,
)
from _xcur_ref import RefParseError, frames_of, parse  # noqa: E402

REFERENCE = Path("/usr/share/icons/Adwaita/cursors/left_ptr")


def solid_frame(width: int, height: int, hotspot=(0, 0), rgba=(255, 255, 255, 255)) -> Frame:
    return Frame(
        width=width,
        height=height,
        hotspot_x=hotspot[0],
        hotspot_y=hotspot[1],
        rgba=bytes(rgba) * (width * height),
    )


class PremultiplyTests(unittest.TestCase):
    def test_half_alpha_darkens_rgb(self):
        # 直通 (255,0,0,128) -> 预乘 r=128；小端存放顺序为 B,G,R,A
        self.assertEqual(premultiply(bytes((255, 0, 0, 128))), bytes((0, 0, 128, 128)))

    def test_transparent_pixel_stays_zero(self):
        self.assertEqual(premultiply(bytes((255, 255, 255, 0))), bytes((0, 0, 0, 0)))

    def test_opaque_pixel_keeps_colour_order(self):
        self.assertEqual(premultiply(bytes((1, 2, 3, 255))), bytes((3, 2, 1, 255)))

    def test_rejects_bad_length(self):
        with self.assertRaises(XcursorError):
            premultiply(b"\x00\x01\x02")


class BuildTests(unittest.TestCase):
    def test_roundtrip_through_reference_parser(self):
        images = [
            image_from_frame(solid_frame(32, 32, (3, 1), (255, 0, 0, 255)), 32, 100),
            image_from_frame(solid_frame(32, 32, (3, 1), (0, 255, 0, 255)), 32, 100),
            image_from_frame(solid_frame(48, 48, (4, 1), (0, 0, 255, 255)), 48, 100),
        ]
        parsed = parse(build(images))

        self.assertEqual(parsed["ntoc"], 3)
        self.assertEqual(parsed["version"], VERSION)
        self.assertEqual([i["nominal"] for i in parsed["images"]], [32, 32, 48])
        self.assertEqual(len(frames_of(parsed, 32)), 2, "同尺寸多图 = 动画帧")
        self.assertEqual(frames_of(parsed, 32)[0]["pixels"][:4], bytes((0, 0, 255, 255)))
        self.assertEqual(frames_of(parsed, 32)[1]["pixels"][:4], bytes((0, 255, 0, 255)))
        self.assertEqual(frames_of(parsed, 48)[0]["xhot"], 4)

    def test_toc_is_grouped_by_nominal_size_and_keeps_frame_order(self):
        images = []
        for step in range(3):
            for nominal in (32, 48, 64):
                images.append(
                    image_from_frame(
                        solid_frame(32, 32, (0, 0), (step, 0, 0, 255)), nominal, 100
                    )
                )
        parsed = parse(build(images))
        self.assertEqual([i["nominal"] for i in parsed["images"]], [32] * 3 + [48] * 3 + [64] * 3)
        reds = [image["pixels"][2] for image in frames_of(parsed, 32)]
        self.assertEqual(reds, [0, 1, 2], "组内必须保持帧序，否则动画顺序会错")

    def test_toc_positions_match_real_layout(self):
        blob = build([image_from_frame(solid_frame(24, 24), 24, 50)])
        parsed = parse(blob)
        self.assertEqual(parsed["toc"][0][2], 16 + 12, "首图偏移应为 头16 + TOC12")
        self.assertEqual(len(blob), 16 + 12 + IMAGE_HEADER_SIZE + 24 * 24 * 4)

    def test_delay_is_preserved(self):
        parsed = parse(build([image_from_frame(solid_frame(32, 32), 32, 100)]))
        self.assertEqual(parsed["images"][0]["delay"], 100)

    def test_rejects_delay_beyond_u32(self):
        """延迟来自不可信文件的 u32：超范围必须抛 XcursorError，而不是 struct.error。"""
        with self.assertRaises(XcursorError):
            image_from_frame(solid_frame(32, 32), 32, 0xFFFFFFFF * 1000 // 60)

    def test_rejects_invalid_nominal(self):
        image = image_from_frame(solid_frame(32, 32), 32)
        broken = type(image)(
            nominal=0,
            width=image.width,
            height=image.height,
            hotspot_x=0,
            hotspot_y=0,
            delay_ms=0,
            pixels_argb=image.pixels_argb,
        )
        with self.assertRaises(XcursorError):
            build([broken])

    def test_rejects_empty(self):
        with self.assertRaises(XcursorError):
            build([])

    def test_rejects_hotspot_outside_image(self):
        with self.assertRaises(XcursorError):
            image_from_frame(solid_frame(32, 32, (32, 0)))

    def test_rejects_mismatched_pixel_count(self):
        image = image_from_frame(solid_frame(32, 32), 32)
        broken = type(image)(
            nominal=image.nominal,
            width=64,
            height=64,
            hotspot_x=0,
            hotspot_y=0,
            delay_ms=0,
            pixels_argb=image.pixels_argb,
        )
        with self.assertRaises(XcursorError):
            build([broken])

    def test_reference_parser_rejects_garbage(self):
        with self.assertRaises(RefParseError):
            parse(b"Xcur" + b"\x00" * 20)


@unittest.skipUnless(REFERENCE.is_file(), "系统缺少 Adwaita 光标主题，跳过格式比对")
class SystemReferenceTests(unittest.TestCase):
    def test_our_header_layout_matches_system_theme(self):
        """系统自带主题必须能被我们的独立读取器读懂，证明格式假设正确。"""
        blob = REFERENCE.read_bytes()
        parsed = parse(blob)
        first = parsed["images"][0]
        self.assertEqual(first["nominal"], 24)
        self.assertEqual((first["width"], first["height"]), (24, 24))
        self.assertEqual(parsed["toc"][0][2], 16 + parsed["ntoc"] * 12)
        self.assertGreaterEqual(parsed["ntoc"], 1)

    def test_our_output_has_same_container_shape(self):
        ours = parse(build([image_from_frame(solid_frame(24, 24), 24, 50)]))
        theirs = parse(REFERENCE.read_bytes())
        self.assertEqual(ours["version"], theirs["version"])
        self.assertEqual(ours["images"][0]["nominal"], 24)
        self.assertEqual(ours["images"][0]["nominal"], theirs["images"][0]["nominal"])
        self.assertEqual(len(ours["images"][0]["pixels"]), 24 * 24 * 4)

    def test_image_type_constant_is_the_documented_one(self):
        self.assertEqual(IMAGE_TYPE, 0xFFFD0002)


if __name__ == "__main__":
    unittest.main()
