<!-- SPDX-License-Identifier: CC-BY-NC-SA-4.0 -->
<!-- Copyright (C) 2026 BigFatFish contributors -->

# assets/ — 上游素材目录（**不入库**）

本目录是本项目**唯一的本地素材区**，放两类东西：

| 路径 | 内容 | 用途 |
| --- | --- | --- |
| `大肥鱼.zip` / `BigFatFish/` | `BigFatFish` 的 Windows 原始包与其解包结果（`.ani` / `.inf` / `.bat`） | 构建 `themes/BigFatFish/` |
| `src/<仓库>/` | 上游 11 个光标仓库的**稀疏克隆**（只含选中的档位与元数据） | 构建 `themes/` 下 15 套 AI 娘主题 |
| `_meta/`（若存在） | 取证时的中间产物（视频元数据、许可文本副本） | 只作核对，可随时删 |

> 注意区分：**原始素材不入库**，但由它**转换出的主题已经入库**（`themes/`），
> 并按**各自来源的条件**对外分发（见 [docs/SOURCES.md](../docs/SOURCES.md)）。这是刻意的分层（见下）。

## 为什么不入库

- `BigFatFish` 的 Windows 包是他人（B 站 UP `4evergr8`）的**分发物本身**：视频页无许可声明、平台标记 `no_reprint`。
- `src/` 下是另一个发布者的**公开仓库内容**：仓库代码虽为 MIT，但角色美术的许可与代码不同，
  且原始仓库体量很大（含视频与预编译包）。直接转发进仓库既无必要，也会让仓库体积失控。

`.gitignore` 已强制拦截：

```
/assets/*
!/assets/README.md
*.ani
*.cur
```

## 那为什么转换后的主题可以入库

因为各来源公开声明了**可依据的条件**（署名 + 禁止商用 / 上游署名许可），转换后的主题是这条链的演绎作品，
按**该来源的条款**发布是合规的；而原始包不属于我们的作品，没有理由替他人转发。
**来源不同、条件不同**，所以每个主题目录内都带自己的 `ATTRIBUTION.md`。
完整说明与残余风险见 [docs/SOURCES.md](../docs/SOURCES.md) 与 [THIRD-PARTY.md](../THIRD-PARTY.md)。

## 本地使用

```bash
# 1) BigFatFish：解开本地压缩包
unzip assets/大肥鱼.zip -d assets/

# 2) 合集主题：稀疏拉取需要的档位（不下载整仓）
git clone --filter=blob:none --no-checkout --depth 1 \
  https://github.com/nibushiyigeren123-bot/<仓库>.git assets/src/<仓库>
git -C assets/src/<仓库> sparse-checkout init --no-cone
printf '/*.md\n/*.txt\n/LICENSE*\n/ASSET_LICENSE.md\n/cursors/*/32/\n/cursors/*/48/\n/cursors/*/64/\n/source/cursor_manifest.json\n' \
  > assets/src/<仓库>/.git/info/sparse-checkout
git -C assets/src/<仓库> checkout
# 更大档位按需追加：git -C assets/src/<仓库> sparse-checkout add '/cursors/*/128/'

# 3) 构建（在 tools/ 下）
cd tools && PYTHONPATH=src uv run python -m bigfatfish build --all
```

## 何时可以解除素材拦截

取得上游**书面许可**后：把许可凭据记入 [THIRD-PARTY.md](../THIRD-PARTY.md)，
同步更新 `.gitignore` 与 [README.md](../README.md)，并在提交信息中说明。**在此之前不要用 `git add -f` 强行加入。**
