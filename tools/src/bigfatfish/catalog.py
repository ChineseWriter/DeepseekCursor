# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 BigFatFish contributors
"""主题清单：素材布局与 Windows 角色 -> XCursor 名字映射。

本模块只放**数据**（哪套素材、怎么映射、有哪些主题），构建逻辑在 :mod:`bigfatfish.theme`。

两套映射各自独立，不互相"顺手统一"：

* :data:`LEGACY_CURSORS` —— 现有 ``BigFatFish`` 素材（4evergr8 的 ``install.inf`` 声明的 11 个角色）。
  保持原样，保证已入库主题可逐字节重建。
* :data:`COLLECTION_CURSORS` —— B 站合集（11 个仓库 / 15 个角色）统一的 17 个 Windows 角色。

别名取 freedesktop/X11 的通用名，**参考**系统自带 ``Adwaita`` 的 63 个条目，
但不承诺逐条对齐（``grab``/``copy``/``context-menu``/``dnd-*``/``zoom-*`` 等未映射，
请求它们的应用会回退到系统主题）；别名在生成时做成**相对软链**，主题目录可整体搬移。

**许可分组（``license_id``）必须与上游声明一致**：不同来源条件不同，不得互相套用；
上游明确表示"未确认原作者"的造型，**不得**被标注成某个已确认作者的作品。
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
    title: str
    comment: str
    out_dir: str
    pattern: str
    cursors: tuple[CursorSpec, ...]
    license_id: str
    sizes: tuple[int, ...] = (32, 48, 64)
    #: 来源信息，用于署名文件与排错；不参与像素构建。
    repo: str = ""
    video: str = ""
    note: str = ""


#: 合集的 11 个仓库都属于同一发布者
_UPSTREAM_OWNER = "nibushiyigeren123-bot"
_COLLECTION_PATTERN = "src/{repo}/cursors/{char}/{size}/{source}"
_COLLECTION_SIZES = (32, 48, 64)


def _collection(
    name: str,
    title: str,
    comment: str,
    repo: str,
    char: str,
    video: str,
    license_id: str,
    note: str = "",
) -> ThemeSpec:
    return ThemeSpec(
        name=name,
        title=title,
        comment=comment,
        out_dir=f"themes/{name}",
        pattern=_COLLECTION_PATTERN.format(repo=repo, char=char, size="{size}", source="{source}"),
        cursors=COLLECTION_CURSORS,
        license_id=license_id,
        sizes=_COLLECTION_SIZES,
        repo=f"{_UPSTREAM_OWNER}/{repo}",
        video=video,
        note=note,
    )


#: 全部主题。顺序即 README 与 ``build --all`` 的顺序。
THEMES: tuple[ThemeSpec, ...] = (
    ThemeSpec(
        name="BigFatFish",
        title="大肥鱼 / 鲸鱼娘",
        comment="大肥鱼 / BigFatFish 全动态光标主题（由 .ani 转换）",
        out_dir="themes/BigFatFish",
        pattern="BigFatFish/{source}",
        cursors=LEGACY_CURSORS,
        license_id="cc-by-nc-sa-4.0",
        repo="",
        video="BV1WypJ6WExu",
        note="Windows 光标包由 B 站 UP 4evergr8 发布，视频页未附许可声明。",
    ),
    _collection(
        "ChatGPTDragon",
        "ChatGPT 龙娘",
        "ChatGPT 龙娘 · 17 状态动态光标（社区二创）",
        "chatgpt-dragon-cursors",
        "chatgpt-dragon",
        "BV1t2pZ6iEJ2",
        "unconfirmed",
        note="上游自述参考图署名 @光影随云飞，但明确表示原作者身份与授权范围尚未确认。",
    ),
    _collection(
        "ClaudeOpus",
        "Claude 三姐妹 · Opus",
        "Claude 三姐妹 · Opus · 17 状态动态光标（社区二创）",
        "claude-sisters-cursors",
        "opus",
        "BV1MGpD62EVE",
        "zipzip-nc",
    ),
    _collection(
        "ClaudeSonnet",
        "Claude 三姐妹 · Sonnet",
        "Claude 三姐妹 · Sonnet · 17 状态动态光标（社区二创）",
        "claude-sisters-cursors",
        "sonnet",
        "BV1MGpD62EVE",
        "zipzip-nc",
    ),
    _collection(
        "ClaudeFable",
        "Claude 三姐妹 · Fable",
        "Claude 三姐妹 · Fable · 17 状态动态光标（社区二创）",
        "claude-sisters-cursors",
        "fable",
        "BV1MGpD62EVE",
        "zipzip-nc",
        note="v1.0.1 按用户提供的全身图重做 Fable 形象，与 Opus 区分开；"
        "上游同时说明原作者身份并未因用户提供图片而得到额外确认。",
    ),
    _collection(
        "AstraMint",
        "Astra（薄荷绿 GPT 姐妹 · 姐姐）",
        "Astra · 薄荷绿 · 17 状态动态光标（社区二创）",
        "astra-sol-mint-cursors",
        "astra",
        "BV1iGpL6fELG",
        "unconfirmed",
        note="上游仓库未附素材许可文件，仅代码为 MIT；视频简介称角色形象为本地模型 Q 版重绘。",
    ),
    _collection(
        "SolMint",
        "sol（薄荷绿 GPT 姐妹 · 妹妹）",
        "sol · 薄荷绿 · 17 状态动态光标（社区二创）",
        "astra-sol-mint-cursors",
        "sol",
        "BV1iGpL6fELG",
        "unconfirmed",
        note="上游仓库未附素材许可文件，仅代码为 MIT；视频简介称角色形象为本地模型 Q 版重绘。",
    ),
    _collection(
        "DeepSeekWhale",
        "DeepSeek 小鲸鱼",
        "DeepSeek 小鲸鱼 · 17 状态动态光标（社区二创）",
        "DeepSeek-mint-cursors",
        "deepseek",
        "BV1fBpn6jEVb",
        "yunyue-1.0",
        note="角色素材出自 YunYueSama 的 codex-deepseek-pet，采用其「大肥鱼项目署名许可 1.0」。",
    ),
    _collection(
        "Gemini",
        "Gemini 猫耳娘",
        "Gemini 猫耳娘 · 17 状态动态光标（社区二创）",
        "gemini-cursors",
        "gemini",
        "BV1MGpD62ExT",
        "zipzip-nc",
    ),
    _collection(
        "GLM",
        "GLM 黑狐耳",
        "GLM 黑狐耳 · 17 状态动态光标（社区二创）",
        "glm-cursors",
        "glm",
        "BV1x7pD6VENQ",
        "zipzip-nc",
    ),
    _collection(
        "Grok",
        "Grok 黑金双马尾",
        "Grok 黑金双马尾 · 17 状态动态光标（社区二创）",
        "grok-cursors",
        "grok",
        "BV1N7pD6VECC",
        "zipzip-nc",
    ),
    _collection(
        "Kimi",
        "Kimi 银发",
        "Kimi 银发 · 17 状态动态光标（社区二创）",
        "kimi-cursors",
        "kimi",
        "BV1TLpD6yEwC",
        "zipzip-nc",
    ),
    _collection(
        "MiMo",
        "MiMo 黑白橙",
        "MiMo 黑白橙 · 17 状态动态光标（社区二创）",
        "mimo-cursors",
        "mimo",
        "BV1KLpD6yE1d",
        "upstream-nc-author-unconfirmed",
        note="上游明确写道：MiMo 这一具体造型的原始插画作者尚未确认，"
        "不将它标注为 ZipZipPipe 已确认作品；新增动作仍只用于非商业社区分享。",
    ),
    _collection(
        "Qwen",
        "Qwen 折扇娘",
        "Qwen 折扇娘 · 17 状态动态光标（社区二创）",
        "qwen-cursors",
        "qwen",
        "BV1ZYpD6wE9y",
        "zipzip-nc",
    ),
    _collection(
        "Seedream",
        "Seedream",
        "Seedream · 17 状态动态光标（社区二创）",
        "bytedance-cursors",
        "seedream",
        "BV1ZYpD6wEWU",
        "zipzip-nc",
    ),
    _collection(
        "Doubao",
        "豆包",
        "豆包 · 17 状态动态光标（社区二创）",
        "bytedance-cursors",
        "doubao",
        "BV1ZYpD6wEWU",
        "upstream-nc-author-unconfirmed",
        note="上游明确写道：豆包造型依**用户提供**的短发全身图与 App 头像对照制作，"
        "不作已确认作者的表述；新增动作仍只用于非商业社区分享。",
    ),
)


def theme_by_name(name: str) -> ThemeSpec:
    """按名字取主题；名字不存在时抛出 ``KeyError``。"""
    for spec in THEMES:
        if spec.name == name:
            return spec
    raise KeyError(name)


def theme_names() -> tuple[str, ...]:
    return tuple(spec.name for spec in THEMES)
