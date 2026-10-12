<!-- SPDX-License-Identifier: CC-BY-NC-SA-4.0 -->
<!-- Copyright (C) 2026 BigFatFish contributors -->

# assets/ — 上游素材目录（**不入库**）

本目录是本项目**唯一的本地素材区**：既放原始压缩包（`大肥鱼.zip`），也放它的解包结果
（`.ani` / `.inf` / `.cur`）。仓库其他位置不应再出现 Windows 原始素材。

> 注意区分：**原始素材不入库**，但由它**转换出的 XCursor 主题已经入库**（根目录 `BigFatFish/`），
> 并按 CC BY-NC-SA 4.0 对外分发。这是刻意的分层（见下）。

## 为什么不入库

原始包是他人（B 站 UP `4evergr8`）的**分发物本身**：视频页无许可声明、平台标记 `no_reprint`。
直接把它转发进仓库，等于替他人二次分发他明确标注"禁止转载"的东西——这一层我们不做。
详见 [THIRD-PARTY.md](../THIRD-PARTY.md) 与 [docs/PROVENANCE.md](../docs/PROVENANCE.md)。

`.gitignore` 已强制拦截：

```
/assets/*
!/assets/README.md
*.ani
*.cur
```

## 那为什么转换后的主题可以入库

因为形象链上游（`ZipZipPipe` 声明、基于 `上善无形`）用的是 **CC BY-NC-SA 4.0** —— 该许可
**允许非商业的分发与改编**，条件是署名、相同方式共享、非商业。转换后的主题是这条链的演绎作品，
按同样条款发布是合规的；而原始包不属于我们的作品，没有理由替他人转发。

完整说明与残余风险见 [ATTRIBUTION.md](../ATTRIBUTION.md)。

## 本地使用

```bash
# 本地解包（assets/ 不入库，不会产生待提交内容）
unzip assets/大肥鱼.zip -d assets/
```

## 何时可以解除素材拦截

取得上游（尤其第 3 项发布者）**书面许可**后：把许可凭据记入 [THIRD-PARTY.md](../THIRD-PARTY.md)，
同步更新 `.gitignore` 与 [README.md](../README.md)，并在提交信息中说明。**在此之前不要用 `git add -f` 强行加入。**
