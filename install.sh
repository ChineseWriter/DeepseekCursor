#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 BigFatFish contributors
#
# 安装 / 卸载本仓库的某个光标主题（用户级，不使用 sudo）。
#
# ⚠️ 本脚本会写入**仓库之外**的路径（默认 $XDG_DATA_HOME/icons）。
#    按 AGENTS.md R5：默认只打印计划，必须显式加 --yes 才会真正落盘。
#
# 安全护栏：覆盖或删除既有目录之前，先确认它确实是本主题
# （存在 index.theme 且 Name=<主题名>）。这样 `--target` 一旦写错，
# 也不会把无关目录整体 mv 成 .bak 或丢进回收站；确需覆盖请显式加 --force。

set -euo pipefail

DEFAULT_THEME="BigFatFish"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
THEMES_DIR="$SCRIPT_DIR/themes"

THEME_NAME="$DEFAULT_THEME"
ACTION="install"
CONFIRM=0
FORCE=0
TARGET_DIR=""

usage() {
  cat <<EOF
用法: ./install.sh [选项]

选项:
  --theme NAME    要安装 / 卸载的主题（默认 $DEFAULT_THEME；--list 可看全部）
  --list          列出仓库内全部主题后退出
  --yes, -y       真正写入（不加则只打印计划）
  --uninstall     卸载，移入回收站（默认是安装）
  --target DIR    指定安装位置（默认 \${XDG_DATA_HOME:-\$HOME/.local/share}/icons/NAME）
  --force         目标目录不是本主题时，仍允许覆盖 / 删除
  -h, --help      显示本帮助

装完后启用（请自行确认后执行）：
  gsettings set org.gnome.desktop.interface cursor-theme '<主题名>'
  # 之后注销并重新登录：Wayland 会缓存光标主题
EOF
}

list_themes() {
  [ -d "$THEMES_DIR" ] || { echo "未找到 $THEMES_DIR" >&2; return 1; }
  for dir in "$THEMES_DIR"/*/; do
    [ -f "$dir/index.theme" ] || continue
    name="$(basename -- "$dir")"
    comment="$(sed -n 's/^Comment=//p' "$dir/index.theme" | head -1)"
    printf '%-16s %s\n' "$name" "$comment"
  done
}

is_our_theme() {
  [ -f "$1/index.theme" ] && grep -q "^Name=${THEME_NAME}\$" "$1/index.theme" 2>/dev/null
}

while [ $# -gt 0 ]; do
  case "$1" in
    --theme) THEME_NAME="${2:?--theme 需要一个名称}"; shift 2 ;;
    --list) list_themes; exit 0 ;;
    --uninstall) ACTION="uninstall"; shift ;;
    --target) TARGET_DIR="${2:?--target 需要一个路径}"; shift 2 ;;
    --yes|-y) CONFIRM=1; shift ;;
    --force) FORCE=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "未知参数：$1（用 --help 查看用法）" >&2; exit 2 ;;
  esac
done

case "$THEME_NAME" in
  ""|*/*|.|..) echo "错误：主题名非法：$THEME_NAME" >&2; exit 2 ;;
esac

SOURCE_DIR="$THEMES_DIR/$THEME_NAME"
: "${TARGET_DIR:=${XDG_DATA_HOME:-$HOME/.local/share}/icons/$THEME_NAME}"

echo "动作      : $ACTION"
echo "主题      : $THEME_NAME"
echo "源目录    : $SOURCE_DIR"
echo "目标目录  : $TARGET_DIR   （仓库之外，见 AGENTS.md R5）"

if [ "$CONFIRM" -ne 1 ]; then
  echo
  echo "这是预览。确认无误后加 --yes 执行。"
  exit 0
fi

case "$ACTION" in
  install)
    [ -d "$SOURCE_DIR" ] || {
      echo "错误：$SOURCE_DIR 不存在。用 --list 查看可用主题。" >&2
      exit 1
    }
    mkdir -p "$(dirname -- "$TARGET_DIR")"
    if [ -e "$TARGET_DIR" ] && [ ! -d "$TARGET_DIR" ]; then
      echo "错误：$TARGET_DIR 已存在但不是目录，拒绝覆盖" >&2
      exit 1
    fi
    if [ -d "$TARGET_DIR" ]; then
      if ! is_our_theme "$TARGET_DIR" && [ "$FORCE" -ne 1 ]; then
        echo "错误：$TARGET_DIR 存在，但不是本主题（缺 index.theme 或 Name 不符）。" >&2
        echo "      为避免误覆盖无关目录已中止；确认无误请加 --force。" >&2
        exit 1
      fi
      echo "已存在同名主题，覆盖前先备份到 ${TARGET_DIR}.bak"
      if [ -e "${TARGET_DIR}.bak" ]; then
        echo "错误：${TARGET_DIR}.bak 已存在，请先自行处理，避免覆盖你的备份" >&2
        exit 1
      fi
      mv -- "$TARGET_DIR" "${TARGET_DIR}.bak"
    fi
    cp -a -- "$SOURCE_DIR" "$TARGET_DIR"
    echo "已安装：$TARGET_DIR"
    echo
    echo "下一步（需你自己确认后执行）："
    echo "  gsettings set org.gnome.desktop.interface cursor-theme '$THEME_NAME'"
    echo "  然后注销并重新登录（Wayland 会缓存光标主题）"
    echo "提示：若觉得光标偏小或发虚，见 README「光标大小与清晰度」一节。"
    ;;
  uninstall)
    if [ -d "$TARGET_DIR" ]; then
      if ! is_our_theme "$TARGET_DIR" && [ "$FORCE" -ne 1 ]; then
        echo "错误：$TARGET_DIR 存在，但不是本主题，拒绝删除。" >&2
        echo "      确认要删除请加 --force。" >&2
        exit 1
      fi
      if command -v trash >/dev/null 2>&1; then
        trash -- "$TARGET_DIR" && echo "已移入回收站：$TARGET_DIR"
      else
        echo "未找到 trash 命令；请手动删除：$TARGET_DIR" >&2
        exit 1
      fi
    else
      echo "目标目录不存在，无需卸载：$TARGET_DIR"
    fi
    if [ -d "${TARGET_DIR}.bak" ]; then
      echo "注意：备份仍在 ${TARGET_DIR}.bak"
    fi
    echo "如需恢复默认光标主题：gsettings reset org.gnome.desktop.interface cursor-theme"
    ;;
esac
