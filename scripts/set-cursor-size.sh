#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 BigFatFish contributors
#
# 让光标"又大又不虚"。
#
# 原理：合成器按 `需求像素 = round(逻辑尺寸 × 显示器缩放)` 取图。若该需求不落在
# 主题的原生像素档上，它只能拉伸现有档，于是发虚。所以清晰档位满足
# `逻辑尺寸 ≈ 原生档 ÷ 缩放`；在此前提下再取尽可能大的档。
# 推导与实测方法见 themes/README.md。
#
# ⚠️ 本脚本会写入**工作区之外**（AGENTS.md R5 管辖）：
#     1) gsettings  org.gnome.desktop.interface cursor-size
#     2) $XDG_CONFIG_HOME/environment.d/95-cursor-theme.conf 中的 XCURSOR_SIZE
#    默认只打印计划；必须显式加 --yes 才写入。应用后会打印回滚命令。
#
# 仅针对 GNOME；其它桌面环境请用系统设置里对应的光标尺寸项。

set -euo pipefail

NATIVE_SIZES="32,48,64"
STRETCH_LIMIT="1.20"
ENV_FILE="${XDG_CONFIG_HOME:-$HOME/.config}/environment.d/95-cursor-theme.conf"

SCALE=""
ACTION="list"
TARGET=""
CONFIRM=0

die() { printf '错误：%s\n' "$*" >&2; exit 1; }
note() { printf '%s\n' "$*"; }

usage() {
  cat <<'EOF'
用法: scripts/set-cursor-size.sh [选项]

选项:
  --list               列出本机推荐档位（默认动作，只读）
  --auto               自动挑选「清晰前提下最大」的档位
  --set N              直接指定逻辑尺寸 N
  --reset              把 cursor-size 恢复为系统 schema 默认值
  --native 32,48,64    主题原生像素档（默认 32,48,64，与本主题一致）
  --stretch L          --auto 允许的最大拉伸倍数（默认 1.20）
  --scale S            手动指定显示器缩放因子（默认自动探测）
  --env-file PATH      覆盖 environment.d 配置文件路径
  --yes                真正写入（不加则只打印计划）
  -h, --help           显示本帮助

含义:
  需求像素 = round(逻辑尺寸 × 缩放)；它落在原生档上才清晰。
  判定列的「拉伸」= 需求像素 ÷ 实际取到的原生档，越接近 1.00 越清晰。
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --list)    ACTION="list"; shift ;;
    --auto)    ACTION="auto"; shift ;;
    --set)     ACTION="set"; TARGET="${2:?--set 需要一个正整数}"; shift 2 ;;
    --reset)   ACTION="reset"; shift ;;
    --native)  NATIVE_SIZES="${2:?--native 需要形如 32,48,64}"; shift 2 ;;
    --stretch) STRETCH_LIMIT="${2:?--stretch 需要一个数字}"; shift 2 ;;
    --scale)   SCALE="${2:?--scale 需要一个数字}"; shift 2 ;;
    --env-file) ENV_FILE="${2:?--env-file 需要路径}"; shift 2 ;;
    --yes|-y)  CONFIRM=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "未知参数：$1（用 --help 查看用法）" ;;
  esac
done

command -v gsettings >/dev/null 2>&1 || die "找不到 gsettings（本脚本仅支持 GNOME/GTK 桌面）"

# 只接受形如 12 或 1.25 的正数：挡掉 --scale 0（会让 awk 除零，或让 --auto
# 算出荒唐档位并真的写进系统）以及 1.2.3（awk 只取数值前缀）这类静默错误。
is_positive_number() {
  printf '%s' "$1" | grep -Eq '^[0-9]+(\.[0-9]+)?$' &&
    awk -v v="$1" 'BEGIN { exit (v + 0 > 0) ? 0 : 1 }'
}

validate_native() {
  local item
  local IFS=','
  for item in $NATIVE_SIZES; do
    case "$item" in ''|*[!0-9]*) die "--native 只接受逗号分隔的正整数，收到：$NATIVE_SIZES" ;; esac
    [ "$item" -gt 0 ] || die "--native 不能为 0：$NATIVE_SIZES"
    [ "$item" -le 4096 ] || die "--native 单项不得超过 4096：$NATIVE_SIZES"
  done
}

is_positive_number "$STRETCH_LIMIT" || die "--stretch 需要一个正数（如 1.20），收到：$STRETCH_LIMIT"
validate_native

# ---------- 探测显示器缩放 ----------
detect_scale() {
  local file list
  file="${XDG_CONFIG_HOME:-$HOME/.config}/monitors.xml"
  if [ -f "$file" ]; then
    list=$(grep -o '<scale>[^<]*' "$file" 2>/dev/null | sed 's/<scale>//' | sort -g -u || true)
    if [ -n "$list" ]; then
      # 多显示器缩放不一致时取最大值，并提示
      if [ "$(printf '%s\n' "$list" | wc -l)" -gt 1 ]; then
        note "注意：检测到多个缩放值（$(printf '%s' "$list" | tr '\n' ' ')），按最大值计算。"
      fi
      printf '%s' "$(printf '%s\n' "$list" | tail -1)"
      return
    fi
  fi
  printf '1'
}

[ -n "$SCALE" ] || SCALE="$(detect_scale)"
# 注意：必须在探测之后校验——否则未显式传 --scale 时会把空值当成错误
is_positive_number "$SCALE" || die "--scale 需要一个正数（如 1.25），收到：$SCALE"

# ---------- 档位表 ----------
ladder() {
  awk -v s="$SCALE" -v native="$NATIVE_SIZES" '
  function abs(x) { return x < 0 ? -x : x }
  function pick(need,   b, j) {
    b = nat[1]
    for (j = 2; j <= n; j++) if (abs(need - nat[j]) < abs(need - b)) b = nat[j]
    return b
  }
  function verdict(ratio) {
    if (ratio > 0.98 && ratio < 1.02) return "原生 1:1 —— 最清晰"
    if (ratio <= 1.10) return "几乎无损"
    if (ratio <= 1.20) return "轻微发虚（肉眼难辨）"
    if (ratio <= 1.35) return "看得出变软"
    return "明显发虚"
  }
  BEGIN {
    n = split(native, raw, ",")
    for (i = 1; i <= n; i++) {
      nat[i] = raw[i] + 0
      if (nat[i] <= 0) { print "错误：--native 只接受正整数" > "/dev/stderr"; exit 2 }
    }
    for (i = 1; i <= n; i++) {
      logical = int(nat[i] / s + 0.5)
      if (logical < 1) logical = 1
      need = int(logical * s + 0.5)
      b = pick(need)
      ratio = need / b
      printf "  逻辑 %-4d → 需求 %-5d → 取到 %-5d → 拉伸 %.2f×  %s\n", logical, need, b, ratio, verdict(ratio)
    }
  }'
}

# --auto：在拉伸不超过 STRETCH_LIMIT 的档位里取最大
pick_auto() {
  awk -v s="$SCALE" -v native="$NATIVE_SIZES" -v limit="$STRETCH_LIMIT" '
  function abs(x) { return x < 0 ? -x : x }
  function pick(need,   b, j) {
    b = nat[1]
    for (j = 2; j <= n; j++) if (abs(need - nat[j]) < abs(need - b)) b = nat[j]
    return b
  }
  BEGIN {
    n = split(native, raw, ",")
    maxnat = 0
    for (i = 1; i <= n; i++) { nat[i] = raw[i] + 0; if (nat[i] > maxnat) maxnat = nat[i] }
    # 扫描逻辑尺寸本身（而不是只从原生档反推），才能在允许的拉伸内取到更大值
    best = 0; need_b = 0; got_b = 0; ratio_b = 0
    for (L = 1; L <= maxnat * 4; L++) {
      need = int(L * s + 0.5)
      b = pick(need)
      ratio = need / b
      if (ratio <= limit && L > best) { best = L; need_b = need; got_b = b; ratio_b = ratio }
    }
    if (best > 0) printf "%d %d %d %.2f", best, need_b, got_b, ratio_b
  }'
}

write_env_file() {
  # 原子替换：不跟随软链、不留半截文件；只管理 XCURSOR_SIZE 行
  local value="$1" theme="$2" tmp
  tmp="${ENV_FILE}.tmp.$$"
  if [ -f "$ENV_FILE" ]; then
    grep -v '^XCURSOR_SIZE=' -- "$ENV_FILE" > "$tmp" || true
  else
    printf 'XCURSOR_THEME=%s\n' "$theme" > "$tmp"
  fi
  printf 'XCURSOR_SIZE=%s\n' "$value" >> "$tmp"
  mv -f -- "$tmp" "$ENV_FILE"
}

apply_size() {
  local value="$1" theme
  theme="$(gsettings get org.gnome.desktop.interface cursor-theme | tr -d "'")"
  # 主题名会被写进 environment.d 配置：只允许安全字符，避免换行注入额外 KEY=VALUE
  case "$theme" in
    ''|*[!A-Za-z0-9._-]*) die "光标主题名异常，拒绝写入配置文件：$theme" ;;
  esac

  if [ "$CONFIRM" -ne 1 ]; then
    note "这是预览。确认无误后加 --yes 执行。"
    return 0
  fi

  gsettings set org.gnome.desktop.interface cursor-size "$value"

  mkdir -p "$(dirname -- "$ENV_FILE")"
  write_env_file "$value" "$theme"

  note "已应用："
  note "  gsettings cursor-size = $(gsettings get org.gnome.desktop.interface cursor-size)"
  note "  $ENV_FILE 中的 XCURSOR_SIZE = ${value}"
  note "  （environment.d 需重新登录才生效；GNOME 自身界面通常立即生效）"
  note "回滚：gsettings reset org.gnome.desktop.interface cursor-size"
}

case "$ACTION" in
  list)
    note "显示器缩放 s = ${SCALE}    当前 cursor-size = $(gsettings get org.gnome.desktop.interface cursor-size)"
    note "当前 cursor-theme  = $(gsettings get org.gnome.desktop.interface cursor-theme)"
    note "主题原生档        = ${NATIVE_SIZES}"
    note ""
    note "原生 1:1（最清晰）的档位："
    ladder
    note ""
    auto="$(pick_auto)"
    if [ -n "$auto" ]; then
      read -r a_size a_need a_got a_ratio <<<"$auto"
      note "在拉伸 ≤ ${STRETCH_LIMIT} 前提下可用的最大档：逻辑 ${a_size}"
      note "  （需求 ${a_need}px，取到 ${a_got}px，拉伸 ${a_ratio}×）"
    fi
    note ""
    note "用法：scripts/set-cursor-size.sh --set <逻辑尺寸> --yes"
    note "      scripts/set-cursor-size.sh --auto --yes   （清晰前提下尽量大）"
    ;;
  auto)
    auto="$(pick_auto)"
    [ -n "$auto" ] || die "在拉伸 ≤ ${STRETCH_LIMIT} 的约束下没有可用档位（缩放 s=${SCALE}？）"
    read -r value need got ratio <<<"$auto"
    note "自动选定：逻辑 ${value} → 需求 ${need}px → 取到 ${got}px → 拉伸 ${ratio}×"
    note "（拉伸上限 ${STRETCH_LIMIT}，缩放 s=${SCALE}）"
    note ""
    apply_size "$value"
    ;;
  set)
    case "$TARGET" in
      ''|*[!0-9]*) die "--set 需要一个正整数，收到：$TARGET" ;;
    esac
    [ "$TARGET" -gt 0 ] || die "--set 需要大于 0"
    [ "$TARGET" -le 512 ] || die "--set 超出合理范围（应 ≤ 512，收到 $TARGET）"
    note "指定逻辑尺寸 = ${TARGET}（缩放 s=${SCALE}）"
    note ""
    note "原生 1:1（最清晰）的档位："
    ladder
    note ""
    ratio="$(awk -v s="$SCALE" -v t="$TARGET" -v native="$NATIVE_SIZES" '
      function abs(x){return x<0?-x:x}
      BEGIN{ n=split(native,a,","); need=int(t*s+0.5); b=a[1]+0
             for(i=2;i<=n;i++) if(abs(need-(a[i]+0))<abs(need-b)) b=a[i]+0
             printf "%.2f", need/b }')"
    note "该值对应拉伸 ${ratio}×（越接近 1.00 越清晰）"
    awk -v r="$ratio" 'BEGIN{ if (r+0 > 1.25) exit 1 }' || note "提示：拉伸偏大，可能看起来发虚。"
    note ""
    apply_size "$TARGET"
    ;;
  reset)
    if [ "$CONFIRM" -ne 1 ]; then
      note "这是预览：将执行 gsettings reset org.gnome.desktop.interface cursor-size"
      note "并从 $ENV_FILE 移除 XCURSOR_SIZE 行。确认无误后加 --yes。"
      exit 0
    fi
    gsettings reset org.gnome.desktop.interface cursor-size
    if [ -f "$ENV_FILE" ] && grep -q '^XCURSOR_SIZE=' "$ENV_FILE"; then
      tmp="${ENV_FILE}.tmp.$$"
      grep -v '^XCURSOR_SIZE=' -- "$ENV_FILE" > "$tmp" || true
      mv -f -- "$tmp" "$ENV_FILE"
    fi
    note "已恢复默认：cursor-size = $(gsettings get org.gnome.desktop.interface cursor-size)"
    ;;
esac
