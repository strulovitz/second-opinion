"""Selected-page PDF evidence shared by TOC correction and A3 mapping.

No model calls, whole-document text extraction or page-label assumptions.
Text and proofs stay in gitignored logs. A session opens its PDF only once.
"""

import hashlib
import json
import re
from pathlib import Path

from pypdf import PdfReader

from page_offset import folded, positive_integer, require
from toc_reexport import atomic_write

VERSION = 1
NUMBER = r"\d+(?:\.\d+)*[A-Za-z]?"
CHAPTER = re.compile(rf"^(?:chapter\s+)?({NUMBER})(?:\s*[:.\-–—]\s*|\s+)(\S.*)$", re.I)
BANNER = re.compile(r"^(?:part|section|volume|vol\.?|unit|book|module|division)\b", re.I)
EXCLUDED = re.compile(r"\b(?:list of techniques|chapter outline|contents|index|contributors|"
                      r"preface|online[ -]only|videos?|supplement)\b", re.I)


def fingerprint(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def pdf_identity(path):
    """Local file identity, not a claim to have hashed/read the entire PDF."""
    path = Path(path).resolve()
    stat = path.stat()
    return {"path": str(path), "size": stat.st_size, "mtime_ns": stat.st_mtime_ns,
            "ctime_ns": stat.st_ctime_ns, "inode": stat.st_ino, "device": stat.st_dev}


def opener_matches(text, number, title):
    """Full title and bounded number together, including drop-cap C / HAPTER.

    A repeated short title prefix, a chapter number alone, a contents line
    or a body reference to another chapter is not opener proof.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if any(re.fullmatch(r"(?:table of )?contents|(?:subject )?index", folded(s))
           for s in lines[:6]):
        return False
    # Only a heading-sized prefix, not every mention in the body.
    head = "\n".join(lines[:35])[:3500]
    head = re.sub(r"c\s*h\s*a\s*p\s*t\s*e\s*r", "CHAPTER", head, flags=re.I)
    wanted = folded(title)
    num = re.escape(str(number))
    # Keep dots in chapter numbers significant (4.2 must not match 42).
    marker = re.compile(rf"(?<![\w.])(?:chapter\s+)?{num}(?![\w.]|\s*\.\s*\d)", re.I)
    for match in marker.finditer(head):
        before = head[:match.start()].splitlines()[-1:] or [""]
        if before[0].strip():
            continue
        tail = folded(head[match.end():match.end() + len(title) * 3 + 150])
        if wanted and (tail == wanted or tail.startswith(wanted + " ")):
            return True
    return False


def corner_folios(text, number=None):
    lines = [s.strip() for s in text.splitlines() if s.strip()]
    # Do not mistake an opener's bare chapter number for a printed folio.
    return {int(s) for s in lines[:3] + lines[-3:]
            if s.isdigit() and int(s) > 0 and s != str(number)}


def heading_names_chapter(heading, number, title):
    heading = re.sub(r"c\s*h\s*a\s*p\s*t\s*e\s*r", "CHAPTER", heading or "", flags=re.I)
    return bool(folded(title) and (" " + folded(title) + " ") in (" " + folded(heading) + " ")
                and re.search(rf"(?<![\w.]){re.escape(str(number))}(?![\w.])", heading))


class PdfEvidence:
    def __init__(self, pdf, cache=None, evidence=None):
        self.pdf = Path(pdf)
        self.identity = pdf_identity(pdf)
        self.cache = Path(cache) if cache else None
        self.key = {"version": VERSION, "pdf": self.identity, "evidence": fingerprint(evidence)}
        self.pages = {}
        self.reader = None
        self.hits = self.extracted = 0
        if self.cache and self.cache.exists():
            try:
                saved = json.loads(self.cache.read_text())
                if saved.get("key") == self.key:
                    self.pages = saved["pages"]
            except (ValueError, KeyError):
                pass  # A truncated cache is never proof.

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        if self.reader is not None:
            self.reader.close()

    def open(self):
        if self.reader is None:
            self.reader = PdfReader(str(self.pdf))
        return self.reader

    def text(self, page):
        require(positive_integer(page), "invalid PDF page")
        if str(page) in self.pages:
            self.hits += 1
            return self.pages[str(page)]
        reader = self.open()
        require(page <= len(reader.pages), "PDF destination exceeds document length")
        text = reader.pages[page - 1].extract_text() or ""
        self.pages[str(page)] = text
        self.extracted += 1
        return text

    def save_cache(self):
        require(pdf_identity(self.pdf) == self.identity, "PDF changed during verification")
        if self.cache:
            self.cache.parent.mkdir(parents=True, exist_ok=True)
            atomic_write(self.cache, json.dumps({"key": self.key, "pages": self.pages}, ensure_ascii=False))


def bookmark_toc(entries, title):
    """Use true bookmark ancestry, never page-sorted 'last banner wins'.

    entries are toc_outline.walk() rows. Numbered descendants of a chapter
    are internal outlines, not additional chapters. Unusable entries are
    reported, not silently certified as a complete contents list.
    """
    stack, provinces, excluded, unresolved = [], [], [], []
    for index, entry in enumerate(entries):
        depth, label = entry["depth"], entry["title"].strip()
        while stack and stack[-1]["depth"] >= depth:
            stack.pop()
        ancestors = list(stack)
        match = CHAPTER.fullmatch(label)
        blocked = EXCLUDED.search(label) or any(a["excluded"] for a in ancestors)
        internal = any(a["chapter"] for a in ancestors)
        row = entry | {"chapter": bool(match), "excluded": bool(blocked), "index": index}
        stack.append(row)
        if not match:
            continue
        if blocked or internal:
            excluded.append({"title": label, "reason": "excluded listing" if blocked else "chapter-internal outline"})
            continue
        if not positive_integer(entry.get("image")):
            unresolved.append({"title": label, "reason": "no physical PDF destination"})
            continue
        parents = [a for a in ancestors if not a["chapter"]]
        home = parents[-1] if parents else None
        part = next((a for a in reversed(parents[:-1]) if BANNER.match(a["title"])), home)
        group = home["index"] if home else -1
        if not provinces or provinces[-1]["_bookmark_group"] != group:
            name = home["title"] if home else "ALL"
            provinces.append({"name": name, "part_name": part["title"] if part else title,
                              "_bookmark_group": group, "chapters": []})
        provinces[-1]["chapters"].append({
            "number": match[1], "title": match[2].strip(), "page_start": entry["image"],
            "pdf_page": entry["image"], "_page_source": "pdf-outline",
            "_outline_image": entry["image"]})
    for province in provinces:
        province.pop("_bookmark_group")
    require(provinces, "no chapter bookmarks; use the contents/free-reader path")
    return {"provinces": provinces}, {"kind": "pdf-chapter-bookmarks", "excluded": excluded,
                                      "unresolved": unresolved}


def verify_targets(session, toc, progress=None):
    proofs, unresolved = [], []
    for i, province in enumerate(toc["provinces"]):
        for chapter in province["chapters"]:
            page = chapter.get("pdf_page")
            identity = {"province": province["name"], "province_index": i,
                        "number": chapter.get("number"), "title": chapter["title"], "pdf_page": page}
            if not positive_integer(page):
                unresolved.append(identity | {"reason": "no checked PDF target"})
                continue
            text = session.text(page)
            if opener_matches(text, chapter.get("number"), chapter["title"]):
                proofs.append(identity | {"method": "page-text-number-and-full-title",
                                           "text_hash": hashlib.sha256(text.encode()).hexdigest()})
            else:
                unresolved.append(identity | {"reason": "opener text ambiguous; use the free reader"})
            count = len(proofs) + len(unresolved)
            if progress and (count == 1 or count % 25 == 0):
                progress(f"  targets checked: {count}; ambiguous: {len(unresolved)}")
    return proofs, unresolved
