# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 BigFatFish contributors
"""主题构建测试：目录结构、软链、防误删护栏，以及端到端产物可解析性。"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bigfatfish.catalog import LEGACY_CURSORS as CURSORS  # noqa: E402
from bigfatfish.catalog import theme_by_name  # noqa: E402
from bigfatfish.theme import ThemeError, build_theme  # noqa: E402
from _xcur_ref import frames_of, parse  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SPEC = theme_by_name("BigFatFish")
ASSETS = ROOT / "assets"

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


class SpecTests(unittest.TestCase):
    def test_every_source_file_is_used_once(self):
        sources = [spec.source for spec in CURSORS]
        self.assertEqual(len(sources), len(set(sources)))
        self.assertEqual(len(sources), 11, "install.inf 中共 11 个角色文件")

    def test_canonical_and_alias_names_are_unique(self):
        names: list[str] = []
        for spec in CURSORS:
            names.append(spec.canonical)
            names.extend(spec.aliases)
        self.assertEqual(len(names), len(set(names)), "光标名不得重复，否则会互相覆盖")

    def test_names_are_relative_safe(self):
        for spec in CURSORS:
            for name in (spec.canonical, *spec.aliases):
                self.assertNotIn("/", name)
                self.assertNotIn("..", name)


@unittest.skipUnless(ASSETS.is_dir(), "本地素材不存在（assets/ 不入库，属预期）")
class BuildThemeTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.out = Path(self._tmp.name) / SPEC.name

    def tearDown(self):
        self._tmp.cleanup()

    def test_builds_all_cursors_with_native_sizes(self):
        report = build_theme(SPEC, ASSETS, self.out)
        self.assertEqual({c.canonical for c in report.cursors}, set(EXPECTED_FRAMES))
        for cursor in report.cursors:
            with self.subTest(cursor=cursor.canonical):
                self.assertEqual(cursor.sizes, (32, 48, 64))
                self.assertEqual(cursor.frames, EXPECTED_FRAMES[cursor.canonical])
                self.assertEqual(
                    cursor.bytes_written,
                    (self.out / "cursors" / cursor.canonical).stat().st_size,
                )

    def test_every_produced_file_is_a_valid_xcursor_with_matching_frame_count(self):
        report = build_theme(SPEC, ASSETS, self.out)
        for cursor in report.cursors:
            with self.subTest(cursor=cursor.canonical):
                parsed = parse((self.out / "cursors" / cursor.canonical).read_bytes())
                self.assertEqual(parsed["ntoc"], cursor.frames * 3)
                for nominal in (32, 48, 64):
                    self.assertEqual(len(frames_of(parsed, nominal)), cursor.frames)
                first = frames_of(parsed, 32)[0]
                self.assertTrue(0 <= first["xhot"] < first["width"])
                self.assertTrue(0 <= first["yhot"] < first["height"])
                self.assertEqual(first["delay"], 100)

    def test_symlinks_are_relative_and_resolve(self):
        build_theme(SPEC, ASSETS, self.out)
        cursors_dir = self.out / "cursors"
        for spec in CURSORS:
            for alias in spec.aliases:
                with self.subTest(alias=alias):
                    link = cursors_dir / alias
                    self.assertTrue(link.is_symlink(), f"{alias} 应为软链")
                    self.assertEqual(link.readlink().as_posix(), spec.canonical)
                    self.assertTrue(link.resolve().is_file())
                    self.assertEqual(link.resolve().read_bytes(), (cursors_dir / spec.canonical).read_bytes())

    def test_index_theme_is_written(self):
        build_theme(SPEC, ASSETS, self.out)
        text = (self.out / "index.theme").read_text(encoding="utf-8")
        self.assertIn("[Icon Theme]", text)
        self.assertIn(f"Name={SPEC.name}", text)

    def test_size_filter_limits_output(self):
        report = build_theme(SPEC, ASSETS, self.out, sizes=(32,))
        for cursor in report.cursors:
            self.assertEqual(cursor.sizes, (32,))
            parsed = parse((self.out / "cursors" / cursor.canonical).read_bytes())
            self.assertEqual(parsed["ntoc"], cursor.frames)

    def test_rebuild_is_idempotent(self):
        first = build_theme(SPEC, ASSETS, self.out)
        second = build_theme(SPEC, ASSETS, self.out)
        self.assertEqual(first.total_bytes, second.total_bytes)
        self.assertEqual(
            [c.bytes_written for c in first.cursors], [c.bytes_written for c in second.cursors]
        )

    def test_refuses_foreign_non_empty_directory(self):
        self.out.mkdir(parents=True)
        (self.out / "someone-elses-file.txt").write_text("别删我", encoding="utf-8")
        with self.assertRaises(ThemeError):
            build_theme(SPEC, ASSETS, self.out)
        self.assertTrue((self.out / "someone-elses-file.txt").exists(), "护栏不得删除外来文件")

    def test_force_allows_foreign_directory(self):
        self.out.mkdir(parents=True)
        (self.out / "someone-elses-file.txt").write_text("别删我", encoding="utf-8")
        report = build_theme(SPEC, ASSETS, self.out, force=True)
        self.assertEqual(len(report.cursors), 11)
        self.assertTrue((self.out / "someone-elses-file.txt").exists())

    def test_refuses_symlinked_cursor_file_without_touching_target(self):
        """规范名被换成软链时必须拒绝：否则会以本进程身份覆写链接目标。"""
        victim = Path(self._tmp.name) / "victim.txt"
        victim.write_text("original", encoding="utf-8")
        cursors = self.out / "cursors"
        cursors.mkdir(parents=True)
        (cursors / "left_ptr").symlink_to(victim)

        with self.assertRaises(ThemeError):
            build_theme(SPEC, ASSETS, self.out)
        self.assertEqual(victim.read_text(encoding="utf-8"), "original")

    def test_refuses_symlinked_cursors_dir(self):
        """cursors/ 本身是软链时，整批产物会被重定向，必须拒绝。"""
        elsewhere = Path(self._tmp.name) / "elsewhere"
        elsewhere.mkdir()
        self.out.mkdir()
        (self.out / "index.theme").write_text(f"Name={SPEC.name}\n", encoding="utf-8")
        (self.out / "cursors").symlink_to(elsewhere, target_is_directory=True)

        with self.assertRaises(ThemeError):
            build_theme(SPEC, ASSETS, self.out)
        self.assertEqual(list(elsewhere.iterdir()), [])

    def test_missing_assets_raises(self):
        with self.assertRaises(ThemeError):
            build_theme(SPEC, ROOT / "assets" / "nonexistent", self.out)


if __name__ == "__main__":
    unittest.main()
