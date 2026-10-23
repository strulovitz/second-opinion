#!/usr/bin/env python3
"""BIBLE 3.6: deterministic spherical geography, raster and viewer textures.

  python kitchen/geography.py --draft --out kitchen/logs/geography-draft
  python kitchen/geography.py --books approved-books.json --out data/export/geography

Draft mode uses provisional alphabetical IDs and existing saved book lists.
It does not change books.json, approve seating, load Neo4j or freeze anything.
Normal mode uses accepted books with the BIBLE's clinical clusters/seating.
"""

import argparse
import colorsys
import copy
import csv
import hashlib
import json
import math
import re
import sys
import textwrap
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
W, H = 2048, 1024
CLUSTER_ORDER = ["general", "heart-vessels", "lungs", "gut-liver", "kidney-urology",
                 "brain-nerves-mind", "hormones-metabolism-nutrition", "infection-immunity",
                 "skin-bone-joint-muscle", "women-children-aging", "cancer-blood",
                 "emergency-toxins-environment", "drugs", "senses", "surgery-anesthesia",
                 "imaging-laboratory"]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def fibonacci_sphere(n):
    require(type(n) is int and n > 0, "at least one continent is required")
    i = np.arange(n) + 0.5
    phi = np.arccos(1 - 2 * i / n)
    theta = np.pi * (1 + math.sqrt(5)) * i
    return np.stack([np.sin(phi) * np.cos(theta), np.sin(phi) * np.sin(theta), np.cos(phi)], 1)


def latlon_to_vec(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    return np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])


def vec_to_latlon(vector):
    vector = np.asarray(vector, dtype=float)
    norm = np.linalg.norm(vector)
    require(norm > 1e-14, "cannot locate a zero-vector centre")
    v = vector / norm
    return float(np.degrees(np.arcsin(np.clip(v[2], -1, 1)))), float(np.degrees(np.arctan2(v[1], v[0])))


def pixel_grid(width=W, height=H):
    require(width > 0 and height > 0, "invalid raster dimensions")
    lon = (np.arange(width) + 0.5) / width * 360 - 180
    lat = 90 - (np.arange(height) + 0.5) / height * 180
    longitude, latitude = np.meshgrid(np.radians(lon), np.radians(lat))
    points = np.stack([np.cos(latitude) * np.cos(longitude),
                       np.cos(latitude) * np.sin(longitude), np.sin(latitude)], -1)
    return points.reshape(-1, 3), np.cos(latitude).reshape(-1)


def continent_pixels(points, centres):
    # Bound peak memory instead of materialising a 2-million-by-N matrix.
    result = np.empty(len(points), dtype=np.int32)
    for start in range(0, len(points), 32768):
        result[start:start + 32768] = np.argmax(points[start:start + 32768] @ centres.T, axis=1)
    return result


def seat_books(books, centres, draft=False):
    books = copy.deepcopy(books)
    require(len(books) == len(centres), "book/centre count differs")
    require(len({b['book_id'] for b in books}) == len(books), "duplicate book IDs")
    if draft:
        for index, book in enumerate(sorted(books, key=lambda b: b["book_id"])):
            book.update(seat_order=index + 1, seat_index=index)
        return sorted(books, key=lambda b: b["seat_order"])
    saved = ["seat_order" in b or "seat_index" in b for b in books]
    require(not any(saved) or all(saved), "partial saved seating; supply one complete seating")
    if all(saved):
        for field, expected in (("seat_order", set(range(1, len(books) + 1))),
                                ("seat_index", set(range(len(books))))):
            require(all(type(b.get(field)) is int for b in books)
                    and {b[field] for b in books} == expected, f"invalid saved {field}")
        return sorted(books, key=lambda b: b["seat_order"])
    require(all(b.get("cluster") in CLUSTER_ORDER for b in books), "clinical cluster missing/unknown")
    books.sort(key=lambda b: (CLUSTER_ORDER.index(b["cluster"]), -b["page_count_images"], b["book_id"]))
    # Harrison is the opening-view hub even when another general book is longer.
    hub = next((b for b in books if b["book_id"] == "HARRISON-22"), books[0])
    books.remove(hub)
    books.insert(0, hub)
    free, seated = list(range(len(centres))), []
    for book in books:
        same = [centres[b["seat_index"]] for b in seated if b["cluster"] == book["cluster"]]
        target = (np.mean(same, axis=0) if same else centres[seated[-1]["seat_index"]]) if seated else latlon_to_vec(0, 0)
        best = max(free, key=lambda j: float(centres[j] @ target))
        free.remove(best)
        book.update(seat_order=len(seated) + 1, seat_index=best)
        seated.append(book)
    return seated


def local_xy(points, centre):
    up = np.array([0, 0, 1.0]) if abs(centre[2]) < math.cos(math.radians(1)) else np.array([1.0, 0, 0])
    east = np.cross(up, centre)
    east /= np.linalg.norm(east)
    north = np.cross(centre, east)
    theta = np.arccos(np.clip(points @ centre, -1, 1))
    azimuth = np.arctan2(points @ north, points @ east)
    return theta * np.cos(azimuth), theta * np.sin(azimuth)


def leaf_count(item):
    return sum(leaf_count(child) for child in item["children"]) if "children" in item else 1


def partition(indices, items, x, y, weights, raster, leaves):
    require(items and len(indices) >= sum(leaf_count(i) for i in items),
            "raster resolution cannot give every district at least one pixel")
    if len(items) == 1:
        item = items[0]
        if "children" in item:
            partition(indices, item["children"], x, y, weights, raster, leaves)
        else:
            raster[indices] = item["raster_code"]
            leaves[item["raster_code"]] = indices
        return
    pages = np.array([item["weight"] for item in items], dtype=float)
    split = int(np.argmin(np.abs(np.cumsum(pages)[:-1] - pages.sum() / 2))) + 1
    first, second = items[:split], items[split:]
    fraction = pages[:split].sum() / pages.sum()
    xs, ys = x[indices], y[indices]
    axis = xs if np.ptp(xs) >= np.ptp(ys) else ys
    ordered = indices[np.argsort(axis, kind="stable")]
    cumulative = np.cumsum(weights[ordered])
    cut = int(np.searchsorted(cumulative, fraction * cumulative[-1])) + 1
    cut = min(max(cut, sum(leaf_count(i) for i in first)),
              len(indices) - sum(leaf_count(i) for i in second))
    partition(ordered[:cut], first, x, y, weights, raster, leaves)
    partition(ordered[cut:], second, x, y, weights, raster, leaves)


def territory(tid, level, name, book, parent, start=None, end=None, **extra):
    return {"territory_id": tid, "level": level, "name": name, "book_id": book,
            "parent": parent, "page_start": start, "page_end": end,
            "page_count": end - start + 1 if start is not None and end is not None else 0,
            "border_geojson": None, "raster_code": None, "seat_order": None,
            "part_name": None, "bbox_px": None, "toc_number": None, **extra}


def make_items(book, contents):
    cid = f"C{book['seat_order']:02d}"
    provinces, rows, warnings = [], [], []
    book_counter = 0
    for pi, province in enumerate(contents["provinces"], 1):
        pid = f"{cid}.P00" if province["name"] == "ALL" else f"{cid}.P{pi:02d}"
        chapters = province.get("chapters", [])
        reserved = {int(str(c.get("number"))) for c in chapters if re.fullmatch(r"\d+", str(c.get("number")))}
        used, children = set(), []
        for chapter in chapters:
            book_counter += 1
            start, end = chapter["page_start"], chapter["page_end"]
            require(type(start) is int and type(end) is int and 0 < start <= end,
                    f"{book['book_id']}: invalid stored chapter bounds")
            number = str(chapter.get("number", ""))
            if re.fullmatch(r"\d+", number) and int(number) not in used:
                suffix = int(number)
            else:
                suffix = book_counter
                while suffix in used or suffix in reserved:
                    suffix += 1
            used.add(suffix)
            child = territory(f"{pid}.D{suffix:03d}", "district", chapter["title"], book["book_id"], pid,
                              start, end, toc_number=chapter.get("number"), weight=end - start + 1)
            children.append(child)
        start = min((c["page_start"] for c in children), default=None)
        end = max((c["page_end"] for c in children), default=None)
        row = territory(pid, "province", province["name"], book["book_id"], cid, start, end,
                        part_name=province.get("part_name", province["name"]),
                        weight=sum(c["weight"] for c in children), children=children)
        rows.append(row)
        rows.extend(children)
        if children:
            provinces.append(row)
        else:
            warnings.append(f"{pid}: existing empty heading retained with zero area")
    require(provinces, f"{book['book_id']}: no stored district geometry")
    return provinces, rows, warnings


def build(books, contents, width=W, height=H, draft=False):
    centres = fibonacci_sphere(len(books))
    seated = seat_books(books, centres, draft)
    points, weights = pixel_grid(width, height)
    continents = continent_pixels(points, centres)
    raster = np.zeros(len(points), dtype=np.int32)
    rows, leaves, warnings, code = [], {}, [], 0
    total_weight = weights.sum()
    for book in seated:
        items, children, notes = make_items(book, contents[book["book_id"]])
        warnings.extend(notes)
        districts = [r for r in children if r["level"] == "district"]
        require(code + len(districts) <= 65535, "district codes exceed the viewer's R*256+G encoding")
        for district in districts:
            code += 1
            district["raster_code"] = code
        indices = np.flatnonzero(continents == book["seat_index"])
        centre = centres[book["seat_index"]]
        x, y = np.zeros(len(points)), np.zeros(len(points))
        x[indices], y[indices] = local_xy(points[indices], centre)
        partition(indices, items, x, y, weights, raster, leaves)
        lat, lon = vec_to_latlon(centre)
        continent = territory(f"C{book['seat_order']:02d}", "continent", book.get("field_name") or book["title"],
                              book["book_id"], None, min(i["page_start"] for i in items),
                              max(i["page_end"] for i in items), lat=lat, lon=lon,
                              seat_order=book["seat_order"], area_fraction=float(weights[indices].sum() / total_weight))
        rows.append(continent)
        for row in children:
            row.update(lat=lat, lon=lon, area_fraction=0.0)
            if row["level"] == "district":
                pixels = leaves[row["raster_code"]]
                vector = np.sum(points[pixels] * weights[pixels, None], axis=0)
                direction = vector / np.linalg.norm(vector)
                best = pixels[np.argmax(points[pixels] @ direction)]
                row["lat"], row["lon"] = vec_to_latlon(points[best])
                row["area_fraction"] = float(weights[pixels].sum() / total_weight)
                rr, cc = pixels // width, pixels % width
                row["bbox_px"] = [int(cc.min()), int(rr.min()), int(cc.max()), int(rr.max())]
        for province in (r for r in children if r["level"] == "province"):
            kids = province["children"]
            province["area_fraction"] = sum(k["area_fraction"] for k in kids)
            if kids:
                vector = sum(latlon_to_vec(k["lat"], k["lon"]) * k["area_fraction"] for k in kids)
                province["lat"], province["lon"] = vec_to_latlon(vector)
        all_provinces = [r for r in children if r["level"] == "province"]
        hue = (book["seat_order"] - 1) / len(seated)
        for index, province in enumerate(all_provinces):
            colour = colorsys.hls_to_rgb(hue, 0.45 + 0.25 * index / max(1, len(all_provinces) - 1), 0.55)
            hex_colour = "#%02x%02x%02x" % tuple(int(c * 255) for c in colour)
            province["colour_hex"] = hex_colour
            for kid in province["children"]:
                kid["colour_hex"] = hex_colour
        continent["colour_hex"] = "#%02x%02x%02x" % tuple(int(c * 255) for c in colorsys.hls_to_rgb(hue, 0.55, 0.55))
        rows.extend(children)
    require(np.all(raster > 0), "unpainted map pixels")
    require(len({r["territory_id"] for r in rows}) == len(rows), "territory ID collision")
    for row in rows:
        row.pop("weight", None)
        row.pop("children", None)
    return {"territories": rows, "raster": raster.reshape(height, width),
            "continents": continents.reshape(height, width), "seating": seated,
            "warnings": warnings, "draft": draft, "width": width, "height": height}


def borders(image):
    edge = (image != np.roll(image, 1, axis=1)) | (image != np.roll(image, -1, axis=1))
    edge[1:] |= image[1:] != image[:-1]
    edge[:-1] |= image[:-1] != image[1:]
    return edge


def write_outputs(result, out, approved=False):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rows, raster = result["territories"], result["raster"]
    districts = [r for r in rows if r["level"] == "district"]
    lookup = {str(r["raster_code"]): r["territory_id"] for r in districts}
    np.save(out / "district_raster.npy", raster)
    encoded = np.zeros((*raster.shape, 3), dtype=np.uint8)
    encoded[..., 0], encoded[..., 1] = raster // 256, raster % 256
    Image.fromarray(encoded).save(out / "district_raster.png")
    palette = np.zeros((len(districts) + 1, 3), dtype=np.uint8)
    for district in districts:
        palette[district["raster_code"]] = [int(district["colour_hex"][i:i + 2], 16) for i in (1, 3, 5)]
    texture = palette[raster]
    texture[borders(raster)] = (40, 40, 40)
    texture[borders(result["continents"])] = (0, 0, 0)
    image = Image.fromarray(texture).resize((result["width"] * 2, result["height"] * 2), Image.Resampling.NEAREST)
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", max(10, result["width"] // 75))
    except OSError:
        font = ImageFont.load_default()
    for row in rows:
        if row["level"] == "continent":
            px = (row["lon"] + 180) / 360 * image.width
            py = (90 - row["lat"]) / 180 * image.height
            draw.multiline_text((px, py), "\n".join(textwrap.wrap(row["name"], 24)), font=font,
                                fill="white", anchor="mm", align="center", stroke_width=2, stroke_fill="black")
    image.save(out / "continents_texture.png")
    image.resize((result["width"], result["height"]), Image.Resampling.LANCZOS).save(out / "continents_texture_2k.png")
    (out / "geography.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
    (out / "districts_lookup.json").write_text(json.dumps(lookup, indent=1) + "\n")
    # Staging CSV only; the frozen registry is exported from Neo4j later.
    columns = ["territory_id", "level", "name", "part_name", "book_id", "parent", "page_start", "page_end",
               "page_count", "lat", "lon", "area_fraction", "seat_order", "raster_code", "colour_hex", "bbox_px", "toc_number"]
    with (out / "territories.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            record = row | {"bbox_px": ",".join(map(str, row["bbox_px"])) if row["bbox_px"] else ""}
            writer.writerow(record)
    (out / "seating-proposal.json").write_text(json.dumps(result["seating"], indent=1, ensure_ascii=False) + "\n")
    # Matplotlib is the BIBLE's diagnostic map renderer (headless, no service).
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axis = plt.subplots(figsize=(16, 8), dpi=128)
    axis.imshow(texture, extent=(-180, 180, -90, 90), origin="upper")
    for row in rows:
        if row["level"] == "continent":
            axis.text(row["lon"], row["lat"], "\n".join(textwrap.wrap(row["name"], 22)), fontsize=5.5,
                      ha="center", va="center", color="white", bbox={"facecolor": "black", "alpha": 0.55, "pad": 1})
    axis.set(xlabel="Longitude", ylabel="Latitude", title="Second Opinion — provisional alphabetical geography" if result["draft"] else "Second Opinion — seating proposal")
    fig.tight_layout()
    fig.savefig(out / "seating-preview.png")
    plt.close(fig)
    manifest = {"draft": result["draft"], "seating_approved": bool(approved),
                "approved_by_human": bool(approved), "database_loaded": False,
                "width": result["width"], "height": result["height"],
                "continents": sum(r["level"] == "continent" for r in rows),
                "provinces": sum(r["level"] == "province" for r in rows), "districts": len(districts),
                "district_area_sum": sum(r["area_fraction"] for r in districts),
                "warnings": result["warnings"],
                "files": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())
                          if p.is_file() and p.name != "build.json"}}
    (out / "build.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--books", type=Path, default=ROOT / "kitchen/books.json")
    parser.add_argument("--logs", type=Path, default=ROOT / "kitchen/logs")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--draft", action="store_true", help="provisional alphabetical geometry from all active books")
    parser.add_argument("--approved", action="store_true", help="record the human's approval of this exact seating/texture")
    args = parser.parse_args(argv)
    try:
        all_books = json.loads(args.books.read_text())
        books = [b for b in all_books if b.get("status") in (("candidate", "accepted", "geography-done")
                 if args.draft else ("accepted", "geography-done"))]
        require(books, "no eligible books")
        if not args.draft:
            require(all(b.get("field_name") for b in books), "accepted field names are needed for final geography")
        contents = {b["book_id"]: json.loads((args.logs / f"{b['book_id']}-toc.json").read_text()) for b in books}
        out = args.out or (args.logs / "geography-draft" if args.draft else ROOT / "data/export/geography")
        existing = out / 'build.json'
        require(not existing.exists() or json.loads(existing.read_text()).get('layout') != 'chapter-honeycomb',
                'Amendment 3.5 selected honeycomb tiles; use geography_honeycomb.py, not the old rectangle generator')
        print(f"Building one {W}x{H} raster from {len(books)} existing books; draft={args.draft}", flush=True)
        result = build(books, contents, draft=args.draft)
        manifest = write_outputs(result, out, args.approved)
        print(f"Built: {manifest['continents']} continents; {manifest['provinces']} provinces; {manifest['districts']} districts")
        print(f"District area sum: {manifest['district_area_sum']:.12f}; unpainted pixels: 0")
        print(f"Preview: {out / 'seating-preview.png'}")
        approval = "human-approved" if manifest["seating_approved"] else "not approved"
        print(f"Existing empty headings retained: {len(manifest['warnings'])}; inputs unchanged; seating {approval}; database not loaded")
        return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f"NOT BUILT: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
