#!/usr/bin/env python3
"""laya-guard for Cursor — beforeShellExecution hook (command type).

Install (user): copy to ~/.cursor/hooks/laya-guard.py, chmod +x, and point
~/.cursor/hooks.json at it (see hooks.json in this directory).
Install (project): copy to <project>/.cursor/hooks/laya-guard.py instead.
Needs laya-guard on localhost:8787. Override: LAYA_GUARD_URL env.

Contract (per Cursor docs): JSON event on stdin, JSON on stdout, exit 0
uses the JSON output, exit 2 blocks (= deny). Other exits fail open
(unless failClosed is set). review maps to ask (human approval lane).
Guard unreachable or unreadable input -> fail open (exit 0, no output).
"""
import json
import os
import sys
import urllib.request

GUARD_URL = os.environ.get("LAYA_GUARD_URL", "http://localhost:8787/guard")


def extract_command(event: object) -> str:
    # Schema-agnostic: prefer known command fields, else judge the payload text.
    if isinstance(event, dict):
        for key in ("command", "shell_command", "cmd"):
            val = event.get(key)
            if isinstance(val, str) and val:
                return val
        tool_input = event.get("tool_input")
        if isinstance(tool_input, dict):
            for key in ("command", "shell_command", "cmd"):
                val = tool_input.get(key)
                if isinstance(val, str) and val:
                    return val
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
        raw = sys.stdin.read()
        event = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0  # unreadable input -> fail open
    verdict = judge(extract_command(event))
    if verdict is None:
        return 0  # guard unreachable -> fail open
    action = verdict.get("action")
    if action == "block":
        print(json.dumps({
            "permission": "deny",
            "reason": f"laya-guard blocked [{verdict.get('policy_id')} risk={verdict.get('risk')}]: {verdict.get('reason')}",
        }))
        return 2
    if action == "review":
        print(json.dumps({
            "permission": "ask",
            "reason": f"laya-guard review [{verdict.get('policy_id')} risk={verdict.get('risk')}]: {verdict.get('reason')}",
        }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
