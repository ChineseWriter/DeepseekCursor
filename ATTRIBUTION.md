<!-- SPDX-License-Identifier: CC-BY-NC-SA-4.0 -->
<!-- Copyright (C) 2026 BigFatFish contributors -->

# 署名与许可（必读）

本仓库提供 **16 个可直接安装的 Linux/XCursor 光标主题**（[`themes/`](themes)）。
每一个都是**第三方美术作品的演绎作品**：本项目只做格式转换（Windows 动画光标 `.ani` → XCursor）
与安装工程，**未改动角色美术，也未新增动作**。

> **本仓库不是单一许可。** 不同来源的主题适用不同条件，**必须逐个主题查看**；
> 汇总视图见 [docs/SOURCES.md](docs/SOURCES.md)，每个主题目录内还有一份随包分发的
> `themes/<主题名>/ATTRIBUTION.md`。**对外分发某个主题时，必须原样携带该主题目录内的 `ATTRIBUTION.md`。**

## 1. 许可分组（按来源）

| 分组 | 主题 | 商用 | 必须做到 |
| --- | --- | --- | --- |
| **ZipZipPipe 非商业** | ClaudeOpus / ClaudeSonnet / ClaudeFable / Gemini / GLM / Grok / Kimi / Qwen / Seedream（9 个） | **禁止** | 署名 `ZipZipPipe` + 保留图库地址 <https://www.pixiv.net/artworks/148186519>；同一非商业条件传递给下游 |
| **上游非商业·作者未确认** | MiMo / Doubao（2 个） | **禁止** | **不得**把角色署名给 ZipZipPipe 或任何未确认作者；原样保留"原作者未确认"；非商业条件传递下游 |
| **大肥鱼项目署名许可 1.0** | DeepSeekWhale | 上游许可**允许含商用**（仅及于上游有权授权部分） | 署名 `作者：YunYueSama`、`仓库：https://github.com/YunYueSama/codex-deepseek-pet`，并保留完整许可文本（[themes/DeepSeekWhale/LICENSE-ART.txt](themes/DeepSeekWhale/LICENSE-ART.txt)） |
| **权利未确认** | ChatGPTDragon / AstraMint / SolMint（3 个） | **禁止** | 如实标注"权利未确认"，不声称已获授权；权利人主张即移除 |
| **CC-BY-NC-SA-4.0**（依形象链推断） | BigFatFish | **禁止** | 署名链（`@上善无形` → `@ZipZipPipe` → `4evergr8`）、非商业、相同方式共享 |

**任何情况下都不得声称这些主题可以商用。** DeepSeekWhale 的商用余地来自其上游许可，
且上游自己声明其社区参考图"原作者与授权尚待核实"，故该余地**只及于上游有权授权的部分**。

> **为什么 MiMo / Doubao 单独成组**：上游对这两个造型明确写了"未确认原始插画作者，不将它标注为
> ZipZipPipe 已确认作品"/"用户提供的参考"，因此**不能**把它们并进 ZipZipPipe 组、也不能替它们补一个作者。
> 把未经确认的归属写成已确认，是比"少标一个来源"更严重的错误。

## 2. 代码与本项目原创内容

| 范围 | 许可 | 全文 |
| --- | --- | --- |
| `tools/`、`install.sh` 等代码 | `AGPL-3.0-or-later` | [tools/LICENSE](tools/LICENSE) |
| 本项目原创文档、说明与预览图 | `CC-BY-NC-SA-4.0` | [LICENSE](LICENSE) |

## 3. 已知残余风险（如实声明）

1. **ZipZipPipe 组（9 个主题）**：上游图库只声明"允许保存、使用、署名、禁止商用"，**没有明确授予再分发**。
   上游仓库自身公开发布了这些二创包，本项目据此按"非商业社区分享"分发转换结果 —— 这是**推断**，不是明确授权。
2. **`MiMo` / `Doubao`（2 个主题）**：上游虽公开了包，但对这两个造型**未确认原始插画作者**
   （Doubao 为"用户提供的参考图"）。本项目不替其指定作者，原样保留该事实，并同样按非商业处理。
3. **ChatGPTDragon / AstraMint / SolMint**：上游对角色素材的权属自身就不确定（或未声明）。这三个主题的收录
   是项目所有者的明确决定，并已在主题内显著标注；权利人若提出异议，立即移除。
4. **BigFatFish**：即时上游（B 站视频页）未附许可声明且平台标记 `no_reprint`，判断依据是形象链上游的
   CC BY-NC-SA 4.0 声明与更上游 Linux 源主题的存在（见 [docs/PROVENANCE.md](docs/PROVENANCE.md) §6）。

以上四点都写进了对应的 `themes/<主题名>/ATTRIBUTION.md` 与 [docs/SOURCES.md](docs/SOURCES.md)，
不得因为"看起来没事"而在下游文档中删除或弱化。

## 4. 移除通道

任一权利人要求移除时，本项目将立即从仓库、Release 与一切派生分发中删除相关内容并停止分发，
并在提交信息中记录该请求与执行情况。流程详见 [THIRD-PARTY.md](THIRD-PARTY.md) §5。
