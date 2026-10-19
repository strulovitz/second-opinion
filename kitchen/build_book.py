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
    # MEASURED 2026-10-13: keeping only the "--word" arguments silently threw
    # the VALUE away, so "--windows 40" reached toc_vision.py as "--windows"
    # and the book was read with the default 20 windows. An option and its
    # value are now passed through together.
    extra = argv[1:]
    print(f"=== BUILDING {bid} ===", flush=True)

    # 1. locate + read with the model's eyes (the only stage that costs time)
    # --no-read rebuilds the book from the transcription ALREADY on disk, so a
    # parser fix or a validator fix costs no model time at all.
    if "--no-read" not in extra:
        run("toc_vision.py", [bid] + [a for a in extra if a != "--no-read"])
    else:
        print("  (--no-read: rebuilding from the saved transcription, no "
              "model call)", flush=True)

    # MEASURED 2026-10-13 on BRADDOM-6 and BRENNER-11: when the reader names
    # no contents page, toc_vision.py writes no JSON and the six bookkeeping
    # steps behind it then fail one after another with FileNotFoundError,
    # which looks like a crash rather than "this book has no contents page
    # yet". Stop here and say so plainly.
    if not (LOGS / f"{bid}-vis-toc.json").exists():
        print("=== VERDICT ===", flush=True)
        print("  NO CONTENTS PAGE WAS FOUND -- nothing was read, nothing was "
              "invented. Next: a wider --windows, then toc_openers.py.", flush=True)
        return 1

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

    # 4b. the provinces are always rebuilt LAST.
    # MEASURED 2026-10-13 on BRANT-5: the step before this one starts again
    # from the transcript and therefore throws the provinces away, so with
    # --no-gaps the book ended flat with 1 province and 83 chapters. The
    # headings are the last thing that decides the geography.
    if (LOGS / f"{bid}-vis-headings.json").exists():
        run("toc_apply_headings.py", [bid], must=False)

    # 4c. a multi-volume book prints "PART 1" again for every volume, so the
    # same part can arrive twice and a truncated read can invent a part that is
    # only a slice of the part before it (MEASURED 2026-10-19 on YOUMANS-4:
    # 12 chapters counted twice, one false "PART 3"). It must run after the
    # provinces are rebuilt, because that rebuild throws them away.
    run("toc_merge_dup_provinces.py", [bid], must=False)

    # 5. the honest check
    ok, out = run("toc_validate.py", [bid, "--vis"], must=False)

    got = numbers(bid)
    print("=== VERDICT ===", flush=True)
    if not got:
        print("  NO JSON PRODUCED", flush=True)
        return 1
    provs, ch = got
    lettered = [c["number"] for c in ch
                if c.get("number") and not str(c["number"]).isdigit()]
    nums = sorted(int(c["number"]) for c in ch if str(c.get("number")).isdigit())
    gaps = [n for n in range(1, (max(nums) if nums else 0) + 1)
            if n not in set(nums)]
    pages_seen = [c.get("page_start") for c in ch if c.get("page_start")]
    nopage = len(ch) - len(pages_seen)
    # MEASURED 2026-10-13: BRANT-5 was reported "validator: CLEAN" with 0
    # chapters, because the verdict string was searched inside the validator's
    # output instead of being read from the result. An empty book is never
    # clean: 0 chapters is a FAILED build, and a book with no printed pages
    # is reported as such rather than counted as read.
    val_ok = f"RESULT {bid} ok" in out
    clean = bool(val_ok and ch)
    print(f"  provinces={provs} chapters={len(ch)}", flush=True)
    if gaps and not lettered:
        print(f"  numbered {min(nums)}..{max(nums)} unique={len(set(nums))} "
              f"missing_in_range={len(gaps)}", flush=True)
        print(f"  first missing numbers: {gaps[:20]}", flush=True)
    elif lettered:
        # MEASURED 2026-10-13 on BRANT-5: the book itself prints "32A", "36B",
        # "71A", so those numbers are simply not printed bare and a missing
        # number is not a missing chapter.
        print(f"  numbered {min(nums) if nums else '-'}.."
              f"{max(nums) if nums else '-'} unique={len(set(nums))}; "
              f"{len(lettered)} lettered chapter number(s) as the book prints "
              f"them: {' '.join(str(x) for x in lettered[:8])}", flush=True)
    else:
        print(f"  numbered {min(nums) if nums else '-'}.."
              f"{max(nums) if nums else '-'} unique={len(set(nums))} "
              f"missing_in_range=0", flush=True)
    print(f"  printed pages {min(pages_seen) if pages_seen else '-'}.."
          f"{max(pages_seen) if pages_seen else '-'}"
          + (f" ({nopage} chapter(s) print no page at all)" if nopage else ""),
          flush=True)
    if not ch:
        print("  validator: FAILED -- 0 chapters, this book is EMPTY", flush=True)
    else:
        print(f"  validator: {'CLEAN' if val_ok else 'WARNED'}", flush=True)
    if refused:
        print(f"  REFUSED look-alike pages: {refused}", flush=True)
    return 0 if clean else 1


if __name__ == "__main__":
    sys.exit(main())