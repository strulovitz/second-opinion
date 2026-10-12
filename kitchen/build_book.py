"""kitchen/build_book.py -- take ONE book from raw PDF to a verified TOC.

The human asked (2026-10-12) that a whole book be done without stopping to
ask him anything in the middle. This script is that: locate -> read ->
dedupe -> sort -> repair -> headings -> rebuild -> validate, and it prints a
verdict at the end. Nothing is invented at any step and every page the
reader refused is reported, never dropped.

    python kitchen/build_book.py SABISTON-22
    python kitchen/build_book.py ROBBINS-10 --start 1 --windows 20

It runs the same scripts that were proven on GUYTON-2026, CAMPBELL-2020,
HARRISON-22 and SLEISENGER-11, in that order, and each one regenerates its
JSON from the reader's own recorded words, so a parser fix costs no model
time at all.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

KITCHEN = Path(__file__).resolve().parent
LOGS = KITCHEN / "logs"
PY = sys.executable


def run(step, args, must=True):
    t = time.time()
    p = subprocess.run([PY, str(KITCHEN / step)] + args,
                       capture_output=True, text=True)
    out = (p.stdout or "").strip()
    err = (p.stderr or "").strip()
    ok = p.returncode == 0
    print(f"  -- {step} ({int(time.time()-t)}s) "
          f"{'ok' if ok else 'FAILED'}", flush=True)
    for line in out.splitlines()[-14:]:
        print(f"     {line}", flush=True)
    if not ok:
        for line in err.splitlines()[-8:]:
            print(f"     ! {line}", flush=True)
    if must and not ok:
        raise SystemExit(f"   {step} failed for {args}")
    return ok, out


def numbers(bid):
    f = LOGS / f"{bid}-vis-toc.json"
    if not f.exists():
        return None
    d = json.loads(f.read_text())
    ch = [c for p in d["provinces"] for c in p["chapters"]]
    return len(d["provinces"]), ch


def main():
    argv = sys.argv[1:]
    if not argv:
        print(__doc__)
        return 1
    bid = argv[0]
    extra = [a for a in argv[1:] if a.startswith("--")]
    print(f"=== BUILDING {bid} ===", flush=True)

    # 1. locate + read with the model's eyes (the only stage that costs time)
    run("toc_vision.py", [bid] + extra)

    pages = LOGS / f"{bid}-vis-pages.json"
    refused = json.loads(pages.read_text()).get("refused_lookalike") \
        if pages.exists() else []
    print(f"  look-alike pages refused: {refused or 'none'}", flush=True)

    # 2. pure bookkeeping on the model's own words -- no model calls
    run("toc_reparse.py", [bid])
    run("toc_strip_online_only.py", [bid], must=False)
    run("toc_dedupe.py", [bid, "--vis"], must=False)
    run("toc_sort_pages.py", [bid], must=False)
    run("toc_fix_misfiled.py", [bid], must=False)

    # 3. the Part/Section banners, asked for ALONE (they get misread while
    #    fifty chapter entries are being transcribed beside them)
    h = LOGS / f"{bid}-vis-headings.json"
    if not h.exists():
        run("toc_headings.py", [bid], must=False)
    if h.exists():
        run("toc_apply_headings.py", [bid], must=False)
        run("toc_reparse.py", [bid])
        run("toc_strip_online_only.py", [bid], must=False)
        run("toc_dedupe.py", [bid, "--vis"], must=False)
        run("toc_sort_pages.py", [bid], must=False)
        run("toc_fix_misfiled.py", [bid], must=False)

    # 4. fill numbered gaps by asking the model directly
    if "--no-gaps" not in extra:
        run("toc_fill_gaps.py", [bid], must=False)
        # a gap repair may answer with an "(online only)" entry and invent a
        # page for it; the strip runs again and the validator has the last word
        run("toc_reparse.py", [bid])
        run("toc_strip_online_only.py", [bid], must=False)
        run("toc_dedupe.py", [bid, "--vis"], must=False)
        run("toc_sort_pages.py", [bid], must=False)
        run("toc_fix_misfiled.py", [bid], must=False)
        run("toc_apply_headings.py", [bid], must=False)

    # 5. the honest check
    ok, out = run("toc_validate.py", [bid, "--vis"], must=False)

    got = numbers(bid)
    print("=== VERDICT ===", flush=True)
    if not got:
        print("  NO JSON PRODUCED", flush=True)
        return 1
    provs, ch = got
    nums = sorted(int(c["number"]) for c in ch if str(c.get("number")).isdigit())
    gaps = [n for n in range(1, (max(nums) if nums else 0) + 1)
            if n not in set(nums)]
    pages_seen = [c.get("page_start") for c in ch if c.get("page_start")]
    print(f"  provinces={provs} chapters={len(ch)}", flush=True)
    print(f"  numbered {min(nums) if nums else '-'}..{max(nums) if nums else '-'} "
          f"unique={len(set(nums))} missing_in_range={len(gaps)}", flush=True)
    if gaps:
        print(f"  first missing numbers: {gaps[:20]}", flush=True)
    print(f"  printed pages {min(pages_seen) if pages_seen else '-'}.."
          f"{max(pages_seen) if pages_seen else '-'}", flush=True)
    print(f"  validator: {'CLEAN' if ' clean' in out else 'WARNED'}", flush=True)
    if refused:
        print(f"  REFUSED look-alike pages: {refused}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())