import { W, H, districtCode } from './geo.js';

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
export const search = () => json('../data/search.json');
export const wording = () => json('../data/wording.json');
export const ledger = () => json('../data/ledger.json');
export const entity = slug => json(`../data/entities/${segment(slug)}.json`);
export const district = id => json(`../data/districts/${segment(id)}.json`);

export function image(url) {
  return cached(url, () => new Promise((resolve, reject) => {
    const picture = new Image();
    picture.onload = () => resolve(picture);
    picture.onerror = () => reject(new Error(`Could not load ${url}`));
    picture.src = url;
  }));
}

export async function geography() {
  return cached('world', async () => {
  const base = '../data/geography/';
  const [territories, lookup, rasterImage] = await Promise.all([
    json(base + 'geography.json'), json(base + 'districts_lookup.json'), image(base + 'district_raster.png'),
  ]);
  if (rasterImage.width !== W || rasterImage.height !== H) throw new Error('District raster has unexpected dimensions');
  const canvas = document.createElement('canvas');
  canvas.width = W; canvas.height = H;
  const context = canvas.getContext('2d', { willReadFrequently: true });
  context.drawImage(rasterImage, 0, 0);
  const raster = context.getImageData(0, 0, W, H);
  const byId = new Map(territories.map(t => [t.territory_id, t]));
  return { territories, byId, lookup, raster,
    districtAt(x, y) { return byId.get(lookup[String(districtCode(raster, x, y))]); },
    textureURL(small = false) { return base + (small ? 'continents_texture_2k.png' : 'continents_texture.png'); },
  };
  });
}
