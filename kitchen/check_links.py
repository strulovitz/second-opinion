#!/usr/bin/env python3
"""BIBLE 6.9 / 7.13: check relative HTML links and fixed viewer dependencies."""

import argparse
import json
import random
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        self.links.extend(value for key, value in attrs if key in ("href", "src") and value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-pending", action="store_true", help="report not-yet-exported medical layers separately during Phase A")
    args = parser.parse_args()
    site = ROOT / "site"
    broken, pending, checked = [], [], 0

    def check(path, source, future=False):
        nonlocal checked
        checked += 1
        if path.exists():
            return
        (pending if future and args.allow_pending else broken).append(f"{source}: {path.relative_to(site)}")

    for path in sorted(site.rglob("*.html")):
        reader = Links()
        reader.feed(path.read_text())
        for href in reader.links:
            url = urlsplit(href)
            if url.scheme or url.netloc or not url.path:
                continue
            target = (path.parent / unquote(url.path)).resolve()
            if not target.is_relative_to(site):
                broken.append(f"{path.relative_to(site)}: link escapes site: {href}")
                continue
            check(target, str(path.relative_to(site)), target.is_relative_to(site / "pages"))
    names = ["geography/geography.json", "geography/districts_lookup.json", "geography/district_raster.png",
             "geography/continents_texture.png", "geography/continents_texture_2k.png", "wording.json", "search.json"]
    for name in names:
        check(site / "data" / name, "viewer data", name == "search.json")
    for name in ("three.module.js", "three.core.js", "OrbitControls.js", "LICENSE", "VERSION.txt"):
        check(site / "assets/three" / name, "vendored Three.js")
    for name in ("app.js", "data.js", "geo.js", "ui.js", "globe3d.js", "map2d.js", "viewer.css",
                 "materials.js", "atlas.js", "sandtable.js", "layers.js", "labels.js"):
        check(site / "viewer" / name, "viewer module")
    rng = random.Random(0)
    search = site / "data/search.json"
    if search.exists():
        rows = json.loads(search.read_text())
        for row in rng.sample(rows, min(20, len(rows))):
            check(site / "data/entities" / (row["slug"] + ".json"), "sample entity")
    geography = site / "data/geography/geography.json"
    if geography.exists():
        rows = [r for r in json.loads(geography.read_text()) if r["level"] == "district"]
        if any(r.get('tile_sides') for r in rows):
            check(site / 'data/geography/honeycomb.json', 'whole-tile topology')
        # Opus 5.5 addition (Amendment 3.6): one flower 2-D map per book.
        for book in (r["book_id"] for r in json.loads(geography.read_text()) if r["level"] == "continent"):
            check(site / "data/geography/flowers" / f"{book}.json", "flower map")
        for row in rng.sample(rows, min(20, len(rows))):
            check(site / "data/districts" / (row["territory_id"] + ".json"), "sample district", True)
    print(f"Links/assets checked: {checked}; broken: {len(broken)}; pending medical exports: {len(pending)}")
    for item in broken:
        print("BROKEN", item)
    if pending:
        print("Pending exports are not claimed built. Use the default strict check after exporting.")
    return int(bool(broken))


if __name__ == "__main__":
    raise SystemExit(main())
