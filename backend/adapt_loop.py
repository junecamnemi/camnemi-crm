#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""adapt_loop.py — the ⑥ ADAPT step (ARCHITECTURE §3/§8). Proposes, never auto-applies.

Commands:
  status                     show current tier→model assignments
  rank [--bench B]           rank candidate models from a benchmark file -> propose T1
  check [--jsonl P]          golden-set regression on the current production parse -> rollback proposal
  apply --tier T1 --model M  apply a change (records history; keeps last_good)
  rollback                   restore last_good

Guardrails (model_config.json): golden pass >= 0.8, json success >= 0.95, auto_apply=false.
"""
import os, re, json, glob, argparse, subprocess, sys, datetime

B = r"C:\Users\USER\camnemi-crm\backend"
CFG = os.path.join(B, "model_config.json")
BENCH = os.path.join(B, "model_bench.json")

def load():
    return json.load(open(CFG, encoding="utf-8"))

def save(c):
    c["updated"] = datetime.date.today().isoformat()
    open(CFG, "w", encoding="utf-8", newline="\n").write(json.dumps(c, ensure_ascii=False, indent=1) + "\n")

def upstream_cost(u):
    cd = (u or {}).get("cost_details") or {}
    v = cd.get("upstream_inference_cost")
    if v is not None:
        return float(v)
    return float((u or {}).get("cost") or 0)

def cmd_status(a):
    c = load()
    print("=== 티어별 모델 (model_config.json) ===")
    for t, d in c["tiers"].items():
        print(f"  {t}: {d['model']:36s} — {d['role']}")
    lg = c.get("last_good", {})
    print(f"\nlast_good: {lg.get('date')} (golden pass {lg.get('golden_pass_rate')})")
    print(f"guardrails: pass≥{c['guardrails']['golden_pass_threshold']} · json≥{c['guardrails']['min_json_success']} · auto_apply={c['guardrails']['auto_apply']}")

def cmd_rank(a):
    bench = json.load(open(a.bench or BENCH, encoding="utf-8"))
    rows = []
    for model, m in bench.items():
        tot = m["ok"] + m["json_fail"] + m["trunc"] + m["err"]
        succ = m["ok"] / tot if tot else 0
        jac = sum(m["jac"]) / len(m["jac"]) if m["jac"] else 0
        cost = m.get("cost_real") or m.get("cost") or 0
        ms = sum(m["ms"]) / len(m["ms"]) if m["ms"] else 0
        # score: reliability-gated accuracy per cost
        ok_gate = succ >= 0.95
        eff = (jac * succ) / (cost * 1000 + 0.001) if ok_gate else 0
        rows.append({"model": model, "json_success": round(succ, 2), "jaccard": round(jac, 2),
                     "cost": round(cost, 5), "ms": round(ms, 1), "gate": ok_gate, "eff": round(eff, 1)})
    rows.sort(key=lambda r: (-r["gate"], -r["eff"]))
    print("=== 모델 순위 (신뢰성 게이트 × 정확도/비용) ===")
    print(f"{'model':34s} {'json':>5} {'jacc':>5} {'cost$':>8} {'ms':>6} {'gate':>5} {'eff':>7}")
    for r in rows:
        print(f"{r['model']:34s} {r['json_success']:>5} {r['jaccard']:>5} {r['cost']:>8} {r['ms']:>6} "
              f"{'PASS' if r['gate'] else 'FAIL':>5} {r['eff']:>7}")
    best = rows[0] if rows and rows[0]["gate"] else None
    cur = load()["tiers"]["T1"]["model"]
    print()
    if best and best["model"] != cur:
        print(f"💡 제안: T1을 '{cur}' → '{best['model']}' 로 교체 고려")
        print(f"   근거: json {best['json_success']} · jaccard {best['jaccard']} · cost {best['cost']} · {best['ms']}ms")
        print(f"   적용: python adapt_loop.py apply --tier T1 --model {best['model']}")
    elif best:
        print(f"✅ 현재 T1('{cur}')이 이미 최우수 — 변경 불필요")
    else:
        print("⚠️ 신뢰성 게이트(0.95)를 통과한 모델 없음 — 현행 유지 권고")

def cmd_check(a):
    c = load()
    thr = c["guardrails"]["golden_pass_threshold"]
    jsonl = a.jsonl or os.path.join(B, "guides_llm_parsed.jsonl")
    print(f"Golden Set 회귀 실행 (기준선 대비): {os.path.basename(jsonl)}")
    r = subprocess.run([sys.executable, os.path.join(B, "golden_set.py"), "run", jsonl],
                       capture_output=True, text=True, cwd=B)
    print(r.stdout.strip() or r.stderr.strip()[:400])
    m = re.search(r"통과율\s+(\d+)%", r.stdout or "")
    rate = int(m.group(1)) / 100 if m else None
    print()
    if rate is None:
        print("⚠️ 통과율 파싱 실패 — 수동 확인 필요"); return
    if rate >= thr:
        print(f"✅ 통과율 {rate:.0%} ≥ {thr:.0%} — 롤백 불필요")
    else:
        lg = c.get("last_good", {})
        print(f"🚨 통과율 {rate:.0%} < {thr:.0%} — 품질 저하!")
        print(f"   롤백 제안: T1→{lg.get('T1')} · T2→{lg.get('T2')} · T3→{lg.get('T3')} (last_good {lg.get('date')})")
        print(f"   적용: python adapt_loop.py rollback")

def cmd_apply(a):
    c = load()
    t = a.tier.upper()
    if t not in c["tiers"]:
        print("알 수 없는 티어:", t); return
    old = c["tiers"][t]["model"]
    c["tiers"][t]["model"] = a.model
    c.setdefault("history", []).append({"date": datetime.date.today().isoformat(), "tier": t,
                                        "from": old, "to": a.model, "by": "human-approved"})
    save(c)
    print(f"적용: {t} {old} → {a.model} (이력 기록)")
    print(f"⚠️ 크론 반영 필요: hermes --profile univ cron edit <id> --provider nous --model {a.model}")

def cmd_rollback(a):
    c = load()
    lg = c.get("last_good", {})
    for t in ("T1", "T2", "T3"):
        if lg.get(t) and c["tiers"][t]["model"] != lg[t]:
            c.setdefault("history", []).append({"date": datetime.date.today().isoformat(), "tier": t,
                                                "from": c["tiers"][t]["model"], "to": lg[t], "by": "rollback"})
            c["tiers"][t]["model"] = lg[t]
    save(c)
    print("롤백 완료 → last_good 복원:")
    for t, d in c["tiers"].items():
        print(f"  {t}: {d['model']}")

def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    r = sub.add_parser("rank"); r.add_argument("--bench"); r.set_defaults(fn=cmd_rank)
    c = sub.add_parser("check"); c.add_argument("--jsonl"); c.set_defaults(fn=cmd_check)
    a1 = sub.add_parser("apply"); a1.add_argument("--tier", required=True); a1.add_argument("--model", required=True); a1.set_defaults(fn=cmd_apply)
    sub.add_parser("rollback").set_defaults(fn=cmd_rollback)
    a = ap.parse_args(); a.fn(a)

if __name__ == "__main__":
    main()
