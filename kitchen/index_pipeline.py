#!/usr/bin/env python3
"""BIBLE 3.7.10: run one book's index stages in order, in the foreground."""

import subprocess
import sys
from pathlib import Path

from index_common import Context, arguments, cli, require

STAGES = ("extract", "parse", "classify", "resolve")


def main(argv=None):
    parser = arguments(__doc__)
    parser.add_argument("--stop-after", choices=STAGES, default="resolve")
    parser.add_argument("--layout", action="store_true")
    parser.add_argument("--columns", action="store_true")
    args = parser.parse_args(argv)
    ctx = Context(args)
    # The seed-book checkpoint applies before ANY reader work on later books.
    if not args.plan:
        ctx.execution_guard()
    stages = STAGES[:STAGES.index(args.stop_after) + 1]
    if args.fallback:
        stages = ("fallback",) + tuple(s for s in stages if s not in ("extract", "parse"))
    for stage in stages:
        command = [sys.executable, str(Path(__file__).with_name(f"index_{stage}.py")), args.book,
                   "--books", str(args.books), "--logs", str(args.logs), "--geography", str(args.geography),
                   "--limit", str(args.limit)]
        if args.plan:
            command.append("--plan")
        if args.fallback:
            command.append("--fallback")
        if stage == "extract":
            command += (["--layout"] if args.layout else []) + (["--columns"] if args.columns else [])
        result = subprocess.run(command, check=False)
        if result.returncode:
            return result.returncode
    print(f"{ctx.bid}: pipeline stopped after {args.stop_after}; no unattended process started", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(cli(main))
