<!-- SPDX-License-Identifier: CC-BY-NC-SA-4.0 -->
<!-- Copyright (C) 2026 BigFatFish contributors -->

# themes/ — 生成的光标主题（**不入库**）

本目录存放由 `assets/` 素材转换出的 XCursor 主题（`index.theme` + `cursors/`），供本机安装使用。

## 为什么不入库

主题内的光标图像是上游美术素材的**演绎作品**，权利属上游，且受**非商业 + 相同方式共享**约束（详见 [THIRD-PARTY.md](../THIRD-PARTY.md)）。提交进 Git 即构成再分发。

`.gitignore` 已强制拦截：

```
/themes/*
!/themes/README.md
```

## 本机安装（个人使用）

用仓库自带的安装脚本（默认 dry-run，写入 `$HOME` 属 AGENTS.md R5 管辖）：

```bash
scripts/install-theme.sh              # 只打印计划
scripts/install-theme.sh --yes        # 装到 $XDG_DATA_HOME/icons（缺省 ~/.local/share/icons）
gsettings set org.gnome.desktop.interface cursor-theme 'BigFatFish'
```

Wayland 会缓存光标主题，**注销并重新登录**后由合成器重新加载。

## 实测结论（在 Ubuntu 26.04 / Wayland 上验证过）

1. **`~/.local/share/icons/` 一个位置就够，不需要再往 `~/.icons/` 放软链。**
   - `libwayland-cursor` 内置搜索路径含 `/icons`（拼接到 XDG 数据目录之后），实测能加载。
   - `libXcursor` 实测也能从该目录加载。**注意**：它的 `XcursorLibraryPath()` 返回的字符串里
     *看不到* 这个目录，但实际仍能解析 —— 所以**不要凭路径字符串判断可用性，要实测**。
2. **加载器在主题缺失时会"回退到系统默认主题"并返回非 NULL，而不是报错。**
   因此任何加载验证都必须校验内容（帧数 / 热点 / 延迟），只看"是否加载成功"会把
   回退结果误判为成功。本项目验证时用帧数比对：`left_ptr`=23、`watch`=22、`hand2`=21。
3. 验证可用的两个真实加载器入口（脚本化，非项目依赖）：
   - `libXcursor.so.1` → `XcursorLibraryLoadImages(file, theme, size)`
   - `libwayland-cursor.so.0` → `wl_cursor_theme_load(theme, size, shm)` + `wl_cursor_theme_get_cursor`
     （需先用 `wl_proxy_marshal_flags` 取 `wl_shm`：Wayland ≥1.20 起 `wl_display_get_registry`
     等请求函数已改为头文件内联，不再是导出符号）

## 尺寸与显示缩放（清晰度关键）

素材只有 **32 / 48 / 64** 三档**原生**尺寸。合成器按

```
需求像素 = round(cursor-size × 显示器缩放 s)
```

取图；若该需求不落在原生档上，它只能拉伸现有档，**必然发虚**。所以清晰条件等价于：

```
需求像素 ∈ {32, 48, 64}        ⇔        cursor-size ≈ 原生档 ÷ s
```

以 **`s = 1.5`** 为例（通用示例，不是任何具体机器的参数）：

| `cursor-size` | 需求 | 命中原生档 | 结果 |
| ---: | ---: | --- | --- |
| 21 | 32px | 32 ✓ | 清晰 |
| 32 | 48px | 48 ✓ | 清晰 |
| 43 | 65px | 64 ✓ | 清晰 |
| 64 | 96px | 64 | 拉伸 1.50× 发虚 |

**具体数值必须现场实测，不要照抄任何人的数字**（AGENTS.md R3：仓库不记录真实系统参数）：

```bash
grep -o '<scale>[^<]*' ~/.config/monitors.xml | head -1   # 本机缩放因子（可能查不到）
gsettings get org.gnome.desktop.interface cursor-size      # 当前逻辑尺寸
```

**不用手算**：仓库自带脚本 [scripts/set-cursor-size.sh](../scripts/set-cursor-size.sh)，默认只读预览：

```bash
scripts/set-cursor-size.sh                  # 列出本机「原生 1:1」档位 + 上限内可用的最大档
scripts/set-cursor-size.sh --auto --yes     # 应用「清晰前提下尽量大」的那一档
scripts/set-cursor-size.sh --set 45 --yes   # 直接指定逻辑尺寸
scripts/set-cursor-size.sh --reset --yes    # 恢复系统默认
```

也可以按 `原生档 ÷ s` 手算候选值逐个试；`cursor-size` 改动立即生效，随时可回退。

> 两个推论：`s = 1` 时不存在这个问题；缩放越偏离整数，越容易踩中"需求落在原生档之外"。
> 这与转换质量无关 —— 素材原生档不够时，任何加载器都只能拉伸。

## 何时可以解除拦截

同 [assets/README.md](../assets/README.md)：取得上游书面许可并登记后方可入库。
