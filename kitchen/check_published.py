#!/usr/bin/env python3
"""THE SITE FOLDER LAW check (BIBLE Part 9, section 9.S; Law 16).

Everything the public website serves lives in site/ and must be in GitHub.
After a plain `git pull` on ANY computer (the laptop or the desktop), the
website must be complete. This script exits 1 and says what is wrong if:

  - a required file or folder under site/ is missing;
  - any file under site/ is ignored by git;
  - any file under site/ is untracked or changed but not committed;
  - this computer has commits that are not on GitHub yet (not pushed);
  - any single file under site/ is over 90 MB (GitHub refuses 100 MB).

With --live it also fetches the live website's search.json and compares
its md5 with the local file (the live site is served by whichever PC is
hosting, so that PC must have pulled first).

Never say "published" or "pushed" until this script prints OK.
"""
import hashlib, subprocess, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
REQUIRED = ["index.html", "viewer/index.html", "data/search.json", "data/golden.json",
            "data/wording.json", "data/entities", "data/districts", "data/geography"]
MAX_BYTES = 90 * 1024 * 1024
LIVE = "https://www.strulovitz.org/2nd-opinion/data/search.json"


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout


def main():
    bad = []
    for rel in REQUIRED:
        p = SITE / rel
        if not p.exists():
            bad.append(f"missing: site/{rel}")
        elif p.is_dir() and not any(p.iterdir()):
            bad.append(f"empty folder: site/{rel}")
    for line in git("status", "--porcelain", "--ignored", "--untracked-files=all", "site/").splitlines():
        code, path = line[:2], line[3:]
        kind = {"!!": "IGNORED by git (hidden from GitHub)", "??": "untracked (not in GitHub)"}.get(code, f"not committed ({code.strip()})")
        bad.append(f"{kind}: {path}")
    git("fetch", "-q", "origin")
    branch = git("rev-parse", "--abbrev-ref", "HEAD").strip()
    ahead = git("rev-list", "--count", f"origin/{branch}..HEAD").strip()
    if ahead != "0":
        bad.append(f"{ahead} commit(s) on this computer are NOT pushed to GitHub (origin/{branch})")
    files = [p for p in SITE.rglob("*") if p.is_file()]
    for p in files:
        if p.stat().st_size > MAX_BYTES:
            bad.append(f"too big for GitHub ({p.stat().st_size // 2**20} MB): {p.relative_to(ROOT)}")
    if "--live" in sys.argv:
        local = hashlib.md5((SITE / "data/search.json").read_bytes()).hexdigest()
        try:
            with urllib.request.urlopen(urllib.request.Request(LIVE, headers={"User-Agent": "check_published"}), timeout=60) as r:
                live = hashlib.md5(r.read()).hexdigest()
            if live != local:
                bad.append(f"live search.json differs from local (live {live}, local {local}); has the hosting PC pulled?")
        except Exception as e:
            bad.append(f"live search.json not served: {LIVE} ({e})")
    if bad:
        print(f"NOT PUBLISHED: {len(bad)} problem(s). The website from GitHub would be broken or old:")
        for b in bad[:40]:
            print("  - " + b)
        if len(bad) > 40:
            print(f"  ... and {len(bad) - 40} more")
        return 1
    print(f"OK: site/ is complete and fully tracked and pushed ({len(files)} files)" + (" and live matches" if "--live" in sys.argv else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
