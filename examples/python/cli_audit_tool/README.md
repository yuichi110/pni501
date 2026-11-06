# logpulse

`logpulse` inspects structured `.jsonl` application logs, groups recurring error signatures, and emits human-readable Rich tables or machine-parseable `--format json` summaries.

## Quickstart

```bash
uv run logpulse scan ./service.jsonl --min-level ERROR --format json
```

## CLI Flags & Exit Codes

- `--format [table|json]`: Emit machine-readable JSON to `stdout` while keeping diagnostic errors on `stderr`.
- `--no-color`: Disable ANSI styling for CI pipelines.
- Exit codes: `0` (healthy), `1` (threshold exceeded), `2` (unreadable input file).
