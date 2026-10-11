"""CLI: laya-guard check / serve / eval."""
from __future__ import annotations
import argparse, json, sys
from .guard import judge, is_mock

def cmd_check(args):
    text = " ".join(args.text) if args.text else sys.stdin.read()
    v = judge(text)
    icon = {"allow": "OK", "review": "REVIEW", "block": "BLOCK"}[v.action]
    print(f"[{icon}] {v.action} risk={v.risk} policy={v.policy_id} mock={v.mock}")
    print(f"reason: {v.reason}")
    return 0 if v.action != "block" else 2

def cmd_serve(args):
    from .server import run
    print(f"laya-guard on http://{args.host}:{args.port} mock={is_mock()}")
    run(args.host, args.port)

def main(argv=None):
    ap = argparse.ArgumentParser(prog="laya-guard")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check"); c.add_argument("text", nargs="*"); c.set_defaults(fn=cmd_check)
    s = sub.add_parser("serve"); s.add_argument("--host", default="127.0.0.1"); s.add_argument("--port", type=int, default=8787); s.set_defaults(fn=cmd_serve)
    args = ap.parse_args(argv)
    return args.fn(args)

if __name__ == "__main__":
    raise SystemExit(main())
