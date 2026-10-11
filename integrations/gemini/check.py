#!/usr/bin/env python3
"""laya-guard for Gemini CLI — BeforeTool hook (command type).

Install: copy to .gemini/hooks/check.py (project) or ~/.gemini/hooks/check.py
(user), chmod +x, and register a BeforeTool entry in settings.json, e.g.
matcher "run_shell_command" (see settings-snippet.json).
Needs laya-guard on localhost:8787. Override: LAYA_GUARD_URL env.

Contract (per Gemini CLI docs): JSON event on stdin (tool_name, tool_input);
deny via stdout {"decision": "deny", "reason": ...}, or exit 2 to block with
stderr as the reason. Other exits warn, exit 0 parses stdout as JSON. No ask
lane on BeforeTool, so review passes with a stderr note. Guard unreachable
or unreadable input -> fail open (exit 0, no output).
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
    if verdict.get("action") == "block":
        print(json.dumps({
            "decision": "deny",
            "reason": f"laya-guard blocked [{verdict.get('policy_id')} risk={verdict.get('risk')}]: {verdict.get('reason')}",
        }))
    elif verdict.get("action") == "review":
        print(f"laya-guard review [{verdict.get('policy_id')} risk={verdict.get('risk')}]: "
              f"{verdict.get('reason')}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
