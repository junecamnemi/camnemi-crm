#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 1 — locate each remaining school's 등록금일람표 (fees) page.

The KB carries no homepage field, only guide_url/apply_source, so the domain is derived from those.
Probes, in order: https://fees.<domain>/ · https://<domain>/fees · https://<domain>/
then records which host/board actually answers, so phase 2 only fetches real pages.

  python _fees_locate.py --limit 8          # probe a sample and print what responded
  python _fees_locate.py --all              # probe every target in _tuition_targets_B.json(+A1)

Writes backend/_fees_locate.json — {school: {domain, candidates:[{url,status,title,snippet}]}}
"""
import os, re, json, sys, urllib.request, urllib.error, socket, concurrent.futures

B = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(B, "_fees_locate.json")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")
socket.setdefaulttimeout(12)


def load_kb():
    import importlib.util
    spec = importlib.util.spec_from_file_location("tpf", os.path.join(B, "_tuition_pro_fill.py"))
    tpf = importlib.util.module_from_spec(spec)
    argv = sys.argv[:]; sys.argv = ["x"]
    try:
        spec.loader.exec_module(tpf)
    except SystemExit:
        pass
    sys.argv = argv
    return tpf.load_kb()


def domain_of(v):
    """Registrable-ish domain from any URL the KB holds (kw.ac.kr, cju.ac.kr, …)."""
    for key in ("guide_url", "guide_page_url", "apply_source", "source", "apply_evidence"):
        val = v.get(key)
        if not isinstance(val, str):
            continue
        m = re.search(r"https?://([^/]+)", val)
        if not m:
            continue
        host = m.group(1).lower().split(":")[0]
        host = re.sub(r"^(www|admission|oia|iphak|enter|ipsi|grad)\.", "", host)
        parts = host.split(".")
        if len(parts) >= 3 and parts[-2] in ("ac", "go", "or", "ne", "co"):
            return ".".join(parts[-3:])
        if len(parts) >= 2 and parts[-1] == "kr":
            return ".".join(parts[-2:])
    return None


def fetch(url, timeout=12):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ko,en;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read(400_000)
            enc = r.headers.get_content_charset() or "utf-8"
            try:
                html = raw.decode(enc, "replace")
            except Exception:
                html = raw.decode("utf-8", "replace")
            return {"status": r.status, "url": r.geturl(), "html": html}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "url": url, "html": ""}
    except Exception as e:
        return {"status": f"ERR:{type(e).__name__}", "url": url, "html": ""}


def probe(school, lvl, v):
    dom = domain_of(v)
    res = {"school": school, "level": lvl, "domain": dom, "candidates": []}
    if not dom:
        res["note"] = "no domain in KB (guide_url/apply_source empty)"
        return res
    for cand in (f"https://fees.{dom}/", f"https://{dom}/fees", f"https://{dom}/"):
        r = fetch(cand)
        title = ""
        m = re.search(r"<title[^>]*>(.*?)</title>", r["html"], re.S | re.I)
        if m:
            title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip()[:100]
        # does the landing page link to anything fee-like?
        links = re.findall(r'href="([^"]+)"[^>]*>([^<]{0,60})', r["html"])[:400]
        hits = [(u, t.strip()) for u, t in links
                if re.search(r"등록금|일람표|fee", u + " " + t, re.I)][:5]
        res["candidates"].append({"url": r["url"], "status": r["status"], "title": title,
                                  "fee_links": [{"href": u, "text": t} for u, t in hits]})
        if r["status"] == 200 and (hits or "등록금" in title or "Fees" in title or "fee" in title.lower()):
            break
    return res


def main():
    idx = load_kb()
    tg = []
    for f in ("_tuition_targets_B.json", "_tuition_targets_A1.json"):
        p = os.path.join(B, f)
        if os.path.exists(p):
            tg += json.load(open(p, encoding="utf-8"))
    if "--all" not in sys.argv:
        lim = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 8
        tg = tg[:lim]
    print(f"locating fees pages for {len(tg)} targets")
    out = {}
    workers = 6
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(probe, t["school"], t["level"], idx.get((t["school"], t["level"]), {})): t for t in tg}
        for f in concurrent.futures.as_completed(futs):
            r = f.result()
            out[r["school"]] = r
            best = next((c for c in r["candidates"] if c["status"] == 200), None)
            flag = "✔" if (best and (best["fee_links"] or re.search(r"등록금|fee", best["title"], re.I))) else "·"
            print(f"  {flag} {r['school'][:16]:18} dom={r['domain'] or '-':16} "
                  f"{best['status'] if best else r.get('note','-')} "
                  f"{(best['title'][:38] if best else '')} "
                  f"{('links='+str(len(best['fee_links']))) if best else ''}")
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("WROTE", OUT)


if __name__ == "__main__":
    main()