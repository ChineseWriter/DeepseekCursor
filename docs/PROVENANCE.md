<!-- SPDX-License-Identifier: CC-BY-NC-SA-4.0 -->
<!-- Copyright (C) 2026 BigFatFish contributors -->

# 素材来源取证记录（Provenance）

**取证日期**：2026-10-12（BigFatFish）／2026-10-13（合集 15 个角色） ｜
**取证方式**：B 站公开 API 与公开页面 + 上游 GitHub 仓库的文件与许可声明 + 本地素材结构核查

> **R3 合规说明**：本文件所有来源链接均已**剥离跟踪参数**（`spm_id_from`、`vd_source`、`share_session_id`、
> `unique_k`、`timestamp` 等）。原始分享链接中带有账号级跟踪标识，一律不记录、不入库。

---

## 1. 本轮新增：合集取证

| 项 | 值 |
| --- | --- |
| 合集入口 | B 站合集「AI形象动态指针」：`https://space.bilibili.com/12103198/lists/5181075`（`type=series`） |
| 规模 | **11 个视频 / 11 个上游仓库 / 15 个角色主题** |
| 取证方式 | ① 列表 API 取合集条目；② 逐视频 `view` API 取**完整简介**；③ 从简介提取 GitHub 仓库地址；④ 逐仓库读取 `ASSET_LICENSE.md` / `LICENSE-CODE` / `README.md` |
| 素材形态 | 每个仓库：`cursors/<角色>/<档位>/<角色状态>.ani`（**17 个 Windows 角色 × 32/48/64/128/256 五档**）、`source/cursor_manifest.json`（状态、热点、帧数、时长）、生成脚本、预览与海报 |
| 视频与仓库对应 | 见 [SOURCES.md](SOURCES.md) §1 一览表 |
| 许可差异 | **同一发布者的 11 个仓库，素材条件并不相同**（合计 15 个主题）：**9 个**依 ZipZipPipe 图库的"署名 + 禁止商用"；**2 个**（`MiMo`、`豆包`）上游声明为非商业分享但**角色原始插画作者未确认**；**1 个**（DeepSeek）依 `YunYueSama` 的署名许可；另有 **3 个**主题的角色权利未确认 |

**取证时确认的关键事实**：

1. 上游简介明确写了"仓库与源码"地址，说明**上游自身以公开仓库分发**这些光标包；
2. 上游 `LICENSE-CODE` 为 MIT，并在文件尾明确 `Scope: code only; excludes character artwork and brand marks.`
   —— **代码许可不覆盖角色美术**，所以不能拿 MIT 当成素材许可；
3. `ASSET_LICENSE.md` 逐仓库给出角色来源：`ZipZipPipe` 图库页码、用户提供的参考图、或"原作者尚未确认"；
4. 上游成品的帧结构经本项目独立解码核实：每档 17 个角色、每角色 4–12 帧、帧时长 100/117/133/200 ms，
   热点随档位缩放（例：32px→(0,1)、64px→(1,1)、256px→(4,4)）。

**素材获取方式（可复现，不把仓库内容入库）**：用 git 稀疏部分克隆，只取需要的档位：

```bash
git clone --filter=blob:none --no-checkout --depth 1 \
  https://github.com/nibushiyigeren123-bot/<仓库>.git assets/src/<仓库>
git -C assets/src/<仓库> sparse-checkout init --no-cone
printf '/*.md\n/*.txt\n/LICENSE*\n/ASSET_LICENSE.md\n/cursors/*/32/\n/cursors/*/48/\n/cursors/*/64/\n/source/cursor_manifest.json\n' \
  > assets/src/<仓库>/.git/info/sparse-checkout
git -C assets/src/<仓库> checkout
# 更大档位按需追加：git -C assets/src/<仓库> sparse-checkout add '/cursors/*/128/'
```

## 2. 本地素材（均不入库，见 `.gitignore`）

| 项 | 值 |
| --- | --- |
| `assets/大肥鱼.zip` | 4.4 MB，BigFatFish 的 Windows 原始包；解包结果 `assets/BigFatFish/` |
| `assets/src/<仓库>/` | 上述 11 个上游仓库的稀疏克隆（只含被选中的档位与元数据） |
| BigFatFish 内容 | 11 个 `.ani` 动画光标 + `install.inf` + `uninstall.bat` |
| BigFatFish 生成工具线索 | `install.inf` 自述由 `clickgen` 生成（<https://github.com/ful1e5/clickgen>） |
| BigFatFish 主题名 | `uninstall.bat` 清理的注册表方案名为 **`BigFatFish Cursors`** |
| **元数据核查结论** | `install.inf`、`uninstall.bat`、11 个 `.ani` 的 RIFF `LIST INFO` / `ISFT` / `IART` / `INAM` **均无**作者、许可或来源信息；上游合集的 `.ani` 同样不含权利信息（权利只能依据外部声明） |

## 3. 直接来源（BigFatFish）

| 项 | 值 |
| --- | --- |
| 平台 / 标识 | B 站视频 `BV1WypJ6WExu` |
| 链接（已脱敏） | `https://www.bilibili.com/video/BV1WypJ6WExu/` |
| 标题 | 完全免费，大肥鱼全动态鼠标指针 |
| 发布者 | `4evergr8` |
| 发布时间 | 2026-10-11（与压缩包时间戳一致） |
| `copyright` | `1`（平台字段：自制） |
| `no_reprint` | **`1`（平台字段：禁止转载）** |
| `desc` | `-`（**无任何许可声明**） |

同发布者的相关工作：`BV1NapP67EbX`《大肥鱼鼠标指针制作中，0手工，纯AI》，同样 `no_reprint=1`、`desc` 为空。

## 4. 形象链上游

`ZipZipPipe`（B 站，`mid=4168597`）在其视频简介中的**公开声明原文**：

> 申明：本视频鲸鱼娘形象基于 @上善无形 原创角色二创（源：b23.tv/Kn7yvnF），依 **CC BY-NC-SA 4.0** 非商业使用，
> **二创同协议授权**，完整声明见主页。

其**原始图库**（合集里 11 个主题的角色来源）地址为 <https://www.pixiv.net/artworks/148186519>，
公开条件为"允许保存、使用，要求注明作者，禁止商业使用"。

`YunYueSama` 的 [codex-deepseek-pet](https://github.com/YunYueSama/codex-deepseek-pet) 采用其自定义的
「大肥鱼项目署名许可 1.0」：允许使用、修改、分享（含商用），须署名并保留完整许可文本。

## 5. 同类分发的社区惯例（旁证）

B 站 `John_milk` 的 `BV1cqhg62E9a`《【Deepseek·大肥鱼】十七款动态鼠标指针免费分享啦》简介原文：

> 所有指针均为个人制作，免费分享，**仅供个人使用，禁止二次贩卖** / 适用于 Windows 系统 / 通过网盘分享…

即同类分发普遍为"免费 + 仅个人使用 + 禁止转售"，**无一份提供再分发或再许可授权**。

## 6. 结论

| 问题 | 结论 |
| --- | --- |
| 我们是否有权对素材施加自选 CC 许可？ | **否。** 素材权利属第三方，我们只是获取者。 |
| 上游允许的许可范围是什么？ | **逐来源不同**：ZipZipPipe 图库 = 署名 + 禁止商用；`YunYueSama` = 署名许可（含商用）；3 个主题权利未确认；BigFatFish 直接来源未授予任何许可且标记禁止转载。 |
| 因此本项目采用？ | 代码 `AGPL-3.0-or-later`；本项目原创文档 `CC-BY-NC-SA-4.0`；主题美术**逐主题**按各自来源条件分发（见 [SOURCES.md](SOURCES.md)）；**原始素材不入库、不转发**。 |
| 转换后的主题能否对外分发？ | **依来源而定**：ZipZipPipe 组按"非商业社区分享"（推断，非明确授权）；`DeepSeekWhale` 依其署名许可；3 个未确认主题已显著标注、权利人主张即移除。 |
| 能否商用 / 进发行版官方仓库？ | **整体不能**：多数来源为 NC 或未确认，不满足自由软件定义（DFSG/OSI）。**不得**作此声称；`DeepSeekWhale` 的商用余地只来自其上游许可。 |

## 7. 待核实项

- [x] `install.inf` / `uninstall.bat` / `.ani` 内是否含作者署名、联系方式或原始来源信息 → **均无**（见 §2）。
- [x] 合集的 11 个仓库是否有素材许可声明 → **已逐仓库读取**；结论与差异见 [SOURCES.md](SOURCES.md) §2。
- [ ] 原始角色（`上善无形`，动态 `1231980045693616162`）的具体许可条款与署名要求。
- [ ] `ZipZipPipe` 图库的条件是否覆盖**光标素材本身**（其声明语境为角色形象），以及是否允许再分发派生主题。
- [ ] `4evergr8` 是否为 BigFatFish 光标素材的原创者，抑或转载方（`copyright=1` 为发布者自行勾选，不能作为权属证明）。
- [ ] `ChatGPTDragon` / `AstraMint` / `SolMint` 的原始角色权利人。
- [ ] `MiMo` 与 `豆包` 的原始插画作者（上游明确"未确认"，Doubao 为"用户提供的参考图"）。
  **在确认之前，任何文档都不得把这两个造型署名给 `ZipZipPipe` 或其他人** —— 这一点曾被本项目写错并已修正。
- [ ] `nibushiyigeren123-bot` 是否允许第三方以转换后的形式再分发其素材。
- [ ] 素材由 AI 生成（上游自述"0手工，纯AI"/"绘制姿态加八相位二维微动"）。**注意**：AI 生成内容本身在某些法域可能
  不受著作权保护，但其**角色形象**仍可能受上游人设权利约束。故一律采取保守策略，不因"AI 生成"而放松限制。
- [ ] **BigFatFish 最高价值线索**：其 Windows 包由 `clickgen` 打包而成，说明上游可能存在一个**原始 XCursor 主题**
  （或 PNG 帧工程）。若定位到它，可能直接获得更清晰的许可与更大分辨率素材。
  检索方向：`clickgen` 构建产物特征、主题名 `BigFatFish`、社区通称 `Whalechan`。

## 8. 变更记录

| 日期 | 变更 |
| --- | --- |
| 2026-10-12 | 首次取证；因直接来源未授予再分发许可，形成"素材与派生图像均不入库"的初版结论 |
| 2026-10-12 | 补充 `clickgen` 生成工具线索（§2）；新增"追溯原始 XCursor 主题"待核实项 |
| 2026-10-12 | 补充上游工程名线索 `Whalechan` |
| 2026-10-12 | 依独立安全审计结论复核：全历史无任何提交新增/删除过素材与派生图像，**从未进入 Git** |
| 2026-10-12 | 补做素材元数据核查（`install.inf` / `uninstall.bat` / RIFF INFO）→ **均无权利信息** |
| 2026-10-12 | **修订结论**：区分"原始素材"与"演绎作品"；转换后的主题入库分发，原始素材仍不入库 |
| 2026-10-13 | **新增合取证（§1）**：11 个上游仓库 / 15 个角色、稀疏克隆获取方式、逐仓库许可差异；来源与许可结论迁至 [SOURCES.md](SOURCES.md) 统一维护 |
