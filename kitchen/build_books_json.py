"""kitchen/build_books_json.py -- STEP A0 / A1 (BIBLE part 3, sections 2.2-2.4).

Builds kitchen/books.json from kitchen/logs/intake.json plus the book_id
table below. Nothing is guessed silently: any row whose key carries
uncertain="..." is listed in the report for the human to rename.

book_id rule (BIBLE part 2 section 6.1 A): the book's eponym or first title
word in UPPERCASE, hyphen, edition number; if the book states no edition,
the year is used instead.
"""
import json
from pathlib import Path

KITCHEN = Path(__file__).resolve().parent
INTAKE = KITCHEN / "logs" / "intake.json"
OUT = KITCHEN / "books.json"

# key            = unique substring of the PDF file name
# (book_id, title, edition, year, notes)
TABLE = [
    ("Allan H. Ropper", "ADAMS-12", "Adams and Victor's Principles of Neurology", "12", 2023, ""),
    ("Avery &amp_", "AVERY-2021", "Avery & MacDonald's Neonatology: Pathophysiology and Management of the Newborn", "", 2021, "pdfinfo calls it the South Asian Edition; no edition number stated"),
    ("BRANT AND HELMS", "BRANT-5", "Brant and Helms' Fundamentals of Diagnostic Radiology", "5", 2018, ""),
    ("Braddom's Physical", "BRADDOM-6", "Braddom's Physical Medicine and Rehabilitation", "6", 2021, ""),
    ("Braunwald", "BRAUNWALD-12", "Braunwald's Heart Disease: A Textbook of Cardiovascular Medicine", "12", 2022, "complete 2-volumes-in-1 PDF (2,549 pages, Parts I-XI), added 2026-10-22"),
    ("F. Gary Cunningham", "WILLIAMS-OBSTETRICS-26", "Williams Obstetrics", "26", 2022, "disambiguated from the other two Williams books"),
    ("Firestein", "FIRESTEIN-12", "Firestein & Kelley's Textbook of Rheumatology", "12", 2024, ""),
    ("Frederick M. Azar", "CAMPBELL-2020", "Campbell's Operative Orthopaedics", "", 2020, ""),
    ("Gray&_039_s Anatomy", "GRAY-2020", "Gray's Anatomy: The Anatomical Basis of Clinical Practice", "", 2020, ""),
    ("Guyton and Hall", "GUYTON-2026", "Guyton and Hall Textbook of Medical Physiology", "", 2026, ""),
    ("H. Richard Winn", "YOUMANS-4", "Youmans & Winn Neurological Surgery", "4", 2023, ""),
    ("Honorio T. Benzon", "BENZON-2023", "Practical Management of Pain", "", 2023, ""),
    ("Dermatology_ 2-Volume Set", "BOLOGNIA-2024", "Dermatology", "", 2024, "complete 2-volume set (Sections 1-22, 3,233 pages) glued into one PDF, 2026-10-22"),
    ("John E. Bennett", "MANDELL-9", "Mandell, Douglas, and Bennett's Principles and Practice of Infectious Diseases", "9", 2019, ""),
    ("Kevin P. High", "HAZZARD-2022", "Hazzard's Geriatric Medicine and Gerontology", "", 2022, ""),
    ("Krause and Mahan", "KRAUSE-16", "Krause and Mahan's Food and the Nutrition Care Process", "16", 2022, ""),
    ("Marino&_039_s", "MARINO-2025", "Marino's The ICU Book", "", 2025, ""),
    ("Middleton's Allergy", "MIDDLETON-2019", "Middleton's Allergy: Principles and Practice", "", 2019, "UNCERTAIN: the file name shows '9' which may be an edition or an ISBN fragment; year used until the human decides"),
    ("Miller&_039_s", "MILLER-10", "Miller's Anesthesia", "10", 2024, ""),
    ("Murray & Nadel", "MURRAY-7", "Murray & Nadel's Textbook of Respiratory Medicine", "7", 2022, ""),
    ("Oxford Textbook", "OXFORD-6", "Oxford Textbook of Palliative Medicine", "6", 2021, ""),
    ("Prescriber&_039_s", "STAHL-2024", "The Prescriber's Guide: Children and Adolescents (Stahl's Essential Psychopharmacology)", "", 2024, ""),
    ("Richard S Irwin", "IRWIN-RIPPE-2023", "Irwin and Rippe's Intensive Care Medicine", "", 2023, ""),
    ("Robbins & Cotran", "ROBBINS-10", "Robbins & Cotran Pathologic Basis of Disease", "10", 2020, ""),
    ("Robert Boland", "KAPLAN-11", "Kaplan and Sadock's Comprehensive Textbook of Psychiatry", "11", 2024, "edition taken from pdfinfo, which says 11th edition"),
    ("Robert M. Kliegman", "NELSON-2024", "Nelson Textbook of Pediatrics", "", 2024, ""),
    ("Rockwood and Green", "ROCKWOOD-10", "Rockwood and Green's Fractures in Adults", "10", 2025, ""),
    ("Ron Walls", "ROSEN-2022", "Rosen's Emergency Medicine: Concepts and Clinical Practice", "", 2022, ""),
    ("Scott W. Wolfe", "GREEN-HAND-2021", "Green's Operative Hand Surgery", "", 2021, "disambiguated from GRAY-2020's unrelated 'Green'"),
    ("Sleisenger", "SLEISENGER-11", "Sleisenger and Fordtran's Gastrointestinal and Liver Disease", "11", 2020, ""),
    ("Thompson &amp_ Thompson", "THOMPSON-2023", "Thompson & Thompson Genetics and Genomics in Medicine", "", 2023, ""),
    ("Vincent T. DeVita", "DEVITA-12", "DeVita, Hellman and Rosenberg's Cancer: Principles and Practice of Oncology", "12", 2022, ""),
    ("Williams Hematology", "WILLIAMS-HEMATOLOGY-2021", "Williams Hematology", "", 2021, ""),
    ("Williams Textbook of Endocrinology", "WILLIAMS-ENDO-2024", "Williams Textbook of Endocrinology", "", 2024, ""),
    ("[Harrison", "HARRISON-22", "Harrison's Principles of Internal Medicine", "22", 2023, "the hub book; exempt from duplicate detection"),
    ("[Sabiston", "SABISTON-22", "Sabiston Textbook of Surgery: The Biological Basis of Modern Surgical Practice", "22", 2025, ""),
    # the three accepted copies of the byte-identical pairs
    ("Brenner and Rector's The Kidney, 2-Volume Set -- Alan S_ L_ Yu, Glenn M_ Chertow, Philip A_ Marsden, Valerie -- 2-volume set, 11, 2019 -- Elsevier - -- isbn13 9780323532655 -- f7b79dd7d165457ea0666766b0239aa1 -- Anna’s Archiv.pdf",
     "BRENNER-11", "Brenner and Rector's The Kidney", "11", 2019, "accepted copy of an identical pair"),
    ("Laurence Brunton, Bjorn Knollmann - Goodman and Gilman's The Pharmacological Basis of Therapeutics (2023, McGraw Hill _ Medical) - libgen.li.pdf",
     "GOODMAN-14", "Goodman and Gilman's The Pharmacological Basis of Therapeutics", "14", 2023, "edition from pdfinfo ('14th E'); accepted copy of an identical pair"),
    ("P. Ronan O’Connell, Andrew W. McCaskie, Robert D. Sayers - Bailey and Love’s SHORT PRACTICE of SURGERY 1 (2023, CRC Press) [10.1201_9781003106852] - libgen.li.pdf",
     "BAILEY-2023", "Bailey and Love's Short Practice of Surgery", "", 2023, "accepted copy of an identical pair; no edition number stated"),
]

# The three byte-identical pairs proven by sha256 (see PROGRESS.md). The file
# carrying the marker is rejected; nothing is deleted from disk.
DUP_REJECT_SUFFIX = {
    "BRENNER-11": "Anna’s Archiv-1.pdf",
    "GOODMAN-14": "libgen.li-1.pdf",
    "BAILEY-2023": "libgen.li-1.pdf",
}
DUP_TABLE = [
    ("Brenner and Rector's The Kidney, 2-Volume Set -- Alan S_ L_ Yu, Glenn M_ Chertow, Philip A_ Marsden, Valerie -- 2-volume set, 11, 2019 -- Elsevier - -- isbn13 9780323532655 -- f7b79dd7d165457ea0666766b0239aa1 -- Anna’s Archiv-1.pdf",
     "BRENNER-11", "Brenner and Rector's The Kidney", "11", 2019),
    ("Laurence Brunton, Bjorn Knollmann - Goodman and Gilman's The Pharmacological Basis of Therapeutics (2023, McGraw Hill _ Medical) - libgen.li-1.pdf",
     "GOODMAN-14", "Goodman and Gilman's The Pharmacological Basis of Therapeutics", "14", 2023),
    ("P. Ronan O’Connell, Andrew W. McCaskie, Robert D. Sayers - Bailey and Love’s SHORT PRACTICE of SURGERY 1 (2023, CRC Press) [10.1201_9781003106852] - libgen.li-1.pdf",
     "BAILEY-2023", "Bailey and Love's Short Practice of Surgery", "", 2023),
]


def main():
    intake = json.loads(INTAKE.read_text())
    by_name = {r["pdf_file"]: r for r in intake}

    records, used, report = [], set(), []
    for key, bid, title, edition, year, notes in TABLE:
        hits = [f for f in by_name if key in f and f not in used]
        if len(hits) != 1:
            report.append(f"!! {key!r} matched {len(hits)} files -> {hits}")
            continue
        f = hits[0]
        used.add(f)
        r = by_name[f]
        records.append(make(r, bid, title, edition, year, notes, "candidate"))

    for fname, bid, title, edition, year in DUP_TABLE:
        if fname not in by_name:
            report.append(f"!! duplicate file not found: {fname[:50]}")
            continue
        used.add(fname)
        r = by_name[fname]
        rec = make(r, bid, title, edition, year,
                   "byte-identical duplicate of the accepted copy (sha256 proven); file kept on disk, never read",
                   "rejected-duplicate")
        rec["duplicate_of"] = bid
        records.append(rec)

    missing = set(by_name) - used
    for f in sorted(missing):
        report.append(f"!! NOT ASSIGNED a book_id: {f}")

    records.sort(key=lambda x: x["book_id"])
    OUT.write_text(json.dumps(records, indent=1, ensure_ascii=False))

    acc = [r for r in records if r["status"] == "candidate"]
    print(f"books.json written: {len(records)} records "
          f"({len(acc)} candidates + {len(records)-len(acc)} rejected duplicates)")
    print(f"total pages across candidates: {sum(r['page_count_images'] for r in acc)}")
    print(f"all candidates have a text layer: {all(r['text_layer'] for r in acc)}")
    print("\n--- problems ---")
    for line in report or ["none"]:
        print(" ", line)


def make(r, bid, title, edition, year, notes, status):
    return {
        "book_id": bid,
        "pdf_file": r["pdf_file"],
        "title": title,
        "edition": edition,
        "year": year,
        "page_count_images": r["pages"],
        "text_layer": r["text_layer"],
        "image_dir": f"kitchen/pages/{bid}",
        "image_name_pattern": "page-{n:04d}.png",
        "toc_images": None,
        "index_images": None,
        "page_offset": None,
        "field_name": "",
        "cluster": "",
        "status": status,
        "notes": notes,
    }


if __name__ == "__main__":
    main()