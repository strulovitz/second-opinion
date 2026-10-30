"""Bounded fallback for incomplete pages; keep every literal line and reference."""

import copy
import json
import re
from datetime import datetime, timezone

from index_common import ask_checked, fingerprint, require, save
from index_pages import (CLOSING, REF_ITEM, SEE_TAIL, ground_entries, is_reference_line,
                         source_references)
from index_prompts import PARSE
from index_schema import PARSE_CONTROLS, PARSE_SCHEMA, check_shape

FORMAT = "index-fragments-v4-single-entry"
# A page whose first line is a lowercase qualifier is a continuation of the
# entry opened on the previous page. Real headwords may start lowercase too
# (hMPV, hMG), so only the index's own subentry words count as the signal.
CONTINUATION_START = re.compile(
    r"^(?:in|with|for|and|of|due to|during|after|before|by|from|to|as|at|on|"
    r"vs\.?|versus|or|including|without)\b")
FRAGMENT_NOTE = ("\nThis input is a contiguous fragment of one index page. "
                 "If its first line is indented, use CONTINUED as its first headword, "
                 "even if those words look like a term. This fragment has exactly one main "
                 "entry or one continuation; return that entry and copy through the last supplied line.")
FRAGMENT_SCHEMA = copy.deepcopy(PARSE_SCHEMA)
FRAGMENT_SCHEMA["properties"]["entries"].update(minItems=1, maxItems=1)


def label_prefix_line(lines, i):
    """True when a bare number line is a superscript mass number on the next label."""
    line, token = lines[i], lines[i].strip()
    if not REF_ITEM.fullmatch(token):
        return False
    previous = next((row for row in reversed(lines[:i]) if row.strip()), "")
    if previous.rstrip().endswith(","):
        return False
    following = next((row for row in lines[i + 1:] if row.strip()), "")
    if not following or len(following) - len(following.lstrip(" ")) <= len(line) - len(line.lstrip(" ")):
        return False
    following = SEE_TAIL.sub("", following.strip()).rstrip(" .,")
    return not all(REF_ITEM.fullmatch(item.strip().lstrip(CLOSING).strip())
                   for item in following.split(","))


def fragments(text, target=24):
    """Cut after complete reference runs, never inside a wrapped label/list."""
    lines = text.splitlines(keepends=True)
    prefixes = [i for i in range(1, len(lines)) if label_prefix_line(lines, i)]
    boundaries = prefixes + [i for i in range(1, len(lines))
                  if source_references(lines[i - 1]) and not lines[i - 1].rstrip().endswith(',')
                  and lines[i].strip()
                  and (not lines[i][0].isspace() or source_references(lines[i]))
                  and not label_prefix_line(lines, i - 1)
                  and not is_reference_line(lines[i], ''.join(lines[:i]))]
    boundaries.sort()
    boundaries.append(len(lines))
    result, start = [], 0
    while start < len(lines):
        candidates = [i for i in boundaries if start < i <= start + target]
        end = max(candidates) if candidates else min(i for i in boundaries if i > start)
        # Each request ends before the next physical main-entry margin. This
        # prevents an early close after a large entry from losing later terms.
        next_main = next((i for i in range(start + 1, len(lines))
                          if lines[i].strip() and not lines[i][0].isspace()
                          and len(lines[i].strip()) > 1
                          and (not is_reference_line(lines[i], ''.join(lines[:i]))
                               or label_prefix_line(lines, i))
                          and any(len(line.strip()) > 1 for line in lines[start:i])), len(lines))
        end = min(end, next_main)
        result.append({"start_line": start, "end_line": end, "text": ''.join(lines[start:end])})
        start = end
    require(''.join(part["text"] for part in result) == text, "fragment plan lost source text")
    return result


def printed_label(line):
    """The leading label of a main-entry line, without its page references."""
    items = SEE_TAIL.sub("", line.strip()).rstrip(" .,").split(",")
    while items and REF_ITEM.fullmatch(items[-1].strip().lstrip(CLOSING).strip()):
        items.pop()
    return ",".join(items).strip()


def parse_fragments(ctx, ask, text, page, image, parent_key):
    lines = text.splitlines()
    first = next((line for line in lines if line.strip()), "")
    if first[:1].isspace() or CONTINUATION_START.match(first):
        require(False, f"PDF {page}: the page begins inside an open entry; this page "
                       "must be hand-read from the page image, not guessed from fragments")
    for i in range(2, len(lines)):
        if (lines[i].strip() and not lines[i - 1].strip()
                and lines[i - 2][:1].isspace() and lines[i][:1].islower()
                and lines[i][:1].isascii()):
            require(False, f"PDF {page}: a new column continues an open entry; this page "
                           "must be hand-read from the page image, not guessed from fragments")
    parts = fragments(text)
    require(len(parts) > 1, "page cannot be split safely; preserve response for SMART diagnosis")
    plan = {"format": FORMAT, "parent_key": parent_key,
            "prompt_hash": fingerprint(PARSE + FRAGMENT_NOTE), "schema": FRAGMENT_SCHEMA,
            "parts": [{k: p[k] for k in ("start_line", "end_line")} | {"text_hash": fingerprint(p["text"])}
                      for p in parts]}
    manifest = ctx.path(f"index-{page}-fragments.json")
    if manifest.exists():
        require(json.loads(manifest.read_text()) == plan, "stale fragment plan; preserve evidence")
    else:
        save(manifest, plan)
    merged = []
    for number, part in enumerate(parts, 1):
        key = fingerprint([plan, number, part["text"]])
        path = ctx.path(f"index-{page}-fragment-{number}.json")

        def evidence(kind, value):
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            save(ctx.path(f"index-{page}-fragment-{number}-{kind}-{stamp}.json"),
                 {"key": key, "parent_key": parent_key, "part": number, **part, **value})

        def continuation(rows):
            require(len(rows) == 1, "fragment must contain exactly one entry or continuation")
            if number > 1:
                first_line = next(line for line in part["text"].splitlines() if line.strip())
                continued = bool(rows and rows[0]["headword"] == "CONTINUED")
                if first_line[0].isspace():
                    require(continued, "first line is indented: its headword MUST be CONTINUED, and "
                                       "that first line stays as the first subentry with its own page references")
                else:
                    require(not continued,
                            "first line starts a NEW main entry, not CONTINUED; use the printed label "
                            f"as the headword (it starts {printed_label(first_line)!r}) and the "
                            "trailing numbers as its pages, not a subentry")

        def validate(answer):
            try:
                check_shape(answer)
                # Check the layout rule first: a misread continuation hides the
                # real error and sends the retry an unhelpful message.
                continuation(answer["entries"])
                try:
                    rows = ground_entries(answer, part["text"], page, image)
                except ValueError as exc:
                    first_line = next(line for line in part["text"].splitlines() if line.strip())
                    if first_line[0].isspace() and answer["entries"][0]["headword"] == "CONTINUED":
                        raise ValueError(str(exc) + "; this fragment starts with an indented subentry: "
                                         "keep that line as the first subentry under CONTINUED, "
                                         "with its page references") from exc
                    raise
                require(rows or not source_references(part["text"]), "empty reference-bearing fragment")
                return rows
            except (ValueError, KeyError, TypeError) as exc:
                evidence("rejected", {"answer": answer, "error": f"{type(exc).__name__}: {exc}"})
                raise

        if path.exists():
            record = json.loads(path.read_text())
            require(record["key"] == key, "stale fragment cache; preserve evidence")
            rows = ground_entries({"entries": record["entries"]}, part["text"], page, image)
            continuation(rows)
        else:
            print(f"    PDF {page} fragment {number}/{len(parts)}; lines "
                  f"{part['start_line'] + 1}-{part['end_line']}", flush=True)
            rows = ask_checked(ask, PARSE + FRAGMENT_NOTE, part["text"], validate, max_tokens=4000,
                               on_response=lambda response: evidence("response", response),
                               **(PARSE_CONTROLS | {"response_schema": FRAGMENT_SCHEMA}))
            save(path, {"key": key, "entries": rows})
        for row in copy.deepcopy(rows):
            if row["headword"] == "CONTINUED" and merged:
                require(not merged[-1].get("see") and not row.get("see"), "orphan fragment continuation")
                merged[-1]["pages"].extend(row["pages"])
                merged[-1]["subentries"].extend(row["subentries"])
            else:
                require(number == 1 or row["headword"] != "CONTINUED", "orphan fragment continuation")
                merged.append(row)
    # Rebuild quotes from the full original page; never publish fragment quotes.
    return ground_entries({"entries": merged}, text, page, image)
