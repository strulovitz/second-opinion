#!/usr/bin/env python3
"""One bounded Qwen index request, saving the full local response before validation."""

import hashlib
import json
import time
from datetime import datetime, timezone
from unittest.mock import patch

from index_common import Context, arguments, cli, fingerprint, require, save
from index_pages import ground_entries
from index_order import reading_text
from index_prompts import PARSE
from index_schema import PARSE_SCHEMA
from toc_evidence import pdf_identity


def main(argv=None):
    parser = arguments(__doc__)
    parser.add_argument("--page", type=int, required=True)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--no-reasoning", action="store_true",
                        help="explicit experiment only; otherwise retain current reader settings")
    parser.add_argument("--allow-reasoning", action="store_true",
                        help="explicit hard-page experiment; mutually exclusive with --no-reasoning")
    parser.add_argument("--json-output", action="store_true",
                        help="use the index parser's constrained JSON output mode")
    parser.add_argument("--ordered-text", action="store_true",
                         help="derive the physical column order, preserving source receipts")
    parser.add_argument("--structured-output", action="store_true",
                        help="constrain generation to the full index answer schema")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float)
    parser.add_argument("--presence-penalty", type=float)
    args = parser.parse_args(argv)
    ctx = Context(args)
    require(args.limit == 0 and not args.fallback and not args.plan,
             "diagnostic uses exactly one --page, not pipeline limits/fallback/plans")
    require(not (args.no_reasoning and args.allow_reasoning), "choose one reasoning mode")
    require(args.page in ctx.pages, "page must be inside this book's configured index")
    require(0 < args.timeout <= 300, "diagnostic timeout must be between 1 and 300 seconds")
    ctx.execution_guard()
    source = json.loads(ctx.path(f"index-{args.page}-source.json").read_text())
    text = ctx.path(f"index-{args.page}.txt").read_text()
    require(source["pdf_identity"] == pdf_identity(ctx.pdf), "changed source PDF")
    require(source["text_hash"] == fingerprint(text), "changed source text")
    image = ctx.image(args.page)
    require(hashlib.sha256(image.read_bytes()).hexdigest() == source["image_hash"],
            "changed source image")
    require(len(text.strip()) >= 30, "this diagnostic requires an existing text-layer page")
    order_key = None
    if args.ordered_text:
        text, order_key = reading_text(ctx, args.page, source, text)

    import reader
    from db import _driver, env

    require(env("READER_MODEL") == "qwen3.8:27b", "Nir requested exactly qwen3.8:27b")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    path = ctx.path(f"index-diagnostic-{args.page}-{stamp}.json")
    record = {"book_id": ctx.bid, "page": args.page, "source": source,
              "input_identity": ctx.identity, "prompt_hash": fingerprint(PARSE),
              "explicit_no_reasoning": args.no_reasoning,
               "json_output": args.json_output, "reading_order_key": order_key, "requests": []}
    record["response_schema"] = PARSE_SCHEMA if args.structured_output else None
    record["explicit_allow_reasoning"] = args.allow_reasoning
    post = reader.requests.post

    def capture(url, **kwargs):
        # The reader request has no credentials. Save only the model request,
        # never the environment, database configuration, headers or server URL.
        request = {"body": kwargs["json"], "timeout": kwargs["timeout"]}
        record["requests"].append(request)
        save(path, record)
        started = time.monotonic()
        try:
            response = post(url, **kwargs)
            request["elapsed_seconds"] = round(time.monotonic() - started, 3)
            request["status_code"] = response.status_code
            try:
                request["response"] = response.json()
            except ValueError:
                request["response_text"] = response.text
            save(path, record)
            return response
        except Exception as exc:
            request["elapsed_seconds"] = round(time.monotonic() - started, 3)
            request["error_type"] = type(exc).__name__
            save(path, record)
            raise

    print(f"One Qwen request: {ctx.bid} PDF {args.page}; timeout={args.timeout}s; no automatic retry",
          flush=True)
    print(f"Local evidence: {path}", flush=True)
    started = time.monotonic()
    try:
        with patch.object(reader.requests, "post", capture):
            answer = reader.ask(PARSE, text, max_tokens=12000, retries=1,
                                timeout=args.timeout,
                                no_reasoning=False if args.allow_reasoning else True if args.no_reasoning else None,
                                json_output=args.json_output,
                                response_schema=PARSE_SCHEMA if args.structured_output else None,
                                temperature=args.temperature, top_p=args.top_p,
                                presence_penalty=args.presence_penalty)
        record["answer"] = answer
        try:
            entries = ground_entries(answer, text, args.page, str(image))
            record["validation"] = {"ok": True, "entries": len(entries)}
        except (ValueError, KeyError, TypeError) as exc:
            record["validation"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    except Exception as exc:
        # Network exception messages can contain URLs; preserve only the type.
        record["reader_error_type"] = type(exc).__name__
    finally:
        record["elapsed_seconds"] = round(time.monotonic() - started, 3)
        save(path, record)
        _driver.close()
    print(f"Elapsed: {record['elapsed_seconds']}s")
    print(f"Validation: {record.get('validation', record.get('reader_error_type'))}")
    if record["requests"]:
        response = record["requests"][-1].get("response", {})
        choices = response.get("choices", [])
        print(f"Token usage: {response.get('usage')}")
        if choices:
            message = choices[0].get("message", {})
            print(f"Finish reason: {choices[0].get('finish_reason')}; "
                  f"answer characters: {len(message.get('content') or '')}; "
                  f"reasoning characters: {len(message.get('reasoning') or message.get('reasoning_content') or '')}")
    return 0 if record.get("validation", {}).get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(cli(main))
