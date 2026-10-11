"""MOCK/실전 평가 러너: python eval/run_eval.py [--min-acc 1.0]"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from laya_guard.guard import judge, is_mock

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-acc", type=float, default=None,
                    help="fail with exit 1 if accuracy is below this (for CI)")
    args = ap.parse_args()
    p = Path(__file__).parent / "testset_ko_30.jsonl"
    rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    ok = 0
    fails = []
    for r in rows:
        v = judge(r["tool_call"])
        good = (v.action == r["expected"]) or (r["expected"] in ("review", "block") and v.action in ("review", "block"))
        ok += good
        if not good:
            fails.append((r["id"], r["tool_call"][:50], r["expected"], v.action, v.policy_id))
    acc = ok / len(rows)
    print(f"mock={is_mock()} acc={ok}/{len(rows)} = {acc:.2f}")
    for f in fails:
        print("FAIL", f)
    if args.min_acc is not None and acc < args.min_acc:
        sys.exit(1)

if __name__ == "__main__":
    main()
