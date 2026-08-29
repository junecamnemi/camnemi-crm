#!/usr/bin/env python3
"""
Daily 2027 guide checker — BA / MA / Language school for foreign students.

Re-checks the schools that were NOT yet 2027 on the last pass and updates the
master report (_guide_2027_master.csv/.json). Used by a daily cron job.

Flow:
  1. Re-scrape adiga.kr 2027 foreign guides (scripted, cheap) → catches new BA
     guides published on adiga since yesterday.
  2. Load the previous master report to find the "not yet 2027" set per track.
  3. For each still-pending school, check its official site for a NEWLY
     published 2027 guide (own-site BA / MA grad sites / lang sites).
     [Browser subagents handle the actual page checks — this script prepares
      the pending lists and merges results.]
  4. Rebuild the master + summary reports and emit a "new today" diff.

Outputs (in C:/Users/USER/camnemi-crm/backend/):
  _guide_2027_master.csv/.json   updated per-school 3-track status
  _guide_2027_summary.csv        compact summary
  _daily_pending.json            pending-school list for the subagent pass
  _daily_new.json                schools newly confirmed 2027 this run
"""
import json, os, re, csv, datetime, glob

BASE = r"C:/Users/USER/camnemi-crm/backend"
OUT = BASE
ADIGA27 = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강"
SCRAPE = os.path.join(ADIGA27, "scrape_adiga_2027.py")

TRACK_KEY = {"BA": "ba_status", "MA": "ma_status", "lang": "lang_status"}
OK_2027 = {"2027_own", "2027_adiga", "2027_guide"}
# statuses that mean "not confirmed 2027 yet, worth re-checking"
PENDING = {"2026_or_older", "unknown_year", "error", "2026_only", "?", "none"}


def run_adiga_scrape():
    """Re-run the adiga 2027 scrape; returns count of newly downloaded files."""
    import subprocess, sys
    if not os.path.exists(SCRAPE):
        print("[adiga] scrape script missing:", SCRAPE)
        return 0
    r = subprocess.run([sys.executable, SCRAPE], capture_output=True, text=True, timeout=600)
    print("[adiga] scrape exit:", r.returncode)
    # count files now on disk (foreign folder)
    fdir = os.path.join(ADIGA27, "외국인")
    n = len([f for f in os.listdir(fdir) if not f.startswith(".")]) if os.path.isdir(fdir) else 0
    return n


def load_avail(year):
    """adiga availability set for a given year (stripped names)."""
    path = rf"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_{year}_외국인_모집요강/download_manifest.csv"
    out = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                if r["doc_type"] == "외국인" and r["available"].lower() == "true":
                    out.add(re.sub(r"\[.*?\]", "", r["university"]).strip())
    return out


def build_pending(master):
    """Return per-track list of schools still needing a 2027 check."""
    pend = {}
    for track, key in TRACK_KEY.items():
        schools = []
        for r in master:
            if r[key] not in OK_2027:
                schools.append({
                    "school": r["school"], "type": r.get("type", ""),
                    "name_en": r.get("name_en", ""), "status": r[key],
                    "url": r.get("ba_src" if track == "BA" else r.get("ma_src" if track == "MA" else "lang_src"), ""),
                    "ba_src": r.get("ba_src", ""), "ma_src": r.get("ma_src", ""),
                    "lang_src": r.get("lang_src", ""),
                })
        pend[track] = schools
    return pend


def main():
    today = datetime.date.today().isoformat()
    print("=== Daily 2027 guide checker", today, "===")

    # 0) auto-fill deadlines from newly downloaded adiga PDFs into verified_kb.json
    try:
        import auto_fill_periods
        print("[deadlines] running auto_fill_periods ...")
        auto_fill_periods.main()
    except Exception as e:
        print("[deadlines] auto_fill_periods failed:", e)

    # 0b) rebuild the guide reference map (2027 vs 2026 status) in verified_kb.json
    try:
        import build_guide_map
        print("[guide] rebuilding guide reference map ...")
        build_guide_map.main()
    except Exception as e:
        print("[guide] rebuild failed:", e)

    # 1) adiga re-scrape (BA source of truth)
    n_files = run_adiga_scrape()
    print("[adiga] foreign guides on disk now:", n_files)
    avail27 = load_avail(2027)
    avail26 = load_avail(2026)

    # 2) load previous master
    mpath = os.path.join(OUT, "_guide_2027_master.json")
    master = json.load(open(mpath, encoding="utf-8")) if os.path.exists(mpath) else []
    if not master:
        print("ERROR: no existing master report; run the initial compile first.")
        return

    # 3) update adiga status for BA (cheap, scripted)
    for r in master:
        s = r["school"]
        if s in avail27:
            if r["ba_status"] != "2027_adiga":
                r["ba_status"] = "2027_adiga"
                r["ba_url"] = "adiga_2027 (downloaded)"
                r["ba_title"] = ""
        elif s in avail26 and r["ba_status"] not in OK_2027:
            r["ba_status"] = "2026_or_older"

    # 4) build pending lists for the subagent browser pass
    pending = build_pending(master)
    json.dump(pending, open(os.path.join(OUT, "_daily_pending.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    for track, lst in pending.items():
        print(f"[pending] {track}: {len(lst)} schools still need a 2027 check")

    # save the updated master (adiga statuses refreshed)
    json.dump(master, open(mpath, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("[saved] master report updated (adiga statuses). Pending lists written to _daily_pending.json")


if __name__ == "__main__":
    main()
