# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 BigFatFish contributors
"""主交付物验收测试：仓库 `themes/` 下**已入库**的全部主题本体。

与 test_theme.py 的区别：那些测试验证"构建逻辑是否正确"（需要本地素材，无素材时 skip），
本文件验证"已经入库的成品是否可用"——不依赖任何本地素材，因此在 CI 里必然执行。
主题是本项目的主交付物，它必须在 CI 里被真正校验，否则 CI 形同虚设。

校验内容：清单与目录一一对应、每个光标是可解析的 XCursor、只含入库的原生档、
热点在图像范围内、别名是可解析的相对软链。
"""

from __future__ import annotations

import os
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bigfatfish.catalog import THEMES, theme_names  # noqa: E402
from _xcur_ref import frames_of, parse  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
THEMES_DIR = REPO_ROOT / "themes"

#: 与 bigfatfish.preview.MAX_SAMPLED_FRAMES 一致（预览每列最多几帧）
PREVIEW_MAX_FRAMES = 3

#: BigFatFish 是首个已实测通过的成品，帧数是该素材的事实快照。
#: 它变化意味着素材或构建代码被动过，必须人工确认后再更新本表。
BIGFATFISH_FRAMES = {
    "left_ptr": 23,
    "left_ptr_watch": 25,
    "watch": 22,
    "crosshair": 26,
    "text": 24,
    "fleur": 18,
    "hand2": 21,
    "sb_v_double_arrow": 24,
    "sb_h_double_arrow": 23,
    "size_fdiag": 19,
    "size_bdiag": 23,
}


def _shipped_dirs() -> list[Path]:
    if not THEMES_DIR.is_dir():
        return []
    return sorted(path for path in THEMES_DIR.iterdir() if path.is_dir())


class ShippedThemeTests(unittest.TestCase):
    def test_repository_ships_exactly_the_cataloged_themes(self):
        shipped = {path.name for path in _shipped_dirs()}
        self.assertEqual(shipped, set(theme_names()))

    def test_every_theme_has_its_own_index_theme(self):
        for spec in THEMES:
            with self.subTest(theme=spec.name):
                index = THEMES_DIR / spec.name / "index.theme"
                self.assertTrue(index.is_file(), f"{spec.name} 缺 index.theme")
                text = index.read_text(encoding="utf-8")
                self.assertIn("[Icon Theme]", text)
                self.assertIn(f"Name={spec.name}", text)

    def test_cursor_entries_match_the_catalog(self):
        for spec in THEMES:
            theme_dir = THEMES_DIR / spec.name
            if not theme_dir.is_dir():
                continue
            with self.subTest(theme=spec.name):
                cursors = theme_dir / "cursors"
                entries = list(cursors.iterdir())
                real = {p.name for p in entries if not p.is_symlink()}
                links = {p.name for p in entries if p.is_symlink()}
                self.assertEqual(real, {c.canonical for c in spec.cursors})
                self.assertEqual(links, {a for c in spec.cursors for a in c.aliases})

    def test_every_cursor_parses_with_declared_sizes(self):
        for spec in THEMES:
            theme_dir = THEMES_DIR / spec.name
            if not theme_dir.is_dir():
                continue
            for cursor in spec.cursors:
                with self.subTest(theme=spec.name, cursor=cursor.canonical):
                    path = theme_dir / "cursors" / cursor.canonical
                    parsed = parse(path.read_bytes())
                    sizes = tuple(sorted({img["nominal"] for img in parsed["images"]}))
                    self.assertEqual(sizes, spec.sizes)
                    self.assertEqual(parsed["ntoc"], len(parsed["images"]))
                    for image in parsed["images"]:
                        self.assertTrue(0 <= image["xhot"] < image["width"])
                        self.assertTrue(0 <= image["yhot"] < image["height"])
                        self.assertGreater(image["delay"], 0, "帧延迟为 0 会让动画空转")

    def test_frames_are_aligned_across_sizes(self):
        """同一光标的各档帧数必须一致，否则合成器切档时动画会跳。"""
        for spec in THEMES:
            theme_dir = THEMES_DIR / spec.name
            if not theme_dir.is_dir():
                continue
            for cursor in spec.cursors:
                with self.subTest(theme=spec.name, cursor=cursor.canonical):
                    parsed = parse((theme_dir / "cursors" / cursor.canonical).read_bytes())
                    counts = {len(frames_of(parsed, size)) for size in spec.sizes}
                    self.assertEqual(len(counts), 1, f"各档帧数不一致：{sorted(counts)}")

    def test_aliases_are_relative_symlinks_that_resolve(self):
        for spec in THEMES:
            theme_dir = THEMES_DIR / spec.name
            if not theme_dir.is_dir():
                continue
            cursors = theme_dir / "cursors"
            for cursor in spec.cursors:
                for alias in cursor.aliases:
                    with self.subTest(theme=spec.name, alias=alias):
                        link = cursors / alias
                        self.assertTrue(link.is_symlink(), f"{alias} 应为软链")
                        target = os.readlink(link)
                        # 相对软链：主题目录可以整体搬移/复制而不断链
                        self.assertFalse(os.path.isabs(target), f"{alias} 指向绝对路径")
                        self.assertEqual(target, cursor.canonical)
                        self.assertTrue((cursors / target).is_file(), f"{alias} -> {target} 断链")

    def test_bigfatfish_frame_counts_are_unchanged(self):
        cursors = THEMES_DIR / "BigFatFish" / "cursors"
        if not cursors.is_dir():
            self.skipTest("BigFatFish 未入库")
        for name, expected in BIGFATFISH_FRAMES.items():
            with self.subTest(cursor=name):
                parsed = parse((cursors / name).read_bytes())
                self.assertEqual(len(frames_of(parsed, 64)), expected)

    def test_every_theme_ships_its_preview(self):
        """预览图必须是本主题自己渲染的：尺寸由清单与光标帧数唯一决定。"""
        for spec in THEMES:
            theme_dir = THEMES_DIR / spec.name
            if not theme_dir.is_dir():
                continue
            with self.subTest(theme=spec.name):
                blob = (theme_dir / "preview.png").read_bytes()
                self.assertEqual(blob[:8], b"\x89PNG\r\n\x1a\n", "不是 PNG")
                length, tag = struct.unpack_from(">I4s", blob, 8)
                self.assertEqual(tag, b"IHDR")
                width, height = struct.unpack_from(">II", blob, 16)
                cell = max(spec.sizes)
                rows = 0
                for cursor in spec.cursors:
                    parsed = parse((theme_dir / "cursors" / cursor.canonical).read_bytes())
                    rows = max(rows, min(len(frames_of(parsed, cell)), PREVIEW_MAX_FRAMES))
                self.assertEqual(width, cell * len(spec.cursors))
                self.assertEqual(height, cell * rows)

    def test_every_theme_ships_its_attribution(self):
        for spec in THEMES:
            theme_dir = THEMES_DIR / spec.name
            if not theme_dir.is_dir():
                continue
            with self.subTest(theme=spec.name):
                text = (theme_dir / "ATTRIBUTION.md").read_text(encoding="utf-8")
                self.assertIn(spec.name, text)
                self.assertIn(spec.video, text)
                # 每个主题都必须写明署名要求与商用与否（不同来源结论不同，但都得写清楚）
                self.assertIn("署名", text)
                self.assertIn("商用", text)
                if spec.repo:
                    self.assertIn(spec.repo, text)
                # 防漂移：署名文件里的许可分组与状态数必须与清单一致
                self.assertIn(f"`{spec.license_id}`", text, "许可分组与 catalog 不一致")
                self.assertIn(f"{len(spec.cursors)} 个状态", text, "状态数与 catalog 不一致")
                if spec.license_id == "upstream-nc-author-unconfirmed":
                    # 上游明确未确认作者的造型：不得被署名为 ZipZipPipe 的作品
                    self.assertIn("未确认", text)
                    self.assertNotIn("角色原作：ZipZipPipe", text)

    def test_deepseek_theme_ships_the_upstream_license_text(self):
        """该来源的许可要求分发时保留完整许可文本。"""
        license_file = THEMES_DIR / "DeepSeekWhale" / "LICENSE-ART.txt"
        if not license_file.is_file():
            self.skipTest("主题未入库")
        text = license_file.read_text(encoding="utf-8")
        self.assertIn("大肥鱼项目署名许可", text)
        self.assertIn("YunYueSama", text)


if __name__ == "__main__":
    unittest.main()
