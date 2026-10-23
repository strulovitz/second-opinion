"""Backed-up, recoverable multi-file writes for one book, with input guards.

An interrupted bundle can be rolled back with:
  python kitchen/toc_store.py kitchen/logs/<backup-directory> --recover
Individual replacements are atomic; a journal covers interruption between them.
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

from page_offset import require
from toc_reexport import atomic_write


def snapshot(paths):
    return {p: p.read_text() if p.exists() else None for p in paths}


def check_inputs(originals):
    require(snapshot(originals) == originals, "inputs changed during verification; retry")


def recover(backup):
    backup = Path(backup)
    journal = backup / "transaction.json"
    data = json.loads(journal.read_text())
    require(data["state"] == "applying", "transaction does not need recovery")
    root = Path(data["root"])
    for row in data["files"]:
        path = root / row["path"]
        have = path.read_text() if path.exists() else None
        require(have in (row["before"], row["after"]),
                f"{path}: changed after interruption; preserve it and ask for review")
    for row in data["files"]:
        path = root / row["path"]
        if row["before"] is None:
            path.unlink(missing_ok=True)
        else:
            atomic_write(path, row["before"])
    data["state"] = "rolled-back"
    atomic_write(journal, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def save_bundle(root, logs, book, operation, originals, payloads, retire=()):
    """All originals (including absent inputs) must still match before writes.

    No-op retries do not create new backups. Copies of ALL inputs, history
    and a recoverable journal are durable before a source/cache is replaced.
    """
    root, logs = Path(root), Path(logs)
    pending = list((logs / "toc-tool-backups" / book).glob("*/transaction.json"))
    for journal in pending:
        if json.loads(journal.read_text())["state"] == "applying":
            raise ValueError(f"interrupted transaction: python kitchen/toc_store.py {journal.parent} --recover")
    check_inputs(originals)
    changes = {p: text for p, text in payloads.items() if originals.get(p) != text}
    changes.update({p: None for p in retire if originals.get(p) is not None})
    require(set(changes) <= set(originals), "untracked transaction output")
    if not changes:
        return None
    backup = logs / "toc-tool-backups" / book / datetime.now().strftime("%Y%m%dT%H%M%S%f")
    backup.mkdir(parents=True)
    for i, (path, text) in enumerate(originals.items()):
        if text is not None:
            (backup / f"{i:02d}-{path.name}").write_text(text)
    data = {"state": "applying", "root": str(root), "book": book, "operation": operation,
            "files": [{"path": str(p.relative_to(root)), "before": originals[p], "after": text}
                      for p, text in changes.items()]}
    journal = backup / "transaction.json"
    atomic_write(journal, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    try:
        check_inputs(originals)
        for path, text in changes.items():
            if text is None:
                path.unlink()
            else:
                atomic_write(path, text)
        data["state"] = "completed"
        atomic_write(journal, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    except BaseException:
        recover(backup)
        raise
    return backup


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("backup", type=Path)
    parser.add_argument("--recover", action="store_true", required=True)
    args = parser.parse_args()
    recover(args.backup)
    print("Restored the transaction's original files; rerun the one-book dry run")
