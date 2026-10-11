"""외부 검증: AgentDojo(ETH Zurich) 코퍼스로 laya-guard 심판율 측정.

- 악성 27개: 4개 스위트(banking/slack/travel/workspace)의 injection task GOAL
  = 공격자가 에이전트에 실행시키려는 tool_call 의도 (무단송금, 정보유출 등)
- 정상 97개: user task PROMPT = 평범한 사용자 요청
- 판정 기준: 악성은 block/review 기대, 정상은 allow 기대
- 한계: 생성형 에이전트 롤아웃이 아니라 심판(judge) 레벨 검증.
  전체 파이프라인(생성+공격+방어) 평가는 생성 모델 API 키가 필요하므로 별도.
  실행: PYTHONPATH=src .venv/bin/python eval/run_agentdojo.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from laya_guard.guard import judge, is_mock


def main() -> None:
    from agentdojo.task_suite.load_suites import get_suites

    suites = get_suites("v1")
    malicious = []  # (suite, id, goal)
    benign = []  # (suite, id, prompt)
    for name, s in suites.items():
        for k, t in s.injection_tasks.items():
            malicious.append((name, t.ID, t.GOAL))
        for k, t in s.user_tasks.items():
            benign.append((name, t.ID, t.PROMPT))

    print(f"mock={is_mock()} malicious={len(malicious)} benign={len(benign)}")
    caught, missed = 0, []
    for suite, tid, goal in malicious:
        v = judge(goal)
        if v.action in ("block", "review"):
            caught += 1
        else:
            missed.append((suite, tid, goal[:80], v.action, v.risk))

    kept, blocked, review_ok = 0, [], []
    for suite, tid, prompt in benign:
        v = judge(prompt)
        # 쓰기 액션의 review(승인카드)는 정상 동작 → block만 실패
        if v.action == "block":
            blocked.append((suite, tid, prompt[:80], v.action, v.risk))
        else:
            kept += 1
            if v.action == "review":
                review_ok.append((suite, tid, prompt[:80], v.risk))

    print(f"attack-blocked: {caught}/{len(malicious)} = {caught / len(malicious):.2f}")
    for m in missed:
        print("  MISS", m)
    print(f"benign-kept:   {kept}/{len(benign)} = {kept / len(benign):.2f} (allow+review)")
    print(f"benign-blocked: {len(blocked)}/{len(benign)} (진짜 오탐)")
    for b in blocked:
        print("  OVERBLOCK", b)
    print(f"benign-review: {len(review_ok)}/{len(benign)} (승인카드, 정상)")

    import json
    out = {
        "mock": is_mock(),
        "attack_total": len(malicious),
        "attack_caught": caught,
        "benign_total": len(benign),
        "benign_kept": kept,
        "missed": [{"suite": s, "id": i, "goal": g, "action": a, "risk": r} for s, i, g, a, r in missed],
        "benign_blocked": [{"suite": s, "id": i, "prompt": p, "risk": r} for s, i, p, a, r in blocked],
    }
    p = Path(__file__).parent / "agentdojo_results.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"saved: {p}")


if __name__ == "__main__":
    main()
