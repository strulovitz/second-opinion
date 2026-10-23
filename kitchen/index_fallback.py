#!/usr/bin/env python3
"""BIBLE 3.7.9: free-reader terms from saved chapter titles/opener pages.

Requires explicit --fallback AFTER the operator confirms there is no usable
index. An unset index locator alone is not evidence that an index is absent.
Existing chapter lists are read-only inputs; no chapter verification/rebuild.
"""

import hashlib
import json
import re
import subprocess

from pypdf import PdfReader

from index_common import (Context, arguments, ask_checked, cli, fingerprint,
                          lock, reader_access, require, save)
from index_pages import citation_unit, literal_pattern
from toc_evidence import pdf_identity

PROMPT = """List the medical terms in this chapter opener as a JSON list of
strings, verbatim. Include the chapter title when visible. Do not classify,
paraphrase, infer diagnoses or add terms absent from the page. Report the
integer PRINTED folio from a page corner, not the chapter number or PDF
page label; null if missing/ambiguous/electronic. Output ONLY JSON:
{"terms":["verbatim phrase"],"printed_page":<integer or null>,
"text":"<verbatim transcription when an image is supplied; otherwise empty>"}.
"""


def fallback(ctx, ask, model, vision_model):
    require(ctx.fallback, "use --fallback only after confirming BIBLE 3.7.9 applies")
    contents = json.loads(ctx.path("toc.json").read_text())
    flat = [(p["name"], ch) for p in contents["provinces"] for ch in p["chapters"]]
    require(len(flat) == len(ctx.districts), "saved chapter/district count differs")
    eyes = json.loads(ctx.path("eyes.json").read_text())["chapters"] if ctx.path("eyes.json").exists() else []
    pairs = {(r["province"], str(r["number"]), r["title"]): r for r in eyes}
    unit, identity = citation_unit(ctx), pdf_identity(ctx.pdf)
    all_entries, processed, new, unresolved = [], 0, 0, []
    prior = ctx.path("index-entries.json")
    if prior.exists():
        require(json.loads(prior.read_text())["input_identity"] == ctx.identity,
                "existing index/fallback input differs; archive the old index state before changing mode")
    with PdfReader(str(ctx.pdf)) as reader:
        for index, ((province, ch), district) in enumerate(zip(flat, ctx.districts)):
            row = pairs.get((province, str(ch.get("number")), ch["title"]), {})
            pdf = ch.get("pdf_page") or row.get("pdf_page")
            if pdf is None and unit == "pdf-page":
                pdf = ch["page_start"]
            if pdf is None and type(ctx.book.get("page_offset")) is int:
                pdf = ch["page_start"] + ctx.book["page_offset"]
            require(type(pdf) is int and 0 < pdf <= len(reader.pages), "fallback needs an already recorded PDF opener; do not guess")
            path = ctx.path(f"fallback-{index + 1}.json")
            key = fingerprint([ctx.identity, identity, ch, district, PROMPT, model, vision_model])
            if path.exists():
                record = json.loads(path.read_text())
                require(record["key"] == key, "stale fallback cache")
                image = ctx.image(pdf)
                require(image.is_file() and hashlib.sha256(image.read_bytes()).hexdigest() == record["image_hash"], "fallback evidence image changed")
            else:
                if ctx.args.limit and new >= ctx.args.limit:
                    break
                image = ctx.image(pdf)
                image.parent.mkdir(parents=True, exist_ok=True)
                if not image.exists():
                    subprocess.run(["pdftoppm", "-f", str(pdf), "-l", str(pdf), "-r", "150", "-png", "-singlefile",
                                    str(ctx.pdf), str(image.with_suffix(""))], capture_output=True, check=True, timeout=90)
                text = reader.pages[pdf - 1].extract_text() or ""
                known = ch["page_start"] if unit == "printed" else row.get("printed") if row.get("kind") == "printed" else None
                if known is None and type(ctx.book.get("page_offset")) is int:
                    known = pdf - ctx.book["page_offset"]
                use_image = len(text.strip()) < 30 or known is None
                def validate(answer):
                    require(isinstance(answer["terms"], list), "fallback terms must be a list")
                    source = text if len(text.strip()) >= 30 else answer.get("text", "")
                    require(source.strip(), "fallback transcription is empty")
                    for term in answer["terms"]:
                        require(isinstance(term, str) and term.strip() and re.search(literal_pattern(term), source), "fallback term not verbatim in source")
                    printed = known if known is not None else answer.get("printed_page")
                    require(printed is None or (type(printed) is int and printed > 0), "invalid printed folio")
                    if known is None and printed is not None:
                        lines = [line.strip() for line in source.splitlines() if line.strip()]
                        distinct_footer = len(lines) > 8 and str(printed) in lines[-4:]
                        require(str(printed) in lines[:4] + lines[-4:]
                                and (str(printed) != str(ch.get("number")) or distinct_footer),
                                "fallback folio is not distinctly readable in a page corner")
                    return {"terms": answer["terms"], "source": source, "printed": printed}
                answer = ask_checked(ask, PROMPT, text or "Read the selected opener.", validate,
                                     images=[image] if use_image else None, max_tokens=9000)
                phrases = list(dict.fromkeys(answer["terms"]))
                title_visible = bool(re.search(literal_pattern(ch["title"]), answer["source"]))
                if title_visible and ch["title"] not in phrases:
                    phrases.insert(0, ch["title"])
                entries = []
                for phrase in phrases:
                    match = re.search(literal_pattern(phrase), answer["source"])
                    start = answer["source"].rfind("\n", 0, match.start()) + 1
                    end = answer["source"].find("\n", match.end())
                    quote = answer["source"][start:end if end >= 0 else None]
                    source = {"source_index_pdf": pdf, "image_file": str(image), "quote": quote}
                    entries.append({"id": fingerprint([ctx.bid, index, phrase]), "headword": phrase, "display": phrase,
                                    "see": None, "subentries": [], "sources": [source],
                                    "created_from": "toc" if phrase == ch["title"] else "page",
                                    "references": [source | {"raw": str(answer["printed"]), "printed_page": answer["printed"],
                                        "district_ids": [district["territory_id"]], "source": "page", "reader_model": vision_model if use_image else model,
                                        "issue": "mapping-unresolved" if answer["printed"] is None else None}]})
                record = {"key": key, "entries": entries, "title_visible": title_visible,
                          "image_hash": hashlib.sha256(image.read_bytes()).hexdigest()}
                require(pdf_identity(ctx.pdf) == identity, "PDF changed during fallback reading")
                save(path, record)
                new += 1
                print(f"  fallback opener {index + 1}/{len(flat)}", flush=True)
            all_entries.extend(record["entries"])
            processed += 1
            if not record["title_visible"]:
                unresolved.append(ch["number"])
    counts = {"online-only": 0, "non-integer-or-malformed": 0, "outside-districts": 0,
              "mapping-unresolved": sum(r["issue"] is not None for e in all_entries for r in e["references"])}
    result = {"book_id": ctx.bid, "input_identity": ctx.identity, "unit": "printed", "entries": all_entries,
              "pages_parsed": processed, "expected_pages": len(flat), "reference_counts": counts,
              "complete": processed == len(flat) and not unresolved, "unresolved_title_evidence": unresolved,
              "mode": "chapter-fallback", "limitation": "thin registry from existing chapter titles and opener terms; not a full index"}
    save(ctx.path("index-entries.json"), result)
    ctx.summary("fallback", new_openers=new, saved_openers=processed, terms=len(all_entries), unresolved_titles=len(unresolved))
    return result


def main(argv=None):
    args = arguments(__doc__).parse_args(argv)
    ctx = Context(args)
    if args.plan:
        ctx.plan("fallback")
        return 0
    ctx.execution_guard()
    with lock(ctx.path("index.lock")):
        fallback(ctx, *reader_access())
    return 0


if __name__ == "__main__":
    raise SystemExit(cli(main))
