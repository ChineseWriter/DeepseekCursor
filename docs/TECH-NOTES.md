<!-- SPDX-License-Identifier: CC-BY-NC-SA-4.0 -->
<!-- Copyright (C) 2026 BigFatFish contributors -->

# 技术说明

这里记录实现与验证过程中**确认过的事实**，避免重复踩坑。面向想改造主题或用 `tools/` 重建的人。

## 1. 格式与转换

- 上游是 Windows 动画光标包：`anih`（9×u32 头）、可选 `rate`、可选 `seq `、`LIST fram` → 多个 `icon` 块。
  每帧是 32bpp `BI_RGB` DIB，装在 CUR 容器里，3 个目录项对应 32/48/64 三档。
- `biHeight` 是图像的 2 倍（XOR 位图 + 1bpp AND 掩码）；CUR 目录项复用了 `wPlanes` / `wBitCount` 字段存放热点。
- **alpha 全为 0 时**（本项目素材正是这种情况）透明度取自 AND 掩码，不能只看 alpha 通道。
- 输出的 XCursor：`Xcur` 头 + TOC（类型 `0xFFFD0002`、subtype = 标称尺寸）+ 每图 36 字节头 + 预乘 ARGB 像素。
  TOC 按标称尺寸排序，同一尺寸内保持帧顺序即形成动画。

## 2. 加载器实测（Ubuntu 26.04 / Wayland）

1. **`~/.local/share/icons/` 一个位置就够**，不需要再往 `~/.icons/` 放软链。
   - `libwayland-cursor` 的内置搜索路径含 `/icons`（拼接在 XDG 数据目录之后），实测可加载。
   - `libXcursor` 实测也能从该目录加载。**注意**：它的 `XcursorLibraryPath()` 返回值里*看不到*这个目录，
     所以**不要凭路径字符串判断可用性，要实测**。
2. **主题缺失时加载器会"回退到系统默认主题"并返回非 NULL，而不是报错。**
   因此验证必须校验内容（帧数 / 热点 / 延迟）；只看"是否加载成功"会把回退结果误判为成功。
   本项目用帧数比对：`left_ptr` = 23、`watch` = 22、`hand2` = 21。
3. 可用于脚本化验证的真实入口（非项目依赖）：
   - `libXcursor.so.1` → `XcursorLibraryLoadImages(file, theme, size)`
   - `libwayland-cursor.so.0` → `wl_cursor_theme_load(theme, size, shm)` + `wl_cursor_theme_get_cursor`
     （需先用 `wl_proxy_marshal_flags` 取 `wl_shm`：Wayland ≥ 1.20 起 `wl_display_get_registry`
     等请求函数改为头文件内联，不再是导出符号）

## 3. 尺寸与显示缩放（清晰度关键）

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

**具体数值必须现场实测，不要照抄任何人的数字**（[AGENTS.md](../AGENTS.md) R3：仓库不记录真实系统参数）：

```bash
grep -o '<scale>[^<]*' ~/.config/monitors.xml | head -1   # 本机缩放因子（可能查不到）
gsettings get org.gnome.desktop.interface cursor-size      # 当前逻辑尺寸
```

**不用手算**：仓库自带脚本 [set-cursor-size.sh](../tools/scripts/set-cursor-size.sh)，默认只读预览：

```bash
tools/scripts/set-cursor-size.sh                  # 列出本机「原生 1:1」档位 + 上限内最大档
tools/scripts/set-cursor-size.sh --auto --yes     # 应用「清晰前提下尽量大」的那一档
tools/scripts/set-cursor-size.sh --set 24 --yes   # 直接指定逻辑尺寸
tools/scripts/set-cursor-size.sh --reset --yes    # 恢复系统默认
```

也可以按 `原生档 ÷ s` 手算候选值逐个试；`cursor-size` 改动立即生效，随时可回退。

> 两个推论：`s = 1` 时不存在这个问题；缩放越偏离整数，越容易踩中"需求落在原生档之外"。
> 这与转换质量无关 —— 素材原生档不够时，任何加载器都只能拉伸。

## 4. 素材边界

仓库只在**本地**保留 Windows 原始素材（`assets/`，不入库）；对外分发的是转换后的 XCursor 主题，
按 [ATTRIBUTION.md](../ATTRIBUTION.md) 的署名与非商业条款发布。原始包不随仓库转发，
是为了避免**二次转发他人的原始分发物**。
