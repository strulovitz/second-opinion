// Loading and caching of every data file the viewer reads (BIBLE Part 7 section 6.1,
// Amendment 3.6 / Opus 5.5 addition: honeycomb.json format goldberg-honeycomb-2 and
// one flower map per book). All URLs are relative so the site works from any folder.
const cache = new Map();
function cached(key, load) {
  if (!cache.has(key)) cache.set(key, load().catch(error => { cache.delete(key); console.error(error); throw error; }));
  return cache.get(key);
}
export function json(file) {
  return cached(file, async () => {
    const response = await fetch(file);
    if (!response.ok) {
      const error = new Error(`${file} (HTTP ${response.status})`);
      error.missing = response.status === 404; throw error;
    }
    try { return await response.json(); } catch { throw new Error(`Invalid JSON: ${file}`); }
  });
}
function segment(value) {
  if (!/^[a-zA-Z0-9._-]+$/.test(value) || value === '.' || value === '..') throw new Error('Invalid data identifier');
  return encodeURIComponent(value);
}

// DEMO MODE. Invented placeholder entities (site/data/demo/demo.json, written by
// kitchen/make_demo.py) are served only while the demo switch is on, and only for
// slugs starting with "demo-". They are never in Neo4j and never in the real exports.
let demoOn = false;
export function setDemo(on) { demoOn = !!on; }
export const isDemo = () => demoOn;
export const demo = () => json('../data/demo/demo.json');

export async function search() {
  let rows = [];
  try { rows = await json('../data/search.json'); } catch (error) { if (!demoOn) throw error; }
  return demoOn ? [...(await demo()).search, ...rows] : rows;
}
export const wording = () => json('../data/wording.json');
export async function entity(slug) {
  if (slug.startsWith('demo-')) {
    const found = demoOn && (await demo()).entities[slug];
    if (!found) { const error = new Error(`demo entity ${slug} (switch the demo on)`); error.missing = true; throw error; }
    return found;
  }
  return json(`../data/entities/${segment(slug)}.json`);
}
export const district = id => json(`../data/districts/${segment(id)}.json`);
export const flowers = book => json(`../data/geography/flowers/${segment(book)}.json`);

// Python stores (x, y, z) with z = north; Three.js is y-up with z = -east.
const toThree = p => [p[0], p[2], -p[1]];

export async function geography() {
  return cached('world', async () => {
    const base = '../data/geography/';
    const [territories, honeycomb] = await Promise.all([json(base + 'geography.json'), json(base + 'honeycomb.json')]);
    if (honeycomb.format !== 'goldberg-honeycomb-2') throw new Error('honeycomb.json is not the Goldberg format (Amendment 3.6)');
    const byId = new Map(territories.map(t => [t.territory_id, t]));
    const books = territories.filter(t => t.level === 'continent');
    const bookIndex = new Map(books.map((b, i) => [b.book_id, i]));
    const districts = territories.filter(t => t.level === 'district');
    const districtIndex = new Map(districts.map((d, i) => [d.territory_id, i]));
    const vertices = honeycomb.vertices_xyz.map(toThree);
    const tiles = honeycomb.tiles.map((t, index) => ({ ...t, index, centre: toThree(t.centre_xyz),
      territory: t.territory_id ? byId.get(t.territory_id) : null, book: t.book_id ? bookIndex.get(t.book_id) : -1 }));
    const tileOf = new Map(tiles.filter(t => t.territory_id).map(t => [t.territory_id, t]));
    // Exact picking: nearest centres first, then the tile's own spherical polygon test.
    function tileAt(p) {
      const near = [];
      for (const t of tiles) {
        const d = t.centre[0] * p[0] + t.centre[1] * p[1] + t.centre[2] * p[2];
        if (near.length < 4 || d > near[3][0]) { near.push([d, t]); near.sort((a, b) => b[0] - a[0]); near.length = Math.min(near.length, 4); }
      }
      for (const [, t] of near) {
        let inside = true;
        for (let i = 0; i < t.vertices.length && inside; i++) {
          const a = vertices[t.vertices[i]], b = vertices[t.vertices[(i + 1) % t.vertices.length]];
          const n = [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
          inside = n[0] * p[0] + n[1] * p[1] + n[2] * p[2] >= -1e-9;
        }
        if (inside) return t;
      }
      return near[0]?.[1] || null;
    }
    return { territories, byId, books, bookIndex, districts, districtIndex, vertices, tiles, tileOf, tileAt,
      statistics: honeycomb.statistics, territoryOfTile: t => t?.kind === 'name' ? books[t.book] : t?.territory || null };
  });
}
