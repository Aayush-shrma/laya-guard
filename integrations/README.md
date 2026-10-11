# Agent integrations

All adapters gate tool execution through your local laya-guard server
(`laya-guard serve`, default `http://localhost:8787/guard`).
Set `LAYA_GUARD_URL` to override. Every adapter **fails open** when the
server is unreachable — see the main README's Limitations.

| Agent | Mechanism | Files | review maps to |
|---|---|---|---|
| Claude Code | PreToolUse hook (stdin JSON, exit 2 blocks) | [`../guard-hook.sh`](../guard-hook.sh) | passes through (exit 0) |
| OpenCode | `tool.execute.before` plugin (throw blocks) | [`opencode/laya-guard.ts`](opencode/laya-guard.ts) | allow + stderr warning |
| Codex CLI | `PreToolUse` command hook (deny JSON) | [`codex/`](codex/) | allow + stderr note (PreToolUse has no ask lane) |
| Cursor | `beforeShellExecution` hook (exit 2 / deny JSON) | [`cursor/`](cursor/) | `ask` (human approval lane) |
| Kilo Code | `tool.execute.before` plugin (throw blocks) | [`kilo/laya-guard.ts`](kilo/laya-guard.ts) | allow + stderr warning |

## Claude Code

`guard-hook.sh` is a PreToolUse hook: register it in your settings, it POSTs
each tool call and exits 2 on `block`.

## OpenCode

Copy `opencode/laya-guard.ts` to `.opencode/plugins/laya-guard.ts` (project)
or `~/.config/opencode/plugins/laya-guard.ts` (global). Docs:
https://opencode.ai/docs/plugins/ — the `tool.execute.before` hook throws to
block. For hard asks, add `permission` rules in `opencode.json`:
https://opencode.ai/docs/permissions/

## Codex CLI

1. `cp codex/check_command.py ~/.codex/hooks/ && chmod +x ~/.codex/hooks/check_command.py`
2. Append `codex/config-snippet.toml` to `~/.codex/config.toml`
   (requires `[features] hooks = true`).
3. Docs: https://developers.openai.com/codex/hooks — note hooks are a
   guardrail, not a complete enforcement boundary.

## Cursor

1. `cp cursor/laya-guard.py ~/.cursor/hooks/ && chmod +x ~/.cursor/hooks/laya-guard.py`
2. Merge `cursor/hooks.json` into `~/.cursor/hooks.json` (user) or
   `<project>/.cursor/hooks.json` (project; change the command path to
   `.cursor/hooks/laya-guard.py`). Docs: https://cursor.com/docs/hooks

## Kilo Code

Copy `kilo/laya-guard.ts` to `.kilo/plugin/laya-guard.ts` (project) or
`~/.config/kilo/plugin/laya-guard.ts` (global). For hard asks, add
`permission` rules in `kilo.jsonc`. Docs:
https://kilo.ai/docs/automate/extending/plugins
