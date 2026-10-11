#!/usr/bin/env python3
"""laya-guard for Codex CLI — PreToolUse hook (command type).

Install: copy to ~/.codex/hooks/check_command.py, chmod +x, and add the
[[hooks.PreToolUse]] block from config-snippet.toml to ~/.codex/config.toml
(requires [features] hooks = true). Needs laya-guard on localhost:8787.
Override: LAYA_GUARD_URL env (default http://localhost:8787/guard).

Contract (per Codex docs): JSON event on stdin; denial as JSON on stdout
with hookSpecificOutput.permissionDecision = deny; silence + exit 0 lets
the call through. PreToolUse has no ask lane, so review passes with a
stderr note. Guard unreachable -> fail open (silence, exit 0).
"""
import json
import os
import sys
import urllib.request

GUARD_URL = os.environ.get("LAYA_GUARD_URL", "http://localhost:8787/guard")


def extract_command(event: object) -> str:
    if isinstance(event, dict):
        tool_input = event.get("tool_input")
        if isinstance(tool_input, dict):
            cmd = tool_input.get("command")
            if isinstance(cmd, str) and cmd:
                return cmd
        # schema-agnostic fallback: judge the whole payload text
        try:
            return json.dumps(event, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(event)
    return str(event)


def judge(text: str) -> dict | None:
    try:
        req = urllib.request.Request(
            GUARD_URL,
            data=json.dumps({"tool_call": text, "source": "tool"}).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except Exception:
        return None


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except Exception:
        return 0  # unreadable input -> fail open
    verdict = judge(extract_command(event))
    if verdict is None:
        return 0  # guard unreachable -> fail open
    if verdict.get("action") == "block":
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason":
                    f"laya-guard blocked [{verdict.get('policy_id')} risk={verdict.get('risk')}]: {verdict.get('reason')}",
            }
        }))
    elif verdict.get("action") == "review":
        print(f"laya-guard review [{verdict.get('policy_id')} risk={verdict.get('risk')}]: "
              f"{verdict.get('reason')}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
