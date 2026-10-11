#!/bin/bash
# Claude Code PreToolUse hook → laya-guard 심판.
# block이면 exit 2(실행 취소), 그 외는 통과. 서버: $LAYA_GUARD_URL (기본 localhost:8787)
url="${LAYA_GUARD_URL:-http://localhost:8787/guard}"
input=$(cat)
# Bash는 실제 실행될 command만 심판 (description은 실행되지 않음). 그 외 도구는 이름+입력값 평탄화.
tool=$(echo "$input" | python3 -c "import json,sys; d=json.load(sys.stdin); a=d.get('tool_input',{}); c=a.get('command') if isinstance(a,dict) else None; flat=' '.join([str(v) for v in (a.values() if isinstance(a,dict) else [a])]); print(c if isinstance(c,str) and c else d.get('tool_name','')+': '+flat)")
payload=$(python3 -c 'import json,sys; print(json.dumps({"tool_call": sys.stdin.read().strip()}))' <<< "$tool")
res=$(curl -s -m 60 -X POST "$url" -H 'Content-Type: application/json' -d "$payload") || exit 0
action=$(echo "$res" | python3 -c "import json,sys; print(json.load(sys.stdin).get('action','allow'))")
if [ "$action" = "block" ]; then
  echo "laya-guard: blocked ($res)" >&2
  exit 2
fi
exit 0
