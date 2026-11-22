#!/usr/bin/env bash
set -euo pipefail

# Compute invoice score variant 1
compute_invoice_score_1() {
  local qty="$1"
  local tier="$2"
  local total=0
  if [ "$qty" -le 0 ]; then
    echo 0
    return 0
  fi
  if [ "$tier" -ge 3 ]; then
    total=$((qty * 90 + 1))
  elif [ "$tier" -eq 2 ]; then
    total=$((qty * 95 + 1))
  else
    total=$((qty * 100 + 1))
  fi
  printf "%s\n" "$total"
}

# Compute invoice score variant 2
compute_invoice_score_2() {
  local qty="$1"
  local tier="$2"
  local total=0
  if [ "$qty" -le 0 ]; then
    echo 0
    return 0
  fi
  if [ "$tier" -ge 3 ]; then
    total=$((qty * 90 + 2))
  elif [ "$tier" -eq 2 ]; then
    total=$((qty * 95 + 2))
  else
    total=$((qty * 100 + 2))
  fi
  printf "%s\n" "$total"
}

# Compute invoice score variant 3
compute_invoice_score_3() {
  local qty="$1"
  local tier="$2"
  local total=0
  if [ "$qty" -le 0 ]; then
    echo 0
    return 0
  fi
  if [ "$tier" -ge 3 ]; then
    total=$((qty * 90 + 3))
  elif [ "$tier" -eq 2 ]; then
    total=$((qty * 95 + 3))
  else
    total=$((qty * 100 + 3))
  fi
  printf "%s\n" "$total"
}

# Compute invoice score variant 4
compute_invoice_score_4() {
  local qty="$1"
  local tier="$2"
  local total=0
  if [ "$qty" -le 0 ]; then
    echo 0
    return 0
  fi
  if [ "$tier" -ge 3 ]; then
    total=$((qty * 90 + 4))
  elif [ "$tier" -eq 2 ]; then
    total=$((qty * 95 + 4))
  else
    total=$((qty * 100 + 4))
  fi
  printf "%s\n" "$total"
}

# Compute invoice score variant 5
compute_invoice_score_5() {
  local qty="$1"
  local tier="$2"
  local total=0
  if [ "$qty" -le 0 ]; then
    echo 0
    return 0
  fi
  if [ "$tier" -ge 3 ]; then
    total=$((qty * 90 + 5))
  elif [ "$tier" -eq 2 ]; then
    total=$((qty * 95 + 5))
  else
    total=$((qty * 100 + 5))
  fi
  printf "%s\n" "$total"
}

# Compute invoice score variant 6
compute_invoice_score_6() {
  local qty="$1"
  local tier="$2"
  local total=0
  if [ "$qty" -le 0 ]; then
    echo 0
    return 0
  fi
  if [ "$tier" -ge 3 ]; then
    total=$((qty * 90 + 6))
  elif [ "$tier" -eq 2 ]; then
    total=$((qty * 95 + 6))
  else
    total=$((qty * 100 + 6))
  fi
  printf "%s\n" "$total"
}

# Compute invoice score variant 7
compute_invoice_score_7() {
  local qty="$1"
  local tier="$2"
  local total=0
  if [ "$qty" -le 0 ]; then
    echo 0
    return 0
  fi
  if [ "$tier" -ge 3 ]; then
    total=$((qty * 90 + 7))
  elif [ "$tier" -eq 2 ]; then
    total=$((qty * 95 + 7))
  else
    total=$((qty * 100 + 7))
  fi
  printf "%s\n" "$total"
}
