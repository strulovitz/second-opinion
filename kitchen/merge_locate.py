"""kitchen/merge_locate.py -- write the located TOC/Index page ranges from
kitchen/logs/locate.json back into kitchen/books.json (BIBLE part 3, 2.4).

Books whose TOC or index could not be found are left null and listed in the
report. They are NOT guessed (Law 11).
"""
import json
from pathlib import Path

KITCHEN = Path(__file__).resolve().parent
BOOKS = KITCHEN / "books.json"
LOCATE = KITCHEN / "logs" / "locate.json"

# Books verified to have NO back-of-book printed index (checked by hand).
# The BIBLE does not require an index; the reader simply cannot use one.
NO_INDEX = {
    "THOMPSON-2023": "612-page book, no back-of-book index",
    "ROBBINS-10": "no back-of-book index detected in the last 400 images",
}


def main():
    books = json.loads(BOOKS.read_text())
    loc = {r["book_id"]: r for r in json.loads(LOCATE.read_text())}
    for b in books:
        r = loc.get(b["book_id"])
        if not r:
            continue
        b["toc_images"] = r["toc_images"]
        b["index_images"] = r["index_images"]
        if b["book_id"] in NO_INDEX and not b["index_images"]:
            b["index_images"] = None
            note = f"verified: {NO_INDEX[b['book_id']]}"
            b["notes"] = (b["notes"] + "; " + note).strip("; ")
    BOOKS.write_text(json.dumps(books, indent=1, ensure_ascii=False))

    cand = [b for b in books if b["status"] == "candidate"]
    print(f"merged into books.json: {len(cand)} candidate books")
    print(f"  with toc_images:    {sum(1 for b in cand if b['toc_images'])}/{len(cand)}")
    print(f"  with index_images:  {sum(1 for b in cand if b['index_images'])}/{len(cand)}")
    print("\nstill open (need a human eye or vision fallback):")
    for b in cand:
        if not b["toc_images"] or not b["index_images"]:
            miss = []
            if not b["toc_images"]:
                miss.append("TOC")
            if not b["index_images"]:
                miss.append("index")
            print(f"  {b['book_id']:26s} missing: {', '.join(miss)}")


if __name__ == "__main__":
    main()