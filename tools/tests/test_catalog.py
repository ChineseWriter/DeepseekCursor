# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 BigFatFish contributors
"""主题清单的数据完整性测试（不需要本地素材，CI 里必然执行）。

清单是"哪些主题、怎么映射"的唯一真实来源，一旦写错会成批产出错误的主题目录，
因此在无素材环境下也要把它的约束钉住。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bigfatfish.catalog import (  # noqa: E402
    COLLECTION_CURSORS,
    LEGACY_CURSORS,
    THEMES,
    theme_by_name,
    theme_names,
)


class CatalogTests(unittest.TestCase):
    def test_theme_names_are_unique_and_safe(self):
        names = theme_names()
        self.assertEqual(len(names), len(set(names)), "主题名不得重复")
        for name in names:
            self.assertNotIn("/", name)
            self.assertNotIn("..", name)

    def test_out_dirs_are_unique_and_relative(self):
        dirs = [spec.out_dir for spec in THEMES]
        self.assertEqual(len(dirs), len(set(dirs)), "输出目录不得重复")
        for out_dir in dirs:
            self.assertFalse(out_dir.startswith("/"), "输出目录必须是仓库内相对路径")
            self.assertFalse(out_dir.endswith("/"))

    def test_sizes_are_non_empty_sorted_and_positive(self):
        for spec in THEMES:
            with self.subTest(theme=spec.name):
                self.assertTrue(spec.sizes)
                self.assertEqual(tuple(sorted(set(spec.sizes))), spec.sizes)
                self.assertTrue(all(size > 0 for size in spec.sizes))

    def test_pattern_formats_for_every_cursor_and_size(self):
        for spec in THEMES:
            for cursor in spec.cursors:
                for size in spec.sizes:
                    with self.subTest(theme=spec.name, cursor=cursor.source, size=size):
                        path = spec.pattern.format(source=cursor.source, size=size)
                        self.assertNotIn("{", path, "模板有未替换的占位符")
                        self.assertNotIn("..", path)

    def test_cursor_names_are_unique_within_each_theme(self):
        for spec in THEMES:
            names: list[str] = []
            for cursor in spec.cursors:
                names.append(cursor.canonical)
                names.extend(cursor.aliases)
            with self.subTest(theme=spec.name):
                self.assertEqual(len(names), len(set(names)), "光标名重复会互相覆盖")

    def test_cursor_names_are_filesystem_safe(self):
        for spec in THEMES:
            for cursor in spec.cursors:
                for name in (cursor.canonical, *cursor.aliases):
                    with self.subTest(theme=spec.name, name=name):
                        self.assertNotIn("/", name)
                        self.assertNotIn("..", name)
                        self.assertTrue(name)

    def test_legacy_mapping_is_untouched(self):
        """BigFatFish 已入库，映射一旦改动就无法逐字节重建。"""
        self.assertEqual(len(LEGACY_CURSORS), 11)
        self.assertEqual(sum(len(c.aliases) for c in LEGACY_CURSORS), 34)
        self.assertEqual(
            [c.canonical for c in LEGACY_CURSORS],
            [
                "left_ptr",
                "left_ptr_watch",
                "watch",
                "crosshair",
                "text",
                "fleur",
                "hand2",
                "sb_v_double_arrow",
                "sb_h_double_arrow",
                "size_fdiag",
                "size_bdiag",
            ],
        )

    def test_collection_mapping_covers_windows_17_roles(self):
        roles = [c.windows_role for c in COLLECTION_CURSORS]
        self.assertEqual(len(roles), 17)
        self.assertEqual(len(set(roles)), 17, "Windows 角色不得重复")
        self.assertEqual(len({c.source for c in COLLECTION_CURSORS}), 17)
        for cursor in COLLECTION_CURSORS:
            with self.subTest(role=cursor.windows_role):
                self.assertEqual(cursor.source, f"{cursor.windows_role}.ani")

    def test_collection_themes_share_one_mapping(self):
        for spec in THEMES:
            if spec.name == "BigFatFish":
                continue
            with self.subTest(theme=spec.name):
                self.assertIs(spec.cursors, COLLECTION_CURSORS)
                self.assertEqual(spec.sizes, (32, 48, 64))

    def test_theme_by_name_raises_for_unknown(self):
        with self.assertRaises(KeyError):
            theme_by_name("NoSuchTheme")


if __name__ == "__main__":
    unittest.main()
