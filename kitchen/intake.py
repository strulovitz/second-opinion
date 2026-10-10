"""kitchen/intake.py -- STEP A0: book intake (BIBLE part 3, section 2.1).

For every PDF in kitchen/books/ record:
  - pdfinfo: Pages, Title, Page size, Producer, CreationDate
  - pdffonts on the first 5 pages: does a text layer exist?
  - pdftotext on the page about 40% into the book: is that page readable?

Nothing is written to Neo4j here and nothing is renamed or modified.
Output: kitchen/logs/intake.json
"""
import json
import re
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

KITCHEN = Path(__file__).resolve().parent
BOOKS = KITCHEN / "books"
LOGS = KITCHEN / "logs"


def run(cmd):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        return p.stdout or ""
    except Exception as exc:  # noqa: BLE001 - recorded, never swallowed
        return f"__ERROR__ {exc}"


def info_for(pdf: Path) -> dict:
    raw = run(["pdfinfo", str(pdf)])
    rec = {"pdf_file": pdf.name, "pdf_bytes": pdf.stat().st_size}

    m = re.search(r"^Pages:\s+(\d+)", raw, re.M)
    rec["pages"] = int(m.group(1)) if m else None
    m = re.search(r"^Title:\s+(.*)$", raw, re.M)
    rec["pdf_title"] = m.group(1).strip() if m else ""
    m = re.search(r"^Page size:\s+(.*)$", raw, re.M)
    rec["page_size"] = m.group(1).strip() if m else ""
    m = re.search(r"^Producer:\s+(.*)$", raw, re.M)
    rec["producer"] = m.group(1).strip() if m else ""
    m = re.search(r"^CreationDate:\s+(.*)$", raw, re.M)
    rec["creation_date"] = m.group(1).strip() if m else ""

    fonts = run(["pdffonts", "-f", "1", "-l", "5", str(pdf)])
    rec["fonts_head"] = [ln for ln in fonts.splitlines() if ln.strip()][:6]
    rec["text_layer"] = bool(fonts.strip()) and not fonts.startswith("__ERROR__")

    n = rec["pages"] or 1
    probe = max(1, int(n * 0.4))
    body = run(["pdftotext", "-f", str(probe), "-l", str(probe), str(pdf), "-"])
    rec["probe_image"] = probe
    rec["probe_chars"] = 0 if body.startswith("__ERROR__") else len(body.strip())
    rec["probe_ok"] = rec["probe_chars"] > 500
    rec["probe_sample"] = "" if body.startswith("__ERROR__") else body.strip()[:200]
    return rec


def main():
    LOGS.mkdir(exist_ok=True)
    pdfs = sorted(BOOKS.glob("*.pdf"))
    print(f"scanning {len(pdfs)} PDFs ...", flush=True)
    with ProcessPoolExecutor(max_workers=6) as pool:
        records = list(pool.map(info_for, pdfs))
    out = LOGS / "intake.json"
    out.write_text(json.dumps(records, indent=1, ensure_ascii=False))
    print(f"wrote {out}")
    ok = sum(1 for r in records if r["probe_ok"])
    print(f"readable probe page: {ok}/{len(records)}")
    missing_pages = [r["pdf_file"] for r in records if not r["pages"]]
    if missing_pages:
        print("NO PAGE COUNT (needs attention):")
        for f in missing_pages:
            print("  ", f)


if __name__ == "__main__":
    sys.exit(main())