#!/usr/bin/env python3
"""Download the pinned BIBLE viewer dependencies, unmodified, with hashes."""

import hashlib
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.186.0"
FILES = {"three.module.js": "build/three.module.js", "three.core.js": "build/three.core.js",
         "OrbitControls.js": "examples/jsm/controls/OrbitControls.js", "LICENSE": "LICENSE"}


def main():
    target = ROOT / "site/assets/three"
    target.mkdir(parents=True, exist_ok=True)
    records = [f"Three.js r186 / npm {VERSION}", "Vendored 2026-10-23; MIT; no runtime CDN requests.",
               "Modern three.module.js imports three.core.js; both are required."]
    for name, relative in FILES.items():
        require_path = target / name
        if require_path.exists():
            raise SystemExit(f"Preserve existing vendor file {require_path}; inspect it before replacing")
        url = f"https://unpkg.com/three@{VERSION}/{relative}"
        try:
            with urlopen(url, timeout=40) as response:
                data = response.read()
        except OSError:
            url = f"https://cdn.jsdelivr.net/npm/three@{VERSION}/{relative}"
            with urlopen(url, timeout=40) as response:
                data = response.read()
        if len(data) < 100 or data.lstrip().lower().startswith((b"<!doctype", b"<html")):
            raise SystemExit(f"Invalid dependency download: {name}")
        require_path.write_bytes(data)
        records.extend([f"{name} {len(data)} bytes SHA256 {hashlib.sha256(data).hexdigest()}", url])
        print(f"Vendored {name}: {len(data)} bytes")
    (target / "VERSION.txt").write_text("\n".join(records) + "\n")


if __name__ == "__main__":
    main()
