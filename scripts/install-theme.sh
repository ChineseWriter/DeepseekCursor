#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 BigFatFish contributors
#
# 把构建好的主题安装到本机（per-user，不使用 sudo）。
#
# ⚠️ 本脚本会写入**工作区之外**的路径（默认 $HOME/.local/share/icons/）。
#    按 AGENTS.md R5：动手前先看清楚它要改什么，并已获得用户同意。
#    默认只打印计划，必须显式加 --yes 才会真正落盘。
#
# 用法：
#   scripts/install-theme.sh                      # 只打印计划
#   scripts/install-theme.sh --yes                # 安装
#   scripts/install-theme.sh --uninstall --yes    # 卸载
#   scripts/install-theme.sh --target DIR --yes   # 指定安装位置

set -euo pipefail

THEME_NAME="BigFatFish"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
SOURCE_DIR="$REPO_ROOT/themes/$THEME_NAME"
TARGET_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/icons/$THEME_NAME"

ACTION="install"
CONFIRM=0

while [ $# -gt 0 ]; do
  case "$1" in
    --uninstall) ACTION="uninstall"; shift ;;
    --target) TARGET_DIR="${2:?--target 需要一个路径}"; shift 2 ;;
    --yes|-y) CONFIRM=1; shift ;;
    -h|--help) sed -n '2,16p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "未知参数：$1" >&2; exit 2 ;;
  esac
done

echo "动作      : $ACTION"
echo "主题      : $THEME_NAME"
echo "源目录    : $SOURCE_DIR"
echo "目标目录  : $TARGET_DIR   （工作区之外，见 AGENTS.md R5）"

if [ "$CONFIRM" -ne 1 ]; then
  echo
  echo "这是预览。确认无误后加 --yes 执行。"
  exit 0
fi

case "$ACTION" in
  install)
    [ -d "$SOURCE_DIR" ] || { echo "错误：$SOURCE_DIR 不存在，请先运行构建（见 README）" >&2; exit 1; }
    mkdir -p "$(dirname -- "$TARGET_DIR")"
    if [ -d "$TARGET_DIR" ]; then
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
    echo "启用（按桌面环境选一条，需要你确认后再执行）："
    echo "  GNOME : gsettings set org.gnome.desktop.interface cursor-theme '$THEME_NAME'"
    echo "  KDE   : 系统设置 -> 外观 -> 光标 -> 选择 $THEME_NAME"
    echo "  立即生效：注销并重新登录（Wayland 会缓存光标主题）"
    ;;
  uninstall)
    if [ -d "$TARGET_DIR" ]; then
      if command -v trash >/dev/null 2>&1; then
        trash -- "$TARGET_DIR" && echo "已移入回收站：$TARGET_DIR"
      else
        echo "未找到 trash 命令；请手动删除：$TARGET_DIR" >&2
        exit 1
      fi
    else
      echo "目标目录不存在，无需卸载：$TARGET_DIR"
    fi
    [ -d "${TARGET_DIR}.bak" ] && echo "注意：备份仍在 ${TARGET_DIR}.bak"
    echo "如需恢复默认光标主题：gsettings reset org.gnome.desktop.interface cursor-theme"
    ;;
esac
