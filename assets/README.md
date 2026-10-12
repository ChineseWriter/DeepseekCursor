<!-- SPDX-License-Identifier: CC-BY-NC-SA-4.0 -->
<!-- Copyright (C) 2026 BigFatFish contributors -->

# assets/ — 上游素材目录（**不入库**）

本目录是本项目**唯一的本地素材区**：既放原始压缩包（`大肥鱼.zip`），也放它的解包结果
（`.ani` / `.inf` / `.cur`）。仓库其他位置不应再出现上游素材。

## 为什么不入库

上游未授予再分发许可（详见 [THIRD-PARTY.md](../THIRD-PARTY.md) 与 [docs/PROVENANCE.md](../docs/PROVENANCE.md)）。把素材提交进 Git 即构成再分发。

`.gitignore` 已强制拦截：

```
/assets/*
!/assets/README.md
*.ani
*.cur
```

## 本地使用

```bash
# 本地解包（不生成待提交内容）
unzip assets/大肥鱼.zip -d assets/
```

## 何时可以解除拦截

取得上游书面许可后：把许可凭据记入 [THIRD-PARTY.md](../THIRD-PARTY.md)，同步更新 `.gitignore`、[README.md](../README.md) 许可表，并在提交信息中说明。**在此之前不要用 `git add -f` 强行加入。**
