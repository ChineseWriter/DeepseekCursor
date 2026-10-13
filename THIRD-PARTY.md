<!-- SPDX-License-Identifier: CC-BY-NC-SA-4.0 -->
<!-- Copyright (C) 2026 BigFatFish contributors -->

# 第三方素材与服务 — 权属、署名与合规

本文件记录本项目**不拥有**的第三方内容。凡外部素材、代码、字体、图标，在合入前必须在此登记；
未登记不得合入（见 [AGENTS.md](AGENTS.md) §8）。**逐主题的许可结论见 [docs/SOURCES.md](docs/SOURCES.md)。**

**结论先行：本仓库 16 个主题的美术层都不是我们的，而且来源不止一条、条件也各不相同。**
形象链与上游仓库的许可状态互不相同，因此本仓库采取**分层 + 逐主题标注**的做法：

| 层 | 做法 | 理由 |
| --- | --- | --- |
| Windows 原始素材与上游仓库内容（`assets/`） | **不入库**、不转发 | 那是他人的分发物本身：可能带 `no_reprint` 标记，或根本没有许可声明 |
| 转换后的 XCursor 主题（[`themes/<主题名>/`](themes)） | **入库**，按**该主题自己的来源条件**分发，目录内附 `ATTRIBUTION.md` | 它是形象链的演绎作品；条件不同就不能一概而论 |
| 本项目原创的工具与文档 | 代码 `AGPL-3.0-or-later`；文档 `CC-BY-NC-SA-4.0` | 见 [AGENTS.md](AGENTS.md) §8.1 |

**除 `DeepSeekWhale` 依其上游许可外，一律禁止商业使用；署名不得移除。**

---

## 1. 第三方内容清单

| # | 内容 | 权利人（公开标识） | 来源 | 权利状态 | 处理 |
| --- | --- | --- | --- | --- | --- |
| 1 | 「鲸鱼娘 / 大肥鱼」角色形象（原始） | B 站用户 `上善无形` | B 站动态 `1231980045693616162` | **未核实**（原始条款待确认） | 未直接使用其文件；署名链最上游 |
| 2 | 「鲸鱼娘 / 大肥鱼」二创形象 | B 站 UP `ZipZipPipe`（`mid=4168597`） | <https://space.bilibili.com/4168597> | 公开声明：依 **CC BY-NC-SA 4.0** 非商业使用，「二创同协议授权」 | `BigFatFish` 的许可依据 |
| 3 | **ZipZipPipe 原始图库**（Claude 设定 / Gemini / Kimi / GLM / Grok / Seedream / Qwen 等角色设定） | Pixiv 用户 `ZipZipPipe` | <https://www.pixiv.net/artworks/148186519> | 公开条件：**允许保存、使用，须注明作者，禁止商业使用**；**未授予再许可** | **9 个主题**的角色来源；按非商业社区分享分发转换结果（推断，非明确授权） |
| 3b | 「MiMo」「豆包」两个造型的**角色原画** | **未确认** | 上游 `mimo-cursors` / `bytedance-cursors` 的 `ASSET_LICENSE.md` 自述 | 上游明确：MiMo"未确认这一具体造型的原始插画作者，**不将它标注为 ZipZipPipe 已确认作品**"；豆包为"**用户提供的**短发全身参考" | 属**独立分组**（上游非商业·作者未确认）：不得署名给任何未确认作者，禁止商用，原样保留"作者未确认" |
| 4 | `codex-deepseek-pet`（DeepSeek 小鲸鱼素材） | `YunYueSama` | <https://github.com/YunYueSama/codex-deepseek-pet> | **大肥鱼项目署名许可 1.0**（自定义）：允许使用/修改/分享，**含商用**，须署名 + 保留完整许可文本 | `DeepSeekWhale` 的来源；主题内附 `LICENSE-ART.txt` |
| 5 | 11 个 Windows 光标包仓库（`.ani` / 生成脚本 / PNG 帧） | GitHub `nibushiyigeren123-bot` | 见 [docs/SOURCES.md](docs/SOURCES.md) §1 | 代码为 **MIT**（`LICENSE-CODE`，明确"仅代码、不含角色美术与品牌标识"）；素材条件见第 3/4/6 项 | 原始仓库**不入库**；转换后的主题入库 |
| 6 | ChatGPT 龙娘参考图 | 知乎 `@光影随云飞`（署名仅见于上游自述） | 上游仓库 `ASSET_LICENSE.md` 自述 | **原作者身份与授权范围未确认** | 收录但**显著标注未确认**（见 [docs/SOURCES.md](docs/SOURCES.md) §2.3） |
| 7 | Astra / sol 角色身份参考 | 上游自述来自用户提供截图与 B 站 `BV1xSa76yEqZ` | 上游仓库 `README.md` / 视频简介 | **未确认**；上游仓库无素材许可文件 | 同上，标注未确认 |
| 8 | Windows 动画光标包 **BigFatFish** | B 站 UP `4evergr8` | <https://www.bilibili.com/video/BV1WypJ6WExu/> | 视频页**无许可声明**；平台元数据 `no_reprint=1` | 原始包**不入库**；由它转换出的主题按 CC BY-NC-SA 4.0 入库 |
| 9 | 同系列其他光标分发版本（旁证） | B 站 UP `John_milk` 等 | <https://www.bilibili.com/video/BV1cqhg62E9a/> | 权利人声明：「免费分享，**仅供个人使用，禁止二次贩卖**」 | 未使用，仅作社区惯例旁证 |
| 10 | Windows 包生成工具 `clickgen` | `ful1e5` | <https://github.com/ful1e5/clickgen> | MIT（工具许可不影响美术权利归属） | 仅记录线索，未复制其代码 |
| 11 | 上游展示视频背景音乐 `放課後アフタースクール` | 作曲 `watson` / MusMus | <https://musmus.main.jp/> | 按 MusMus 使用规则署名；**非音乐素材再分发** | 本项目**未使用**该音乐；仅视频含有 |
| 12 | XCursor 格式与系统加载器 | freedesktop.org / Wayland 项目 | 系统库 `libXcursor`、`libwayland-cursor` | 系统组件；本项目**仅调用，未复制其代码** | 无许可义务需传递 |

> 表中列出的是**第三方公开创作者标识**，仅用于署名与授权联络，属 [AGENTS.md](AGENTS.md) R3 明确允许的例外。
> 本项目维护者本人的社交账号、托管账号名与仓库 URL 不在仓库中出现。
>
> 附注（上游元数据核查）：上游 11 个仓库**共用同一份 `LICENSE-CODE` 模板**，其版权行统一写作
> "Astra & sol cursor contributors"（即使主题与该角色无关）；这属于上游模板文字，不影响它
> "许可仅覆盖代码"的适用范围，也不构成对素材的授权。
>
> **注意**：第 3 项与第 3b 项不能混为一谈 —— 把 MiMo / 豆包并入 ZipZipPipe 组、给它们补一个
> "已确认作者"，是本项目曾经犯过并已修正的错误（见 §6 变更记录）。

## 2. 分层决定及其理由

1. **原始分发物一律不入库。** 上游仓库内容是他人（`nibushiyigeren123-bot`）的分发物本体；
   `BigFatFish` 的直接来源还被平台标记禁止转载。"免费下载"不等于"授权再分发"。
2. **转换后的主题按各自来源条件入库。** 逐主题条件见 [docs/SOURCES.md](docs/SOURCES.md) §2：
   有的来自公开的"署名 + 禁止商用"条件，有的来自允许含商用的自定义许可，有的权利未确认，
   还有两个是"上游非商业但**角色作者未确认**"——最后这一类**不得**被并进有明确署名依据的分组。
3. **来源不同就不能套同一份许可。** 把 `DeepSeekWhale` 的宽松条件套到 ZipZipPipe 组，
   或者把"未确认"当成"已授权"，都会造成权利状态误导。
4. **社区惯例是旁证不是授权。** 同类分发普遍为"免费 + 仅个人使用 + 禁止转售"，与本项目的非商业定位一致，
   但它不能替代权利人自己的许可。

## 3. 仍建议取得的许可（**不阻塞入库，但应继续争取**）

- 向 `ZipZipPipe` 确认：是否允许**再分发**基于其图库制作的派生光标主题，以及署名格式；
- 向 `nibushiyigeren123-bot` 确认：仓库中的素材是否可由第三方再分发（转换后的形式）；
- 向 `YunYueSama` 确认：其署名许可适用于"由他人转换格式后的派生主题"（当前按许可文本字面理解）；
- 对 `ChatGPTDragon` / `AstraMint` / `SolMint`：确认原始角色权利人，或取得"不再分发"的处理意见。

取得后：把凭据（时间、方式、原文）记入本文件与 [docs/SOURCES.md](docs/SOURCES.md)，
同步更新对应主题的 `ATTRIBUTION.md`，并在提交信息中说明。

## 4. 分发时必须携带的署名声明

每个主题目录内的 `ATTRIBUTION.md` 就是该主题必须携带的声明（**随包分发，不得删除**）。
主题级最小署名要求见 [docs/SOURCES.md](docs/SOURCES.md) §2 各组条目；`DeepSeekWhale` 还需携带
`themes/DeepSeekWhale/LICENSE-ART.txt` 的完整许可文本。

## 5. 移除通道（takedown）

任一权利人若要求移除，本项目将：立即从仓库、Release 与一切派生分发中删除相关内容、停止分发，
并在提交信息中记录该请求与执行情况。由于**原始素材本就不在仓库中**，
该操作通常等同于删除 `themes/<主题名>/` 目录并撤销相关文档引用。

## 6. 变更记录

| 日期 | 变更 |
| --- | --- |
| 2026-10-12 | 建立本文件；确认即时来源未授予再分发许可，初版结论：素材与派生图像**均不入库** |
| 2026-10-12 | 本地素材统一收敛到 `assets/`；`.gitignore` 同步加固 |
| 2026-10-12 | **修订结论**：区分"原始包"与"演绎作品"，`BigFatFish` 改为**入库并按 CC BY-NC-SA 4.0 分发** |
| 2026-10-13 | **扩充为多来源**：纳入 B 站合集 15 个角色（11 个上游仓库），新增"逐主题许可分组"；登记 ZipZipPipe 图库、`YunYueSama` 署名许可、以及 3 个"权利未确认"主题及其处理方式 |
| 2026-10-13 | **依两份独立只读审计修正**：`MiMo` 与 `Doubao` 曾被错误并入 ZipZipPipe 组并被要求署名 `ZipZipPipe`（上游明确"不将它标注为 ZipZipPipe 已确认作品"/"用户提供的参考"）。现拆为独立分组"上游非商业·作者未确认"（第 3b 项），主题文件、总表、README 与工具清单同步；并补登 `Doubao`/`MiMo`，修正 `LICENSE-CODE` 附注范围（11 个仓库共用同一模板） |
