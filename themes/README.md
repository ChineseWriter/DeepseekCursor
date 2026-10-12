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

```bash
mkdir -p ~/.icons
cp -r themes/<theme-name> ~/.icons/
# Wayland 下由合成器读取；GNOME 可通过 gnome-tweaks 或 gsettings 选择光标主题
```

> 具体安装命令随首个可用版本一并补充并实测。

## 何时可以解除拦截

同 [assets/README.md](../assets/README.md)：取得上游书面许可并登记后方可入库。
