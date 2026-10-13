# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 BigFatFish contributors
"""主题清单：素材布局与 Windows 角色 -> XCursor 名字映射。

本模块只放**数据**（哪套素材、怎么映射、有哪些主题），构建逻辑在 :mod:`bigfatfish.theme`。

两套映射各自独立，不互相"顺手统一"：

* :data:`LEGACY_CURSORS` —— 现有 ``BigFatFish`` 素材（4evergr8 的 ``install.inf`` 声明的 11 个角色）。
  保持原样，保证已入库主题可逐字节重建。
* :data:`COLLECTION_CURSORS` —— B 站合集（11 个仓库 / 15 个角色）统一的 17 个 Windows 角色。

别名一律取 freedesktop/X11 的通用名（覆盖基准为系统自带 ``Adwaita`` 的 63 个条目），
让不同工具链请求的名字都能命中；别名在生成时做成**相对软链**，主题目录可整体搬移。
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CursorSpec:
    """一个角色的映射：源 .ani 文件 -> XCursor 主名 + 别名。"""

    source: str
    canonical: str
    windows_role: str
    aliases: tuple[str, ...] = ()


#: 现有 BigFatFish 素材的映射（依据 install.inf 的权威映射：
#: Arrow/AppStarting/Wait/crosshair+precisionhair/IBeam/SizeNS/SizeWE/SizeNWSE/
#: SizeNESW/Grab+SizeAll/Hand）。**不要改动**，改了会让已入库主题无法逐字节重建。
LEGACY_CURSORS: tuple[CursorSpec, ...] = (
    CursorSpec("pointer.ani", "left_ptr", "Arrow", ("default", "arrow", "top_left_arrow", "left-arrow")),
    CursorSpec("work.ani", "left_ptr_watch", "AppStarting", ("progress", "half-busy")),
    CursorSpec("busy.ani", "watch", "Wait", ("wait", "busy")),
    CursorSpec("cross.ani", "crosshair", "crosshair/precisionhair", ("cross", "tcross")),
    CursorSpec("text.ani", "text", "IBeam", ("xterm", "ibeam")),
    CursorSpec("move.ani", "fleur", "Grab/SizeAll", ("move", "size_all", "all-scroll", "grabbing")),
    CursorSpec("link.ani", "hand2", "Hand", ("pointer", "hand", "hand1", "pointing_hand")),
    CursorSpec(
        "vert.ani",
        "sb_v_double_arrow",
        "SizeNS",
        ("size_ver", "ns-resize", "v_double_arrow", "row-resize"),
    ),
    CursorSpec(
        "horz.ani",
        "sb_h_double_arrow",
        "SizeWE",
        ("size_hor", "ew-resize", "h_double_arrow", "col-resize"),
    ),
    CursorSpec(
        "dgn1.ani",
        "size_fdiag",
        "SizeNWSE",
        ("nwse-resize", "top_left_corner", "bottom_right_corner"),
    ),
    CursorSpec(
        "dgn2.ani",
        "size_bdiag",
        "SizeNESW",
        ("nesw-resize", "top_right_corner", "bottom_left_corner"),
    ),
)


#: 合集的 17 个 Windows 角色 -> XCursor 通用名。
#: 主名取 freedesktop 现代名（应用与新工具链优先请求这些），X11 经典名放别名。
COLLECTION_CURSORS: tuple[CursorSpec, ...] = (
    CursorSpec("Arrow.ani", "left_ptr", "Arrow", ("default", "arrow", "top_left_arrow", "left-arrow")),
    CursorSpec("Help.ani", "question_arrow", "Help", ("help", "whats_this")),
    CursorSpec(
        "AppStarting.ani",
        "left_ptr_watch",
        "AppStarting",
        ("progress", "half-busy", "app-starting"),
    ),
    CursorSpec("Wait.ani", "watch", "Wait", ("wait", "busy")),
    CursorSpec("Crosshair.ani", "crosshair", "Crosshair", ("cross", "tcross")),
    CursorSpec("IBeam.ani", "text", "IBeam", ("xterm", "ibeam")),
    CursorSpec("NWPen.ani", "pencil", "NWPen", ("draft", "draft_large", "draft_small")),
    CursorSpec(
        "No.ani",
        "not-allowed",
        "No",
        ("no-drop", "forbidden", "crossed_circle"),
    ),
    CursorSpec(
        "SizeAll.ani",
        "fleur",
        "SizeAll",
        ("move", "size_all", "all-scroll", "all-resize"),
    ),
    CursorSpec(
        "SizeNESW.ani",
        "nesw-resize",
        "SizeNESW",
        ("size_bdiag", "top_right_corner", "bottom_left_corner", "sw-resize", "ne-resize"),
    ),
    CursorSpec(
        "SizeNS.ani",
        "ns-resize",
        "SizeNS",
        (
            "size_ver",
            "v_double_arrow",
            "sb_v_double_arrow",
            "row-resize",
            "n-resize",
            "s-resize",
        ),
    ),
    CursorSpec(
        "SizeNWSE.ani",
        "nwse-resize",
        "SizeNWSE",
        (
            "size_fdiag",
            "top_left_corner",
            "bottom_right_corner",
            "nw-resize",
            "se-resize",
        ),
    ),
    CursorSpec(
        "SizeWE.ani",
        "ew-resize",
        "SizeWE",
        (
            "size_hor",
            "h_double_arrow",
            "sb_h_double_arrow",
            "col-resize",
            "e-resize",
            "w-resize",
        ),
    ),
    CursorSpec("UpArrow.ani", "center_ptr", "UpArrow", ("up-arrow", "sb_up_arrow")),
    CursorSpec("Hand.ani", "hand2", "Hand", ("pointer", "hand", "hand1", "pointing_hand")),
    CursorSpec("Person.ani", "person", "Person", ("human",)),
    CursorSpec("Pin.ani", "cell", "Pin", ("pin", "location")),
)


@dataclass(frozen=True)
class ThemeSpec:
    """一个可构建主题。

    ``pattern`` 是相对 ``assets/`` 的路径模板，可用占位符 ``{source}`` / ``{size}``
    （``{size}`` 出现在模板里表示素材按档位分文件）。
    """

    name: str
    comment: str
    out_dir: str
    pattern: str
    cursors: tuple[CursorSpec, ...]
    sizes: tuple[int, ...] = (32, 48, 64)
    #: 来源标识（仓库 / 角色目录），供文档与排错核对；不参与构建。
    origin: str = ""


_COLLECTION_PATTERN = "src/{repo}/cursors/{char}/{size}/{source}"
_COLLECTION_SIZES = (32, 48, 64)


def _collection(
    name: str,
    comment: str,
    repo: str,
    char: str,
    origin: str = "",
) -> ThemeSpec:
    return ThemeSpec(
        name=name,
        comment=comment,
        out_dir=f"themes/{name}",
        pattern=_COLLECTION_PATTERN.format(repo=repo, char=char, size="{size}", source="{source}"),
        cursors=COLLECTION_CURSORS,
        sizes=_COLLECTION_SIZES,
        origin=origin or f"{repo} / cursors/{char}",
    )


#: 全部主题。顺序即 README 与 ``build --all`` 的顺序。
THEMES: tuple[ThemeSpec, ...] = (
    ThemeSpec(
        name="BigFatFish",
        comment="大肥鱼 / BigFatFish 全动态光标主题（由 .ani 转换）",
        out_dir="themes/BigFatFish",
        pattern="BigFatFish/{source}",
        cursors=LEGACY_CURSORS,
        origin="BV1WypJ6WExu（UP 4evergr8）",
    ),
    _collection(
        "ChatGPTDragon",
        "ChatGPT 龙娘 · 17 状态动态光标（社区二创）",
        "chatgpt-dragon-cursors",
        "chatgpt-dragon",
    ),
    _collection(
        "ClaudeOpus",
        "Claude 三姐妹 · Opus · 17 状态动态光标（社区二创）",
        "claude-sisters-cursors",
        "opus",
    ),
    _collection(
        "ClaudeSonnet",
        "Claude 三姐妹 · Sonnet · 17 状态动态光标（社区二创）",
        "claude-sisters-cursors",
        "sonnet",
    ),
    _collection(
        "ClaudeFable",
        "Claude 三姐妹 · Fable · 17 状态动态光标（社区二创）",
        "claude-sisters-cursors",
        "fable",
    ),
    _collection(
        "AstraMint",
        "Astra · 薄荷绿 · 17 状态动态光标（社区二创）",
        "astra-sol-mint-cursors",
        "astra",
    ),
    _collection(
        "SolMint",
        "sol · 薄荷绿 · 17 状态动态光标（社区二创）",
        "astra-sol-mint-cursors",
        "sol",
    ),
    _collection(
        "DeepSeekWhale",
        "DeepSeek 小鲸鱼 · 17 状态动态光标（社区二创）",
        "DeepSeek-mint-cursors",
        "deepseek",
    ),
    _collection("Gemini", "Gemini 猫耳娘 · 17 状态动态光标（社区二创）", "gemini-cursors", "gemini"),
    _collection("GLM", "GLM 黑狐耳 · 17 状态动态光标（社区二创）", "glm-cursors", "glm"),
    _collection("Grok", "Grok 黑金双马尾 · 17 状态动态光标（社区二创）", "grok-cursors", "grok"),
    _collection("Kimi", "Kimi 银发 · 17 状态动态光标（社区二创）", "kimi-cursors", "kimi"),
    _collection("MiMo", "MiMo 黑白橙 · 17 状态动态光标（社区二创）", "mimo-cursors", "mimo"),
    _collection("Qwen", "Qwen 折扇娘 · 17 状态动态光标（社区二创）", "qwen-cursors", "qwen"),
    _collection(
        "Seedream",
        "Seedream · 17 状态动态光标（社区二创）",
        "bytedance-cursors",
        "seedream",
    ),
    _collection("Doubao", "豆包 · 17 状态动态光标（社区二创）", "bytedance-cursors", "doubao"),
)


def theme_by_name(name: str) -> ThemeSpec:
    """按名字取主题；名字不存在时抛出 ``KeyError``。"""
    for spec in THEMES:
        if spec.name == name:
            return spec
    raise KeyError(name)


def theme_names() -> tuple[str, ...]:
    return tuple(spec.name for spec in THEMES)
