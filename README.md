<!-- SPDX-License-Identifier: CC-BY-NC-SA-4.0 -->
<!-- Copyright (C) 2026 BigFatFish contributors -->

# 大肥鱼（BigFatFish）光标主题 · Ubuntu 26.04 / Wayland 移植

把 Windows 动画光标主题（`.ani` + `install.inf`）转换为 **Ubuntu 26.04 LTS / Wayland** 下可直接使用的 XCursor 主题。

| | |
| --- | --- |
| 状态 | **可用**：转换器已实现，43 项测试 + 视觉验证通过；等待安装测试 |
| 目标平台 | Ubuntu 26.04 LTS，Wayland 会话 |
| 技术栈 | Python 3.11+（**零第三方依赖**），由 [`uv`](https://docs.astral.sh/uv/) 管理 |
| 协作规约 | [AGENTS.md](AGENTS.md)（R1 Git / R2 uv / R3 隐私零暴露 / R4 最小改动 / R5 工作区外改动须汇报） |

---

## 许可总览

**本仓库不是单一许可**，按内容范围分别授权：

| 范围 | 许可（SPDX） | 全文 |
| --- | --- | --- |
| 源代码（`src/`、`scripts/`、`tests/`、构建与转换工具） | `AGPL-3.0-or-later` | [LICENSE](LICENSE) |
| 本项目原创的非代码内容（文档、说明、配置、注释） | `CC-BY-NC-SA-4.0` | [LICENSE-CC-BY-NC-SA-4.0](LICENSE-CC-BY-NC-SA-4.0) |
| 上游光标美术素材及其派生图像 | **第三方权利，本仓库不收录、不授予任何许可** | 见 [THIRD-PARTY.md](THIRD-PARTY.md) |

新增文件必须带 SPDX 头（约定见 [AGENTS.md §8](AGENTS.md)）。

### 为什么非代码层用 CC BY-NC-SA 4.0 而不是 CC BY-SA

因为上游授权链本身就是 **非商业 + 相同方式共享**（其权利人公开声明原文见 [docs/PROVENANCE.md](docs/PROVENANCE.md)）。本项目的产物美术层是该链条的演绎作品，只可能合法地按"非商业 + 相同方式共享"存在。若把文档层标成允许商业使用的 CC BY-SA，会给使用者一个与实际权利状态不符的信号。

若将来替换为**完全自有**的美术，非代码层可放宽为 `CC-BY-SA-4.0`；那是一处一次性改动，须同步更新本表、`LICENSE-CC-BY-NC-SA-4.0` 与 [THIRD-PARTY.md](THIRD-PARTY.md)。

---

## 重要合规约束（使用前必读）

1. **禁止商业使用。** 本项目及其产物不得用于任何商业目的——美术层的上游链条为非商业许可。
2. **上游素材及其派生图像不进仓库。** 由 `.gitignore` 强制拦截；仅限本地个人使用。仓库只包含我们自己的工具与文档。
3. **不得移除或篡改上游署名。** 分发时必须携带 [THIRD-PARTY.md](THIRD-PARTY.md) 中的署名声明。
4. **文档中不得内嵌上游美术截图**（那会构成再分发）。
5. **对外分发前必须先取得书面许可。** 打包、上架、发版、提交到发行版仓库之前，须获得上游权利人的明确许可，并把许可凭据记入 [THIRD-PARTY.md](THIRD-PARTY.md)。
6. 所有对外链接必须**剥离跟踪参数**（`vd_source`、`spm_id_from`、`share_session_id` 等），见 R3。

> 一句话：**代码开源，美术素材不是我们的，别拿去商用、也别打包发出去。**

---

## 目录

```
.
├── AGENTS.md                     # 协作规约（R1–R5、校验命令、许可与合规）
├── LICENSE                       # AGPL-3.0（代码）
├── LICENSE-CC-BY-NC-SA-4.0       # CC BY-NC-SA 4.0（原创非代码内容）
├── README.md
├── THIRD-PARTY.md                # 第三方素材权属、署名、授权联络与移除通道
├── docs/PROVENANCE.md            # 素材来源取证记录（脱敏）
├── pyproject.toml / uv.lock      # uv 项目定义与锁文件
├── src/bigfatfish/               # 转换器：ani.py / xcursor.py / theme.py / __main__.py
├── scripts/install-theme.sh      # 安装脚本（默认 dry-run）
├── tests/                        # stdlib unittest（含独立交叉校验器）
├── assets/                       # 上游素材（不入库，仅本地）
└── themes/                       # 生成的主题（不入库，仅本地）
```

## 上游署名

本项目的形象与素材来自第三方，来源、权利状态与署名声明见 [THIRD-PARTY.md](THIRD-PARTY.md) 与 [docs/PROVENANCE.md](docs/PROVENANCE.md)。

## 用法

```bash
# uv 可能不在 PATH（例如只装在 ~/.local/bin）
UV=$(command -v uv || echo "$HOME/.local/bin/uv")

# 素材解包到本地（assets/ 不入库）
unzip 大肥鱼.zip -d assets/

# 构建主题 -> themes/BigFatFish/（11 个光标 + 34 个软链别名）
UV_CACHE_DIR="$PWD/.uv-cache" PYTHONPATH=src "$UV" run python -m bigfatfish build

# 只看角色映射表（来自 install.inf，不臆造）
UV_CACHE_DIR="$PWD/.uv-cache" PYTHONPATH=src "$UV" run python -m bigfatfish list

# 测试
UV_CACHE_DIR="$PWD/.uv-cache" PYTHONPATH=src "$UV" run python -m unittest discover -s tests -v
```

`UV_CACHE_DIR` 指向工作区内，避免 uv 去写 `$HOME/.cache/uv`（见 [AGENTS.md](AGENTS.md) R5）。

## 安装（会改动工作区之外，先看计划）

⚠️ 安装会写入 `$HOME/.local/share/icons/`（或 `$XDG_DATA_HOME`），属 [AGENTS.md](AGENTS.md) **R5** 管辖：**默认 dry-run，须显式确认才执行**。

```bash
scripts/install-theme.sh                  # 只打印计划
scripts/install-theme.sh --yes            # 安装（同名旧主题自动备份为 .bak）
scripts/install-theme.sh --uninstall --yes
```

安装后启用（GNOME）：

```bash
gsettings set org.gnome.desktop.interface cursor-theme 'BigFatFish'
```

Wayland 会缓存光标主题，**注销并重新登录**后生效。该命令修改桌面设置（dconf），同属 R5 管辖，需确认后执行。

## 已知限制

- 只输出素材**原生**的 32 / 48 / 64 三档标称尺寸，不做插值放大（R4：不造数据）。桌面若请求 24px，由合成器就近选取或缩放。
- 不支持 PNG 压缩的 ICO 帧（遇到会明确报错）。本项目素材为 `BI_RGB` DIB。
- ruff 尚未引入；代码质量目前由 43 项测试与视觉验证保证。

## 开发环境

按 [AGENTS.md](AGENTS.md) R2 一律走 `uv`。零第三方依赖，`uv sync` 无需联网装包：

```bash
UV_CACHE_DIR="$PWD/.uv-cache" uv sync
```

> 备注：本项目是本地桌面工具，不提供网络服务。若将来引入网络服务形态，AGPL-3.0 §13 要求向使用者提供对应源代码。
