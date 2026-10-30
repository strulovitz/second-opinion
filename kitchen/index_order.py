"""Derive physical column reading order without rewriting extraction evidence."""

import json
import re
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter

from index_common import fingerprint, require, save
from toc_evidence import pdf_identity

NS = {"x": "http://www.w3.org/1999/xhtml"}
FURNITURE = re.compile(r"(?:index|[IVXLCDM]+-\d+)", re.I)
FURNITURE_PREFIX = re.compile(r"^[IVXLCDM]+-\d+\s+", re.I)


def inventory(text):
    # Compare characters, not whitespace-separated words: Poppler's plain
    # output joins a word hyphenated across a line while bbox keeps the
    # physical hyphen, and bbox splits subscript/superscript runs ("B1," ->
    # "B 1 ,", "(Raw)," -> "(R aw ),") that plain text keeps joined. Those are
    # layout-only differences; a lost, duplicated or substituted character
    # still fails. Keep the physical spelling in the reader input and quote.
    text = re.sub(r"(?<=[A-Za-z])-\s*\n\s*(?=[A-Za-z])", "", text)
    text = "\n".join(FURNITURE_PREFIX.sub("", line) for line in text.splitlines()
                     if not FURNITURE.fullmatch(line.strip()))
    return Counter(char for char in text if not char.isspace())


def column_text(xml, original):
    """Order Poppler blocks by overlapping column bounds, then top to bottom.

    This moves literal words only; the free reader still interprets entries.
    Refuse an ambiguous spanning block rather than interleave its columns.
    """
    page = ET.fromstring(xml).find(".//x:page", NS)
    require(page is not None, "missing bbox page")
    blocks = []

    def line_text(line):
        """Keep a running index header out of the column margin.

        Poppler sometimes puts the page label (``I-102``) in the same line as
        the first body words. Its x would set the whole column's left edge and
        falsely indent every entry, so measure that line from the first real
        word. Only a leading Roman-numeral page label is removed; the text
        inventory removes the same prefix from the plain extraction.
        """
        words = line.findall("x:word", NS)
        texts = [word.text or "" for word in words]
        x = float(line.attrib["xMin"])
        if len(words) > 1 and FURNITURE_PREFIX.fullmatch(texts[0] + " "):
            x = float(words[1].attrib["xMin"])
            texts = texts[1:]
        return x, float(line.attrib["yMin"]), " ".join(texts)

    for block in page.findall(".//x:block", NS):
        lines = [line_text(line) for line in block.findall("x:line", NS)]
        label = " ".join(line[2] for line in lines)
        if not label.strip() or FURNITURE.fullmatch(label.strip()):
            continue
        blocks.append({k: float(block.attrib[k]) for k in ("xMin", "xMax", "yMin", "yMax")} | {"lines": lines})
    require(blocks, "no bbox text blocks")
    wide = [b for b in blocks if b["xMax"] - b["xMin"] > float(page.attrib["width"]) * .65]
    body = [b for b in blocks if b not in wide]
    if not body:
        body, wide = wide, []
    top, bottom = min(b["yMin"] for b in body), max(b["yMax"] for b in body)
    require(all(b["yMax"] <= top or b["yMin"] >= bottom for b in wide),
            "ambiguous spanning bbox block; inspect column evidence")
    def body_left(block):
        return min(line[0] for line in block["lines"])

    columns = []
    for block in sorted(body, key=lambda b: (body_left(b), b["yMin"])):
        left = body_left(block)
        matches = [c for c in columns if min(c["right"], block["xMax"]) - max(c["left"], left)
                   > .5 * min(c["right"] - c["left"], block["xMax"] - left)]
        require(len(matches) <= 1, "bbox block crosses columns")
        if matches:
            column = matches[0]
            column["left"] = min(column["left"], left)
            column["right"] = max(column["right"], block["xMax"])
            column["lines"].extend(block["lines"])
        else:
            columns.append({"left": left, "right": block["xMax"], "lines": list(block["lines"])})
    columns.sort(key=lambda c: c["left"])
    require(all(a["right"] <= b["left"] for a, b in zip(columns, columns[1:])), "overlapping bbox columns")

    def render(lines, left):
        return "\n".join(" " * max(0, round((x - left) / 3)) + text
                         for x, y, text in sorted(lines, key=lambda line: (line[1], line[0])))

    head = [b for b in wide if b["yMax"] <= top]
    foot = [b for b in wide if b["yMin"] >= bottom]
    ordered = "\n\n".join([render(b["lines"], b["xMin"]) for b in sorted(head, key=lambda b: b["yMin"])]
                           + [render(c["lines"], c["left"]) for c in columns]
                           + [render(b["lines"], b["xMin"]) for b in sorted(foot, key=lambda b: b["yMin"])]) + "\n"
    require(inventory(ordered) == inventory(original), "bbox/source text inventory differs; preserve both for diagnosis")
    return ordered, [{"left": c["left"], "right": c["right"]} for c in columns]


def reading_text(ctx, page, source, original):
    recipe = "pdftotext-bbox-layout-columns-v2"
    identity = {"format": "index-reading-order-v1", "source_hash": fingerprint(source),
                "recipe": recipe}
    path = ctx.path(f"index-{page}-ordered.json")
    if path.exists():
        saved = json.loads(path.read_text())
        # Older pages keep the recipe they were derived with; its own recorded
        # identity and key still have to verify, so the evidence cannot drift.
        identity = {"format": saved.get("format"), "source_hash": saved.get("source_hash"),
                    "recipe": saved.get("recipe")}
        require(all(saved.get(k) == v for k, v in identity.items()), "stale ordered index text")
        require(saved.get("format") == "index-reading-order-v1"
                and saved.get("source_hash") == fingerprint(source), "stale ordered index text")
        require(saved["key"] == fingerprint(identity | {"text": saved["text"], "columns": saved["columns"]}),
                "ordered index evidence changed")
        require(inventory(saved["text"]) == inventory(original), "ordered/source text inventory differs")
    else:
        xml = subprocess.run(["pdftotext", "-f", str(page), "-l", str(page), "-bbox-layout", str(ctx.pdf), "-"],
                             capture_output=True, text=True, check=True, timeout=60).stdout
        save(ctx.path(f"index-{page}-bbox.json"), identity | {"xml": xml})
        text, columns = column_text(xml, original)
        require(pdf_identity(ctx.pdf) == source["pdf_identity"], "PDF changed while ordering index text")
        payload = identity | {"text": text, "columns": columns}
        saved = payload | {"key": fingerprint(payload)}
        save(path, saved)
    return saved["text"], saved["key"]
