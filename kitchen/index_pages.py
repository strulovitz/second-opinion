"""Pure page-reference conversion, source grounding and district mapping."""

import copy
import json
import re
from collections import Counter

from index_common import fingerprint, require


def expand_reference(raw):
    raw = re.sub(r"\s+", "", raw)
    if re.match(r"^[A-Za-z]", raw):
        return [], "online-only"
    match = re.fullmatch(r"(\d+)[tfb]?(?:[-–—](\d+)[tfb]?)?", raw)
    if not match:
        return [], "non-integer-or-malformed"
    start = int(match[1])
    require(start > 0, "page reference must be positive")
    if match[2] is None:
        return [start], None
    end = int(match[2])
    if len(match[2]) < len(match[1]):
        scale = 10 ** len(match[2])
        end += start // scale * scale
        if end < start:
            end += scale
    require(end >= start, "decreasing page-reference range")
    return (list(range(start, end + 1)) if end - start + 1 <= 30 else [start, end]), None


def literal_pattern(text):
    pattern = r"\s+".join(re.escape(w) for w in text.split())
    # A printed label may wrap after any of these marks; the words still match
    # the same source, so allow the layout break without changing the quote.
    for mark in ('-', '–', '—', '/'):
        pattern = pattern.replace(re.escape(mark), re.escape(mark) + r"\s*")
    return pattern


REF_TOKEN = r"[A-Za-z]?\d+(?:\.\d+)?[A-Za-z]?(?:[-–—]\d+[A-Za-z]?)?"
REF_ITEM = re.compile(REF_TOKEN + r"$")
SEE_TAIL = re.compile(r"\s+See\b.*$")
CLOSING = "”’\"')]}>"


def source_references(text):
    """Literal reference runs at line tails, not numbers inside term labels.

    A headword may itself end with punctuation inside closing quotes or
    brackets (``“Alpha coma,” 191``), so the tail is parsed from the right and
    stops at the first comma-separated item that is not a page reference.
    """
    # A printed range may wrap after any of the three dash forms. Join that
    # layout break for counting only; retain the source text and quote intact.
    text = re.sub(r"(?<=[0-9tfb])([-–—])\s*\n\s*(?=\d)", r"\1", text)
    refs = Counter()
    previous = ""
    for raw in text.splitlines():
        line = SEE_TAIL.sub("", raw.strip()).rstrip(" .,")
        items = line.split(",")
        tail = []
        for item in reversed(items):
            token = item.strip().lstrip(CLOSING).strip()
            if not REF_ITEM.fullmatch(token):
                break
            tail.append(token)
        tail.reverse()
        if not previous.endswith(",") and len(tail) == len(items) > 1:
            # A line that does not continue a wrapped reference run starts with
            # its label, so "C3, 2359" is an entry named C3, not a page number.
            tail = tail[1:]
        refs.update(tail)
        previous = raw.strip()
    return refs


def is_reference_line(line, before=""):
    """True when the whole line is a reference run rather than a labelled entry."""
    items = [item.strip().lstrip(CLOSING).strip()
             for item in SEE_TAIL.sub("", line.strip()).rstrip(" .,").split(",")]
    if not all(REF_ITEM.fullmatch(item) for item in items):
        return False
    return before.rstrip().endswith(",") or len(items) == 1


def wrapped_label_references(text):
    """Reference-shaped lines that are actually a wrapped label prefix.

    Layout extraction can leave a superscript such as ``99m`` alone on a line,
    with the rest of its label indented underneath. Such a line is not a
    wrapped reference continuation (the previous line does not end in a comma),
    so it is label text and must not be required as a page reference.
    """
    lines = text.splitlines()
    ignored = Counter()
    for i, line in enumerate(lines):
        token = line.strip()
        if not REF_ITEM.fullmatch(token):
            continue
        previous = next((row for row in reversed(lines[:i]) if row.strip()), "")
        if previous.rstrip().endswith(","):
            continue
        following = next((row for row in lines[i + 1:] if row.strip()), "")
        if not following:
            continue
        if len(following) - len(following.lstrip()) <= len(line) - len(line.lstrip()):
            continue
        following = SEE_TAIL.sub("", following.strip()).rstrip(" .,")
        if all(REF_ITEM.fullmatch(item.strip().lstrip(CLOSING).strip())
               for item in following.split(",")):
            continue
        ignored[token] += 1
    return ignored


SEE_SUBENTRY = re.compile(r"^(?P<label>.+?)[.,]?\s+See\s+(?P<target>.+)$", re.I)


def canonical_subentry(text, block):
    """Enforce the prompt's rule: a subentry label never carries a See tail.

    The printed line puts page references between the label and a final
    ``See also ...``. The reader sometimes appends that tail anyway; keep the
    label the prompt asks for, but only after proving both parts are verbatim
    source text.
    """
    parts = SEE_SUBENTRY.fullmatch(text.strip())
    if not parts or re.search(literal_pattern(text), block):
        return text
    if (re.search(literal_pattern(parts.group("label")), block)
            and re.search(literal_pattern(parts.group("target")), block)):
        return parts.group("label")
    return text


def subentry_hint(text, block):
    """Explain the one layout shape whose See tail is not part of the label."""
    parts = re.fullmatch(r"(.+?)[.,]?\s+See\s+(.+)", text.strip(), re.I)
    if parts and re.search(literal_pattern(parts.group(1)), block):
        return ("; page references sit between this label and a 'See also' target, "
                "so keep only the label as this subentry's text")
    return ""


TEXT_WITH_REFERENCES = re.compile(
    r"^(.+),\s*(" + REF_TOKEN + r"(?:\s*,\s*" + REF_TOKEN + r")*)$")


def split_text_references(text, pages, block):
    """Move a page-reference tail the reader left in a label into pages.

    Only when pages is empty, the tail is entirely page references, and the
    remaining label is itself verbatim source text.
    """
    if pages:
        return text, pages
    parts = TEXT_WITH_REFERENCES.fullmatch(text.strip())
    if not parts or not re.search(literal_pattern(parts.group(1).strip()), block):
        return text, pages
    return parts.group(1).strip(), [ref.strip() for ref in parts.group(2).split(",")]


def split_references(refs, block=""):
    """Split a page-reference string the reader packed with commas.

    Only splits when every comma-separated part is itself a valid page
    reference, so no label can be pulled into the list. A See tail the reader
    appended is dropped, but only when that target is verbatim source text.
    """
    result = []
    for ref in refs:
        text = str(ref).strip()
        see = re.split(r"[.;,]?\s+See\s+", text, maxsplit=1, flags=re.I)
        if len(see) == 2:
            if not re.search(literal_pattern(see[1]), block):
                result.append(ref)
                continue
            text = see[0].strip().rstrip(".;,")
        if text.endswith("."):
            text = text[:-1].rstrip()
        parts = [part.strip() for part in text.split(",")]
        if len(parts) > 1 and all(REF_ITEM.fullmatch(part) for part in parts):
            result.extend(parts)
        elif REF_ITEM.fullmatch(text):
            result.append(text)
        else:
            result.append(ref)
    return result


def ground_entries(answer, text, page, image):
    entries = answer["entries"]
    require(isinstance(entries, list), "entries must be a list")
    starts, cursor = [], 0
    for i, row in enumerate(entries):
        require(isinstance(row["headword"], str) and row["headword"].strip(), "missing headword")
        require(isinstance(row["display"], str) and row["display"].strip(), "missing display")
        require(row.get("see") is None or isinstance(row["see"], str), "invalid See target")
        require(isinstance(row["pages"], list) and isinstance(row["subentries"], list), "invalid index entry arrays")
        if row["headword"] == "CONTINUED":
            require(i == 0, "CONTINUED must be the first entry")
            starts.append(0)
            continue
        pattern = (r"(?m)^[^\S\r\n]*(" + literal_pattern(row["headword"])
                   + r")(?=$|[\s,.;:])")
        match = re.search(pattern, text[cursor:])
        require(match is not None, f"headword absent from source: {row['headword']}")
        starts.append(cursor + match.start(1))
        cursor += match.end(1)
    result = []
    for i, row in enumerate(entries):
        block = text[starts[i]:starts[i + 1] if i + 1 < len(starts) else len(text)].strip()
        row = copy.deepcopy(row)
        row["pages"] = split_references(row["pages"], block)
        for sub in row["subentries"]:
            require(isinstance(sub, dict) and set(sub) == {"text", "pages"},
                    f"subentry must have only text and pages; nested/unexpected fields "
                    f"would lose references (PDF {page}, headword={row['headword']!r})")
            if isinstance(sub["text"], str):
                sub["text"] = canonical_subentry(sub["text"], block)
            require(isinstance(sub["text"], str) and sub["text"].strip()
                    and re.search(literal_pattern(sub["text"]), block),
                    f"subentry absent from its source block (PDF {page}, "
                    f"headword={row['headword']!r}, subentry={sub['text']!r})"
                    + subentry_hint(sub["text"] if isinstance(sub["text"], str) else "", block))
            require(isinstance(sub["pages"], list), "invalid subentry refs")
            sub["pages"] = split_references(sub["pages"], block)
            sub["text"], sub["pages"] = split_text_references(sub["text"], sub["pages"], block)
        for refs in [row["pages"], *(s["pages"] for s in row["subentries"])]:
            for ref in refs:
                require(isinstance(ref, str) and ref.strip(), "references must be nonempty strings")
                require(REF_ITEM.fullmatch(ref.strip()),
                        f"not a page reference: {ref!r} (PDF {page}, headword={row['headword']!r}); "
                        "put each printed page reference in its own pages item, and put a See "
                        "target in the entry or subentry text")
                require(re.search(r"(?<![\w])" + literal_pattern(ref) + r"(?![\w])", block), f"reference absent from source: {ref}")
        if row.get("see"):
            if re.match(r"^also\b", row["see"], re.I):
                row["see"] = None
            else:
                require(re.search(literal_pattern(row["see"]), block), "See target absent from source")
        row.update(source_index_pdf=page, image_file=image, quote=block)
        result.append(row)
    # A source-present subset is not a complete page. Check the whole page,
    # including an accidentally omitted first/last main entry.
    expected = source_references(text)
    for token, count in wrapped_label_references(text).items():
        expected[token] -= count
    expected = Counter({token: count for token, count in expected.items() if count > 0})
    actual = Counter(ref for row in result for refs in [row["pages"], *(s["pages"] for s in row["subentries"])] for ref in refs)
    missing, extra = expected - actual, actual - expected
    require(not missing and not extra,
            f"index references incomplete (PDF {page}): missing={missing.total()}, extra={extra.total()}; "
            f"missing sample={list(missing.items())[:8]}; extra sample={list(extra.items())[:8]}; "
            "copy every main/subentry reference, without duplicating entries")
    return result


def citation_unit(ctx):
    eyes = ctx.path("eyes.json")
    if eyes.exists():
        data = json.loads(eyes.read_text())
        kinds = {r.get("kind") for r in data.get("chapters", [])}
        require(len(kinds) == 1 and kinds <= {"printed", "pdf-page"}, "mixed/unknown saved citation units")
        return next(iter(kinds))
    source = json.loads(ctx.path("vis-toc.json").read_text())
    kinds = set()
    for province in source["provinces"]:
        for chapter in province["chapters"]:
            pdf = chapter.get("_page_source") in ("pdf-link", "pdf-outline", "text-top") or (
                chapter.get("_page_source") == "text-contents" and chapter.get("_printed_folio") not in (None, chapter.get("page_start")))
            kinds.add("pdf-page" if pdf else "printed")
    require(len(kinds) == 1, "mixed/unknown district citation units")
    return next(iter(kinds))


def map_page(printed, ctx, unit):
    if unit == "printed":
        targets = [printed]
    elif type(ctx.book.get("page_offset")) is int:
        targets = [printed + ctx.book["page_offset"]]
    elif ctx.book.get("page_offsets"):
        ranges = sorted(ctx.book["page_offsets"], key=lambda r: r["from_image"])
        require(all(type(r["offset"]) is int and type(r["from_image"]) is int for r in ranges), "invalid configured range mapping")
        targets = [printed + row["offset"] for i, row in enumerate(ranges)
                   if row["from_image"] <= printed + row["offset"] < (ranges[i + 1]["from_image"] if i + 1 < len(ranges) else ctx.book["page_count_images"] + 1)]
    else:
        return [], "mapping-unresolved"
    return [d["territory_id"] for d in ctx.districts for target in targets
            if d["page_start"] <= target <= d["page_end"]], None


def assemble(pages, ctx, unit):
    entries, counts = [], {"online-only": 0, "non-integer-or-malformed": 0, "outside-districts": 0, "mapping-unresolved": 0}
    for parsed in pages:
        for row in parsed:
            if row["headword"] == "CONTINUED":
                require(entries and not entries[-1].get("see"), "orphan CONTINUED entry; preceding page is required")
                entry = entries[-1]
            else:
                entry = {k: row[k] for k in ("headword", "display", "see")}
                entry.update(id=fingerprint([ctx.bid, row["source_index_pdf"], len(entries), row["headword"]]),
                             subentries=[], references=[], sources=[])
                entries.append(entry)
            entry["sources"].append({k: row[k] for k in ("source_index_pdf", "image_file", "quote")})
            entry["subentries"].extend(row["subentries"])
            groups = [(None, row["pages"])] + [(s["text"], s["pages"]) for s in row["subentries"]]
            for subentry, refs in groups:
                for raw in refs:
                    numbers, reason = expand_reference(raw)
                    if reason:
                        counts[reason] += 1
                    for printed in numbers:
                        dids, issue = map_page(printed, ctx, unit)
                        if issue:
                            counts[issue] += 1
                        elif not dids:
                            counts["outside-districts"] += 1
                        entry["references"].append({"raw": raw, "printed_page": printed, "district_ids": sorted(set(dids)),
                                                   "issue": issue, "subentry": subentry,
                                                   **{k: row[k] for k in ("source_index_pdf", "image_file", "quote")}})
    return entries, counts
