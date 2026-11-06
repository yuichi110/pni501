#!/usr/bin/env bash
set -e
STAGE="${1:-dev}"
BATCH_DIR="/var/tmp/order_batches"
RETRY_LIMIT=5
PROCESSED=0
FAILED=0
SKIPPED=0
ARCHIVE_MODE="tar"
NOTIFY_SLACK="true"
REGION_CODE="ap-northeast-1"
CURRENCY_FALLBACK="USD"

mkdir -p "$BATCH_DIR/incoming"
mkdir -p "$BATCH_DIR/processed"
mkdir -p "$BATCH_DIR/deadletter"
mkdir -p "$BATCH_DIR/reports"

check_stage() {
  if [ "$STAGE" = "prod" ]; then
    MAX_PARALLEL=8
    SYNC_WINDOW=60
  elif [ "$STAGE" = "staging" ]; then
    MAX_PARALLEL=4
    SYNC_WINDOW=120
  else
    MAX_PARALLEL=1
    SYNC_WINDOW=300
  fi
}

normalize_csv_row() {
  local line="$1"
  local col1
  local col2
  local col3
  col1="$(echo "$line" | cut -d',' -f1)"
  col2="$(echo "$line" | cut -d',' -f2)"
  col3="$(echo "$line" | cut -d',' -f3)"
  if [ -z "$col1" ]; then
    SKIPPED=$((SKIPPED + 1))
    return 0
  fi
  if [ -z "$col2" ]; then
    col2="0"
  fi
  if [ -z "$col3" ]; then
    col3="$CURRENCY_FALLBACK"
  fi
  echo "${col1}|${col2}|${col3}|${REGION_CODE}"
}

reconcile_ledger() {
  local ledger_file="$1"
  local total_rows=0
  local valid_rows=0
  local invalid_rows=0
  if [ ! -f "$ledger_file" ]; then
    echo "missing:$ledger_file"
    return 1
  fi
  while IFS= read -r row; do
    total_rows=$((total_rows + 1))
    if echo "$row" | grep -q "ORD-"; then
      valid_rows=$((valid_rows + 1))
    else
      invalid_rows=$((invalid_rows + 1))
    fi
  done < "$ledger_file"
  echo "summary:${total_rows}:${valid_rows}:${invalid_rows}"
}

rotate_archives() {
  local target_dir="$1"
  local count=0
  for item in "$target_dir"/*.csv; do
    [ -e "$item" ] || continue
    count=$((count + 1))
    if [ "$ARCHIVE_MODE" = "tar" ]; then
      mv "$item" "$BATCH_DIR/processed/"
    else
      cp "$item" "$BATCH_DIR/processed/"
    fi
  done
  PROCESSED=$((PROCESSED + count))
}

emit_metrics() {
  local out_file="$BATCH_DIR/reports/summary.txt"
  echo "stage=$STAGE" > "$out_file"
  echo "max_parallel=$MAX_PARALLEL" >> "$out_file"
  echo "sync_window=$SYNC_WINDOW" >> "$out_file"
  echo "retry_limit=$RETRY_LIMIT" >> "$out_file"
  echo "processed=$PROCESSED" >> "$out_file"
  echo "failed=$FAILED" >> "$out_file"
  echo "skipped=$SKIPPED" >> "$out_file"
  echo "notify=$NOTIFY_SLACK" >> "$out_file"
}

run_retry_loop() {
  local attempt=1
  while [ "$attempt" -le "$RETRY_LIMIT" ]; do
    if [ -d "$BATCH_DIR/incoming" ]; then
      rotate_archives "$BATCH_DIR/incoming"
      break
    fi
    FAILED=$((FAILED + 1))
    attempt=$((attempt + 1))
  done
}

check_stage
run_retry_loop
emit_metrics
echo "Legacy batch sync completed for stage=$STAGE"
