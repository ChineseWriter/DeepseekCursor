<!-- SPDX-License-Identifier: CC-BY-NC-SA-4.0 -->
<!-- Copyright (C) 2026 BigFatFish contributors -->

# 署名与许可（必读）

[`BigFatFish/`](BigFatFish) 光标主题是以下作品的**演绎作品**：本项目只做了格式转换
（Windows 动画光标 `.ani` → Linux/XCursor）与安装工程，**未改动美术**。

## 1. 原作与授权链

| 环节 | 作者 / 来源 | 说明 |
| --- | --- | --- |
| 原始角色形象 | **上善无形** | 「鲸鱼娘 / 大肥鱼」形象原作者 |
| 二创与授权声明 | **ZipZipPipe**（哔哩哔哩） | 公开声明该二创基于上善无形，并以 **CC BY-NC-SA 4.0** 授权（二创同协议） |
| Windows 光标包 | **4evergr8**（哔哩哔哩，视频 [BV1WypJ6WExu](https://www.bilibili.com/video/BV1WypJ6WExu)） | 本主题转换自该视频提供的 Windows 动画光标包 |
| 打包工具 | [clickgen](https://github.com/ful1e5/clickgen)（ful1e5） | 上游 Windows 包的生成工具；工具自身许可不影响美术权利归属 |
| 本仓库 | BigFatFish contributors | 格式转换、安装脚本与校验测试 |

取证记录、未核实项与残余风险见 [THIRD-PARTY.md](THIRD-PARTY.md) 与 [docs/PROVENANCE.md](docs/PROVENANCE.md)。

## 2. 许可（本仓库分层）

| 范围 | 许可 | 全文 |
| --- | --- | --- |
| `BigFatFish/` 主题美术、文档与说明 | **CC BY-NC-SA 4.0** | [LICENSE](LICENSE) |
| `tools/`、`install.sh` 等代码 | AGPL-3.0-or-later | [tools/LICENSE](tools/LICENSE) |

主题美术采用 CC BY-NC-SA 4.0，直接沿用上游授权链的约束。使用与分发你必须做到：

1. **署名**：完整保留上面第 1 条的署名链，不得移除、删减或篡改。
2. **非商业**：不得用于任何商业用途，不得二次贩卖。
3. **相同方式共享**：分发修改后的版本必须继续沿用 CC BY-NC-SA 4.0。

## 3. 已知残余风险（如实声明）

即时上游（4evergr8 的视频页）**没有许可声明**，且平台标记 `no_reprint`。
本仓库的判断依据是：其上游角色链公开声明为 CC BY-NC-SA 4.0（允许非商业再分发），
且该 Windows 包由 `clickgen` 自既有主题打包而来，说明存在更上游的 Linux 源主题
（见 [docs/PROVENANCE.md](docs/PROVENANCE.md) §6 的待核实项）。

换言之：**本主题按"允许非商业再分发"的理解发布，但这一环尚未获得即时上游的书面确认。**
一旦获得确认，本文件会更新；一旦权利人提出异议，立即移除（见下条）。

## 4. 移除通道

任一权利人要求移除时，本项目将立即从仓库、Release 与一切派生分发中删除相关内容，
并在提交信息中记录该请求与执行情况。流程详见 [THIRD-PARTY.md](THIRD-PARTY.md) §5；
可通过仓库 Issue 联系我们。
