# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 BigFatFish contributors
"""主交付物验收测试：仓库根目录的 `BigFatFish/` 主题本体。

与 test_theme.py 的区别：那些测试验证"构建逻辑是否正确"（需要本地素材，CI 里会 skip），
本文件验证"**已经入库的成品是否可用**"——不依赖任何本地素材，因此在 CI 里必然执行。
主题是本项目的主交付物，它必须在 CI 里被真正校验，否则 CI 形同虚设。
"""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from _xcur_ref import frames_of, parse  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
THEME = REPO_ROOT / "themes" / "BigFatFish"
CURSORS = THEME / "cursors"

#: 每个光标在 64 标称档下的帧数（与 tools/src 的构建结果一致）
EXPECTED_FRAMES = {
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

#: 素材自带的原生标称尺寸，转换后必须原样保留
EXPECTED_SIZES = (32, 48, 64)

#: install.inf 声明的角色映射（含 34 个别名，共 45 个条目）
EXPECTED_ENTRIES = 45


@unittest.skipUnless(THEME.is_dir(), "主题目录不存在")
class ShippedThemeTests(unittest.TestCase):
    def test_index_theme_declares_the_theme_name(self):
        text = (THEME / "index.theme").read_text(encoding="utf-8")
        self.assertIn("[Icon Theme]", text)
        self.assertIn("Name=BigFatFish", text)

    def test_cursor_count_and_aliases(self):
        entries = list(CURSORS.iterdir())
        self.assertEqual(len(entries), EXPECTED_ENTRIES)
        real = [p for p in entries if not p.is_symlink()]
        self.assertEqual(sorted(p.name for p in real), sorted(EXPECTED_FRAMES))

    def test_every_cursor_parses_with_expected_frames_and_sizes(self):
        for name, expected_frames in EXPECTED_FRAMES.items():
            with self.subTest(cursor=name):
                parsed = parse((CURSORS / name).read_bytes())
                sizes = tuple(sorted({img["nominal"] for img in parsed["images"]}))
                self.assertEqual(sizes, EXPECTED_SIZES)
                self.assertEqual(len(frames_of(parsed, 64)), expected_frames)

    def test_aliases_are_relative_symlinks_that_resolve(self):
        aliases = [p for p in CURSORS.iterdir() if p.is_symlink()]
        self.assertEqual(len(aliases), EXPECTED_ENTRIES - len(EXPECTED_FRAMES))
        for link in aliases:
            with self.subTest(alias=link.name):
                target = os.readlink(link)
                # 相对软链：主题目录可以整体搬移/复制而不断链
                self.assertFalse(os.path.isabs(target), f"{link.name} 指向绝对路径")
                self.assertTrue((CURSORS / target).exists(), f"{link.name} -> {target} 断链")
