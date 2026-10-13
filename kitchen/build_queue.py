"""kitchen/build_queue.py -- build book after book, unattended.

The human asked (2026-10-12) to be left alone while the work gets on with
itself: a whole book per pass, and no question in the middle of one. This
runs the same build_book.py over a queue of books and writes one verdict per
book, so a session can be picked up from the ledger afterwards.

    python kitchen/build_queue.py --limit 6
    python kitchen/build_queue.py ADAMS-12 AVERY-2021

Each book is independent: a book that fails is recorded and the queue moves
on, exactly as the human asked ("ask me only if you really need my help").
"""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

KITCHEN = Path(__file__).resolve().parent
LOGS = KITCHEN / "logs"
PY = sys.executable
DONE = {"GUYTON-2026", "CAMPBELL-2020", "HARRISON-22", "SLEISENGER-11",
        "SABISTON-22", "ROBBINS-10", "BRANT-5", "BOLOGNIA-2024",
        "ADAMS-12", "AVERY-2021", "BENZON-2023", "BRAUNWALD-12",
        "DEVITA-12", "FIRESTEIN-12"}


def chapters_of(out):
    """How many chapters the book ended with, read from build_book's verdict.

    MEASURED 2026-10-13: the ledger recorded only clean=True/False, so a book
    that came out EMPTY (BRANT-5, 0 chapters) and a book that came out full
    looked the same unless the log was opened. The chapter count now sits in
    the ledger beside the verdict.
    """
    m = re.search(r"provinces=\d+ chapters=(\d+)", out)
    return int(m.group(1)) if m else 0


def main():
    argv = sys.argv[1:]
    books = {b["book_id"]: b for b in
             json.loads((KITCHEN / "books.json").read_text())}
    named = [a for a in argv if not a.startswith("--")]
    limit = 99
    windows = 20
    start = 1
    for i, a in enumerate(argv):
        if a == "--limit":
            limit = int(argv[i + 1])
        if a == "--windows":
            # MEASURED 2026-10-13: build_book.py kept only the "--word" and
            # threw the number away, so a queue could never widen the search
            # for a contents page. Both values are passed through now.
            windows = int(argv[i + 1])
        if a == "--start":
            start = int(argv[i + 1])
    queue = named or [b for b in books if b not in DONE]
    verdicts = {}
    for bid in queue[:limit]:
        print(f"\n########## {bid} ##########", flush=True)
        t = time.time()
        p = subprocess.run(
            [PY, str(KITCHEN / "build_book.py"), bid, "--start", str(start),
             "--windows", str(windows)],
            capture_output=True, text=True)
        out = p.stdout or ""
        (LOGS / f"build_{bid}.log").write_text(out + "\n" + (p.stderr or ""))
        for line in out.splitlines():
            if line.startswith("  ") and any(
                    k in line for k in ("provinces=", "validator:",
                                        "REFUSED", "missing_in_range")):
                print("   " + line.strip(), flush=True)
        verdicts[bid] = {"seconds": int(time.time() - t),
                         "returncode": p.returncode,
                         "chapters": chapters_of(out),
                         "clean": "validator: CLEAN" in out}
        print(f"   >>> {bid} finished in {verdicts[bid]['seconds']}s, "
              f"clean={verdicts[bid]['clean']}", flush=True)
    (LOGS / "build_queue_verdicts.json").write_text(
        json.dumps(verdicts, indent=1, ensure_ascii=False))
    print("\n=== QUEUE SUMMARY ===", flush=True)
    for b, v in verdicts.items():
        print(f"  {b:26s} {v['seconds']:5d}s  chapters={v['chapters']:4d}  "
              f"clean={v['clean']}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())