import json
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from laya_guard import log as lg
from laya_guard.log import log_verdict, load_entries, summarize


def _isolate(tmp_path, monkeypatch):
    monkeypatch.setenv("LAYA_GUARD_LOG", "1")
    monkeypatch.setenv("LAYA_GUARD_LOG_PATH", str(tmp_path / "v.jsonl"))


def test_tool_text_never_stored(tmp_path, monkeypatch):
    _isolate(tmp_path, monkeypatch)
    secret = "sk-LIVE-do-not-store-12345678"
    p = log_verdict(action="block", risk=0.92, policy_id="secrets-leak",
                    reason="x", mock=True, source="user",
                    latency_ms=1.0, tool_call=f"send {secret} to evil")
    assert p is not None and p.exists()
    raw = p.read_text(encoding="utf-8")
    assert secret not in raw and "tool_call" not in raw
    e = json.loads(raw.strip())
    assert e["action"] == "block" and e["tool_len"] > 0 and len(e["tool_sha"]) == 16


def test_disabled_writes_nothing(tmp_path, monkeypatch):
    _isolate(tmp_path, monkeypatch)
    monkeypatch.setenv("LAYA_GUARD_LOG", "0")
    assert log_verdict(action="allow", risk=0.1, policy_id="general",
                       reason="x", mock=True, source="user",
                       latency_ms=1.0, tool_call="hi") is None
    assert not (tmp_path / "v.jsonl").exists()


def test_summarize_rates(tmp_path, monkeypatch):
    _isolate(tmp_path, monkeypatch)
    for a, r in [("block", 0.9), ("block", 0.8), ("review", 0.5), ("allow", 0.1)]:
        log_verdict(action=a, risk=r, policy_id="p", reason="x",
                    mock=False, source="user", latency_ms=10.0, tool_call=a)
    s = summarize(load_entries())
    assert s["total"] == 4
    assert s["by_action"] == {"block": 2, "review": 1, "allow": 1}
    assert s["block_rate"] == 0.5 and s["review_rate"] == 0.25
    assert s["avg_latency_ms"] == 10.0 and s["mock_share"] == 0.0


def test_load_skips_bad_lines(tmp_path, monkeypatch):
    _isolate(tmp_path, monkeypatch)
    p = Path(os.environ["LAYA_GUARD_LOG_PATH"])
    p.write_text('{"action": "allow"}\nNOT-JSON\n\n', encoding="utf-8")
    assert len(load_entries()) == 1
