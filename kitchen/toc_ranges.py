"""Pure chapter-range arithmetic; no PDF mapping, model or database needed."""

import statistics


def fill_ranges(toc, final_end=None):
    """Mutate only chapter/province bounds, preserving accepted starts/order.

    BIBLE 3.4.4 plus AMENDMENT 3.4. A missing verified final boundary uses
    the book-wide median of positive successive-start differences.
    """
    provinces = toc.get("provinces", [])
    chapters = [c for p in provinces for c in p.get("chapters", [])]
    if not chapters:
        raise ValueError("no confirmed chapters")
    if any(type(c.get("page_start")) is not int or c["page_start"] < 1 for c in chapters):
        raise ValueError("invalid page_start")
    lengths = []
    for cur, nxt in zip(chapters, chapters[1:]):
        length = nxt["page_start"] - cur["page_start"]
        if length < 0:
            raise ValueError(f"page_start decreases at ch{nxt.get('number')}")
        if length > 0:
            lengths.append(length)
        cur["page_end"] = max(cur["page_start"], nxt["page_start"] - 1)
    if final_end is None:
        if not lengths:
            raise ValueError("no positive chapter lengths for median fallback")
        final_end = chapters[-1]["page_start"] + int(statistics.median(lengths))
    if type(final_end) is not int or final_end < chapters[-1]["page_start"]:
        raise ValueError("index boundary precedes the final chapter")
    chapters[-1]["page_end"] = final_end
    for province in provinces:
        kids = province.get("chapters", [])
        if not kids:
            continue  # keep a pre-existing empty heading untouched
        province["page_start"] = min(c["page_start"] for c in kids)
        province["page_end"] = max(c["page_end"] for c in kids)
    return toc
