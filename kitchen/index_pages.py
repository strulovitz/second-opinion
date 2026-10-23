"""Pure page-reference conversion, source grounding and district mapping."""

import copy
import json
import re

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
    return r"\s+".join(re.escape(w) for w in text.split())


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
        match = re.search(literal_pattern(row["headword"]), text[cursor:])
        require(match is not None, f"headword absent from source: {row['headword']}")
        starts.append(cursor + match.start())
        cursor += match.end()
    result = []
    for i, row in enumerate(entries):
        block = text[starts[i]:starts[i + 1] if i + 1 < len(starts) else len(text)].strip()
        row = copy.deepcopy(row)
        for sub in row["subentries"]:
            require(isinstance(sub["text"], str) and sub["text"].strip()
                    and re.search(literal_pattern(sub["text"]), block), "subentry absent from its source block")
            require(isinstance(sub["pages"], list), "invalid subentry refs")
        for refs in [row["pages"], *(s["pages"] for s in row["subentries"])]:
            for ref in refs:
                require(isinstance(ref, str) and ref.strip(), "references must be nonempty strings")
                require(re.search(r"(?<![\w])" + literal_pattern(ref) + r"(?![\w])", block), f"reference absent from source: {ref}")
        if row.get("see"):
            if re.match(r"^also\b", row["see"], re.I):
                row["see"] = None
            else:
                require(re.search(literal_pattern(row["see"]), block), "See target absent from source")
        row.update(source_index_pdf=page, image_file=image, quote=block)
        result.append(row)
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
