#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Price/callability probe: 1 tiny call per candidate model, report tokens+cost."""
import json, os, re, time, urllib.request

def _auth():
    d = json.load(open(r"C:\Users\USER\AppData\Local\hermes\shared\nous_auth.json", encoding="utf-8"))
    return d["access_token"], d["inference_base_url"].rstrip("/")

KEY, BASE = _auth()
CAND = [
    "stepfun/step-3.7-flash",
    "z-ai/glm-5.3-flash",
    "z-ai/glm-5.2",
    "deepseek/deepseek-v4-flash-0731",
    "google/gemini-3.8-flash",
    "qwen/qwen3.8-flash",
    "minimax/minimax-m3",
    "tencent/hy3",
    "nvidia/nemotron-3-super-120b-a12b",
    "openai/gpt-5.4-mini",
]

def probe(model):
    body = {"model": model, "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
            "max_tokens": 200, "temperature": 0}
    req = urllib.request.Request(BASE + "/chat/completions", data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            j = json.loads(r.read().decode())
        u = j.get("usage", {})
        cd = u.get("cost_details") or {}
        return {"ok": True, "ms": round((time.time()-t0)*1000), "in": u.get("prompt_tokens"),
                "out": u.get("completion_tokens"), "cost": u.get("cost"),
                "upstream": cd.get("upstream_inference_cost")}
    except Exception as e:
        return {"ok": False, "err": str(e)[:80]}

print(f"{'model':40s} {'ok':>4} {'ms':>6} {'in':>6} {'out':>5} {'upstream$':>12}")
for m in CAND:
    r = probe(m)
    if r["ok"]:
        print(f"{m:40s} {'Y':>4} {r['ms']:>6} {r['in']:>6} {r['out']:>5} {str(r['upstream']):>12}")
    else:
        print(f"{m:40s} {'N':>4}  {r['err']}")
