#!/bin/bash
# Claude Code PreToolUse hook → laya-guard 심판.
# block이면 exit 2(실행 취소), 그 외는 통과. 서버: localhost:8787
input=$(cat)
tool=$(echo "$input" | python3 -c "import json,sys; d=json.load(sys.stdin); a=d.get('tool_input',{}); flat=' '.join([str(v) for v in (a.values() if isinstance(a,dict) else [a])]); print(d.get('tool_name','')+': '+flat)")
payload=$(python3 -c 'import json,sys; print(json.dumps({"tool_call": sys.stdin.read()}))' <<< "$tool")
res=$(curl -s -m 60 -X POST localhost:8787/guard -H 'Content-Type: application/json' -d "$payload") || exit 0
action=$(echo "$res" | python3 -c "import json,sys; print(json.load(sys.stdin).get('action','allow'))")
if [ "$action" = "block" ]; then
  echo "laya-guard: blocked ($res)" >&2
  exit 2
fi
exit 0
