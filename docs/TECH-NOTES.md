<!-- SPDX-License-Identifier: CC-BY-NC-SA-4.0 -->
<!-- Copyright (C) 2026 BigFatFish contributors -->

# 技术说明

这里记录实现与验证过程中**确认过的事实**，避免重复踩坑。面向想改造主题或用 `tools/` 重建的人。

## 1. 格式与转换

- 上游是 Windows 动画光标包：`anih`（9×u32 头）、可选 `rate`、可选 `seq `、`LIST fram` → 多个 `icon` 块。
- 单帧是 32bpp `BI_RGB` DIB，装在 CUR 容器里；CUR 目录项复用 `wPlanes` / `wBitCount` 存放热点。
  `biHeight` 是图像的 2 倍（XOR 位图 + 1bpp AND 掩码）。
- **alpha 全为 0 时**（本项目的素材正是这种情况）透明度取自 AND 掩码，不能只看 alpha 通道。
- 两种素材布局都要支持，`tools/src/bigfatfish/catalog.py` 用路径模板区分：
  - **单文件多档**：一个 `.ani` 里的每一帧自带多个分辨率（`BigFatFish`：`install.inf` 声明的 11 个角色，
    每帧含 32/48/64，帧数 18–26）；
  - **按档分文件**：`cursors/<角色>/<档位>/<状态>.ani`（合集 15 个主题：17 个角色 × 每档一个文件，
    帧数 4–12、时长 100/117/133/200 ms）。
  按档布局在构建时会校验**各档帧数一致**，不一致直接报错 —— 否则切档时动画会跳。
- 输出的 XCursor：`Xcur` 头 + TOC（类型 `0xFFFD0002`、subtype = 标称尺寸）+ 每图 36 字节头 + 预乘 ARGB 像素。
  TOC 按标称尺寸排序，同一尺寸内保持帧顺序即形成动画。**不做插值放大**：只写素材原生的标称尺寸。

## 2. 加载器实测（Ubuntu 26.04 / Wayland）

### 2.1 搜索路径：两个加载器不一样（实测）

| 加载器 | 谁在用 | 内置默认搜索路径（库内字符串实测） | 含 `~/.local/share/icons`？ |
| --- | --- | --- | --- |
| `libwayland-cursor` | **Wayland 桌面**（mutter / GTK） | `$XDG_DATA_HOME/icons:~/.icons:/usr/share/icons:/usr/share/pixmaps:~/.cursors:/usr/share/cursors/xorg-x11:…` | **含**（`XDG_DATA_HOME` 缺省为 `~/.local/share`） |
| `libXcursor` | X11 / XWayland 应用 | `~/.icons:/usr/share/icons:/usr/share/pixmaps` | **不含** |

实测（同一主题安装在 `$XDG_DATA_HOME/icons`；库版本随发行版更新，不在仓库记录具体版本号）：

- `XcursorFilenameLoadAllImages(文件)` —— **按文件路径加载正常**：17 个主题 × 17 光标的全部档位都能读出，
  帧数与热点与源素材一致（本项目用它做独立校验）。
- `XcursorLibraryLoadImages(名字, 主题名, 尺寸)` —— **按主题名解析会失败**并**回退到系统默认主题**
  （实测命中 Adwaita：`watch` 60 帧、`person` 不存在），且**不报错**。
- 显式设置 `XCURSOR_PATH=$HOME/.local/share/icons` 后，同一个调用 8/8 命中本主题。
  单独设置 `XDG_DATA_HOME` 对 `libXcursor` **没有帮助**（实测仍是回退结果）。

**结论**：把主题装在 `$XDG_DATA_HOME/icons/<主题名>/` 对 **Wayland 桌面足够**；
若要让**只走 `libXcursor` 的 X11 应用**也命中，需要把它们纳入搜索路径（设 `XCURSOR_PATH`，
或在 `~/.icons/` 下放一个同名软链）。**不要凭"是否加载成功"判断** —— 回退也会返回非 NULL。

> 修订记录：本文件早期版本只写了"`libXcursor` 实测也能从该目录加载"，那是**按文件路径**加载的结论；
> 2026-10-13 补测了**按主题名**解析，发现它默认不搜索 `~/.local/share/icons`，故按上表更正。

### 2.2 验证方法

- 快而全的校验用**独立实现的解析器**（`tools/tests/_xcur_ref.py`，不复用写出代码）：
  校验 `ntoc`、标称尺寸集合、各档帧数一致、热点在图像范围内、延迟 > 0、别名软链可解析。
- 端到端校验用系统真库（非项目依赖）：
  - `libXcursor.so.1` → `XcursorFilenameLoadAllImages`（按文件）
  - `libwayland-cursor.so.0` → `wl_cursor_theme_load(theme, size, shm)` + `wl_cursor_theme_get_cursor`
    （需先用 `wl_proxy_marshal_flags` 取 `wl_shm`：Wayland ≥ 1.20 起 `wl_display_get_registry`
    等请求函数改为头文件内联，不再是导出符号）
- **主题缺失时加载器会"回退到系统默认主题"并返回非 NULL**：所以验证必须校验内容（帧数 / 热点 / 延迟），
  只看"是否加载成功"会把回退结果误判为成功。

## 3. 尺寸与显示缩放（清晰度关键）

上游素材提供 **32 / 48 / 64 / 128 / 256** 五档原生像素；本仓库**入库 32 / 48 / 64**，
更大档按需本地构建（`--sizes 32,48,64,128`），理由是入库五档会让仓库体积增加一个数量级。
`BigFatFish` 的上游包只有 32/48/64 三档。

合成器按

```
需求像素 = round(cursor-size × 显示器缩放 s)
```

取图；若该需求不落在主题持有的原生档上，它只能拉伸，**必然发虚**。所以清晰条件等价于：

```
需求像素 ∈ 该主题的原生档集合        ⇔        cursor-size ≈ 原生档 ÷ s
```

清晰取值是「原生档 ÷ s」的整数近似，与**你自己的** `s` 有关，所以仓库只给判据、不给数字：

```
记 s = 你的显示器缩放，N = 主题持有的原生档集合（本仓库入库的合集主题为 {32,48,64}）

清晰：cursor-size ∈ { round(n / s) : n ∈ N }   —— 需求像素恰好命中某个原生档
发虚：cursor-size ∉ 该集合                      —— 合成器只能拉伸现有档
```

举例说明**结构**（不含任何具体机器的缩放值）：`s` 为 1 时可选值就是原生档本身；`s` 为 2 时可选值减半；
`s` 为非整数时可选值更稀疏、且容易落到两档之间。**不要照抄任何人的数字**，用下面的命令实测你机器上的值
（[AGENTS.md](../AGENTS.md) R3：仓库不记录真实系统参数）：

```bash
grep -o '<scale>[^<]*' ~/.config/monitors.xml | head -1   # 本机缩放因子（可能查不到）
gsettings get org.gnome.desktop.interface cursor-size      # 当前逻辑尺寸
```

**不用手算**：仓库自带脚本 [set-cursor-size.sh](../tools/scripts/set-cursor-size.sh)，默认只读预览：

```bash
tools/scripts/set-cursor-size.sh                  # 列出「原生 1:1」档位 + 上限内最大档
tools/scripts/set-cursor-size.sh --auto --yes     # 应用「清晰前提下尽量大」的那一档
tools/scripts/set-cursor-size.sh --set 24 --yes   # 直接指定逻辑尺寸
tools/scripts/set-cursor-size.sh --reset --yes    # 恢复系统默认
# 安装的是含 128 档的版本时，把原生档一并告诉脚本：
tools/scripts/set-cursor-size.sh --native 32,48,64,128
```

> 两个推论：`s = 1` 时不存在这个问题；缩放越偏离整数，越容易踩中"需求落在原生档之外"。
> 这与转换质量无关 —— 素材原生档不够时，任何加载器都只能拉伸。

## 4. 预览图的生成

`themes/<主题名>/preview.png` 由 `build` 一起生成，**只使用本主题自己的帧**（直通 alpha 合成到深色底），
不引用上游图片、视频截图或外部工具；因此需要时可随时重建：

```bash
cd tools && PYTHONPATH=src uv run python -m bigfatfish build --all
```

布局是确定的：每个角色一列，列内是采样的首/中/末三帧，单元格边长 = 该主题最大的入库档，
所以同一主题每次生成的 PNG 完全一致（`tools/src/bigfatfish/preview.py`，纯标准库写 PNG）。

## 5. 素材边界

仓库只在**本地**保留 Windows 原始素材与上游仓库的稀疏克隆（`assets/`，不入库，见
[assets/README.md](../assets/README.md)）；对外分发的是转换后的 XCursor 主题，
按 [ATTRIBUTION.md](../ATTRIBUTION.md) 与各主题目录内的 `ATTRIBUTION.md` 的条款发布。
原始包不随仓库转发，是为了避免**二次转发他人的原始分发物**。
