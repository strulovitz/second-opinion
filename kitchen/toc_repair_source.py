"""Choose accepted TOC evidence without requiring a constant PDF offset."""

import copy
import re
import subprocess
from collections import Counter

from eyes_folio import toc_from_evidence
from page_offset import flatten, key, positive_integer, require
from toc_ranges import fill_ranges
from toc_reexport import repair_images


def accepted_source(book, source, old, eyes, image_dir):
    """Eyes when present; otherwise the previously accepted vis-toc itself.

    A legacy -toc can be stale/empty. Without eyes, the accepted -vis-toc
    is authoritative, not the old export. Never change its chapter starts.
    """
    image_changes, issues = [], []
    updated = copy.deepcopy(eyes)
    if eyes is not None:
        rows = eyes["chapters"]
        require(eyes["_summary"]["book"] == book["book_id"], "wrong evidence book")
        require(eyes["_summary"]["unresolved"] == 0, "unresolved eyes")
        toc = toc_from_evidence(source, rows, require_complete=True)
        kinds = {r.get("kind") for r in rows}
        require(kinds in ({"printed"}, {"pdf-page"}), "mixed/unknown citation units")
        unit = next(iter(kinds))
        require(flat_identity(old) == flat_identity(toc), "existing export disagrees with accepted eyes")
        for row in updated["chapters"]:
            pdf, page = row.get("pdf_page"), row.get("printed")
            require(positive_integer(pdf) and pdf <= book["page_count_images"], "invalid saved PDF page")
            require(unit != "pdf-page" or pdf == page, "mixed PDF/printed page values")
            try:
                image_changes.extend(repair_images({"chapters": [row]}, image_dir))
                require((image_dir / row["image_file"]).is_file(), "selected picture missing")
            except (ValueError, KeyError, TypeError, OSError) as exc:
                issues.append(f"ch{row.get('number')}: image evidence: {exc}")
        offsets = Counter(r["pdf_page"] - r["printed"] for r in rows)
        mapping = {"source": "saved-eyes", "unit": unit,
                   "offset_values": len(offsets),
                   "uniform_offset": next(iter(offsets)) if len(offsets) == 1 else None}
    else:
        toc = {"provinces": []}
        kinds = set()
        for province in source.get("provinces", []):
            out = {k: copy.deepcopy(v) for k, v in province.items()
                   if k not in ("chapters", "page_start", "page_end")}
            out.setdefault("part_name", province["name"])
            out["chapters"] = []
            for ch in province.get("chapters", []):
                kind = "pdf-page" if ch.get("_page_source") in (
                    "pdf-link", "pdf-outline", "text-top") or (
                    ch.get("_page_source") == "text-contents" and
                    ch.get("_printed_folio") not in (None, ch.get("page_start"))) else "printed"
                kinds.add(kind)
                row = {k: copy.deepcopy(ch.get(k)) for k in ("number", "title", "page_start")}
                if kind == "pdf-page":
                    row["pdf_page"] = ch["page_start"]
                out["chapters"].append(row)
            toc["provinces"].append(out)
        require(len(kinds) == 1, "empty source or mixed/unknown citation units")
        unit = next(iter(kinds))
        mapping = {"source": "accepted-vis-toc", "unit": unit, "offset_values": 0,
                   "uniform_offset": 0 if unit == "pdf-page" else book.get("page_offset")}
        fill_ranges(toc)
    identities = [key(p, c) for p, c in flatten(toc)]
    require(len(set(identities)) == len(identities), "duplicate source chapter identities")
    if mapping["unit"] == "pdf-page":
        require(all(c["page_start"] <= book["page_count_images"] for _, c in flatten(toc)),
                "PDF citation exceeds book length")
    return toc, updated, mapping, image_changes, issues


def flat_identity(toc):
    return [(p, c.get("number"), c.get("title"), c.get("page_start"), c.get("pdf_page"))
            for p, c in flatten(toc)]


def final_boundary(book, toc, old, mapping, pdf, check_index=False):
    """Unknown/unproved final ends use the BIBLE fallback, not a book failure.

    Internal ends need no PDF mapping. Optional index checks use at most
    THREE individual PDF pages, serially, with a bounded timeout.
    """
    last = flatten(toc)[-1][1]
    fallback = {"mode": "median-fallback", "note": "index boundary not verified"}
    index = book.get("index_images")
    if not (isinstance(index, list) and len(index) == 2
            and all(positive_integer(p) for p in index)
            and 1 < index[0] <= index[1] <= book["page_count_images"]):
        return None, fallback | {"note": "index absent/invalid; BIBLE median fallback"}
    start = index[0]
    if positive_integer(last.get("pdf_page")) and start <= last["pdf_page"]:
        return None, fallback | {"note": "configured index is before the final opener; fallback, locator needs review"}
    offset = mapping["uniform_offset"]
    old_rows = flatten(old)
    if not check_index:
        # Preserve a previously computed exact index end (Harrison pilot).
        # Do not promote it to a newly checked boundary in the report.
        if offset is not None and old_rows and flat_identity(old) == flat_identity(toc):
            end = start - offset - 1
            if old_rows[-1][1].get("page_end") == end and end >= last["page_start"]:
                return end, {"mode": "saved-index-boundary", "note": "existing matching index-derived end preserved; not rechecked"}
        return None, fallback
    try:
        def lines(page):
            result = subprocess.run(
                ["pdftotext", "-layout", "-f", str(page), "-l", str(page), str(pdf), "-"],
                capture_output=True, text=True, check=True, timeout=20)
            return [s.strip() for s in result.stdout.splitlines() if s.strip()]

        def is_index(text):
            return any(re.fullmatch(r"(?:Subject\s+)?Index", s, re.I) for s in text[:6])

        opener, previous = lines(start), lines(start - 1)
        require(is_index(opener) and not is_index(previous), "configured index opener not confirmed")
        if mapping["unit"] == "pdf-page" or offset is not None:
            end = start - (offset or 0) - 1
            require(end >= last["page_start"], "computed boundary precedes last chapter")
            return end, {"mode": "verified-index", "note": f"index PDF {start}; citation end {end}"}
        # Variable offsets do not prevent reading two actual adjacent tail
        # folios. Require a unique consecutive pair; never extrapolate the
        # last chapter's offset through intervening e-pages/inserts.
        def folios(text):
            return {int(s) for s in text[:3] + text[-3:] if s.isdigit()
                    and int(s) >= last["page_start"] and s != str(last.get("number"))}

        before = folios(lines(start - 2)) if start > 2 else set()
        candidates = {n for n in folios(previous) if n - 1 in before}
        require(len(candidates) == 1, "printed tail folios not uniquely confirmed")
        end = candidates.pop()
        return end, {"mode": "verified-tail-folios", "note": f"two adjacent tail folios; citation end {end}"}
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        return None, fallback | {"note": f"index check: {exc}; BIBLE median fallback"}
