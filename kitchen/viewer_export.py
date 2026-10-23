"""Shared, deterministic static export helpers. No database writes."""

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GROUPS = ("symptoms-and-signs", "diseases-and-conditions", "treatments-and-drugs")
RELATIONS = "PRESENTS_WITH|TREATED_BY|HARMS|LEADS_TO|MISTAKEN_FOR"


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r"[a-zA-Z0-9_-][a-zA-Z0-9._-]*", value):
        raise ValueError(f"Invalid export identifier: {value!r}")
    return value


def write_json(relative, content, root=ROOT, dated=True):
    """Mirror identical files; unchanged content retains its original export_date."""
    paths = [root / "data/export" / relative, root / "site/data" / relative]
    content = json.loads(json.dumps(content, ensure_ascii=False, default=str, allow_nan=False))
    if dated:
        content = dict(content)
        content.pop("export_date", None)
        old = json.loads(paths[0].read_text()) if paths[0].exists() else {}
        old_date = old.pop("export_date", None)
        content["export_date"] = old_date if old == content and old_date else date.today().isoformat()
    raw = (json.dumps(content, ensure_ascii=False, indent=2, sort_keys=True, default=str, allow_nan=False) + "\n").encode()
    if len(raw) > 40 * 1024 * 1024:
        raise ValueError(f"Export exceeds BIBLE's 40 MB limit: {relative}; stop for human review")
    changed = 0
    for path in paths:
        if path.exists() and path.read_bytes() == raw:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_bytes(raw)
        temporary.replace(path)
        changed += 1
    return changed, len(raw)


def copy_wording(root=ROOT):
    content = json.loads((root / "kitchen/prompts/wording.json").read_text())
    return write_json("wording.json", content, root, dated=False)
