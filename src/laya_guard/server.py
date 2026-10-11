"""laya-guard HTTP server. POST /guard + Jev-compatible POST /v1/systemone."""
from __future__ import annotations
from fastapi import FastAPI
from pydantic import BaseModel
from .guard import judge, is_mock

app = FastAPI(title="laya-guard")

class GuardReq(BaseModel):
    tool_call: str = ""
    state: str = ""
    source: str = "user"  # user | tool | email | web

class GuardRes(BaseModel):
    action: str
    risk: float
    policy_id: str
    reason: str
    mock: bool

@app.get("/health")
def health():
    return {"ok": True, "mock": is_mock()}

@app.post("/guard", response_model=GuardRes)
def guard(req: GuardReq):
    text = req.tool_call or req.state
    v = judge(text, source=req.source)
    return GuardRes(action=v.action, risk=v.risk, policy_id=v.policy_id, reason=v.reason, mock=v.mock)

@app.post("/v1/systemone")
def systemone(body: dict):
    # Jev drop-in: {state, questions} -> laya-guard verdict mapped back
    state = body.get("state", "") if isinstance(body, dict) else ""
    if isinstance(state, dict):
        import json
        state = json.dumps(state, ensure_ascii=False)
    v = judge(str(state), source=str(body.get("source", "user")) if isinstance(body, dict) else "user")
    return {
        "answers": {
            "action": {"choice": v.action},
            "risk": {"score": v.risk},
        },
        "verdict": v.action,
        "policy_id": v.policy_id,
        "reason": v.reason,
        "mock": v.mock,
    }

def run(host: str = "127.0.0.1", port: int = 8787):
    import uvicorn
    uvicorn.run(app, host=host, port=port)
