#!/usr/bin/env python3
"""laya-guard for Qwen Code — PreToolUse hook (command type).

Install: copy to .qwen/hooks/check.py (project) or ~/.qwen/hooks/check.py
(user), chmod +x, and register a PreToolUse entry in settings.json
(see settings-snippet.json).
Needs laya-guard on localhost:8787. Override: LAYA_GUARD_URL env.

Contract (per Qwen Code docs): JSON event on stdin (tool_name, tool_input,
session_id, cwd, permission_mode); on exit 0, stdout JSON controls the event:
permissionDecision allow/deny/ask. Exit 2 blocks (stderr as feedback); other
exits are non-blocking errors. review maps to ask (falls back to deny in
headless runs). Guard unreachable or unreadable input -> fail open.
"""
import json
import os
import sys
import urllib.request

GUARD_URL = os.environ.get("LAYA_GUARD_URL", "http://localhost:8787/guard")


def extract_text(event: object) -> str:
    if isinstance(event, dict):
        tool = event.get("tool_name", "")
        tool_input = event.get("tool_input", {})
        try:
            return f"{tool}({json.dumps(tool_input, ensure_ascii=False)})"
        except (TypeError, ValueError):
            return f"{tool}({tool_input})"
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
        raw = sys.stdin.read()
        event = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0  # unreadable input -> fail open
    verdict = judge(extract_text(event))
    if verdict is None:
        return 0  # guard unreachable -> fail open
    action = verdict.get("action")
    if action == "block":
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason":
                    f"laya-guard blocked [{verdict.get('policy_id')} risk={verdict.get('risk')}]: {verdict.get('reason')}",
            }
        }))
    elif action == "review":
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason":
                    f"laya-guard review [{verdict.get('policy_id')} risk={verdict.get('risk')}]: {verdict.get('reason')}",
            }
        }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
