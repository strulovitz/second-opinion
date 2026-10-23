import { W, H, districtCode } from './geo.js';

async function json(file) {
  const response = await fetch(file);
  if (!response.ok) throw new Error(`Could not load ${file} (HTTP ${response.status})`);
  return response.json();
}

export function image(url) {
  return new Promise((resolve, reject) => {
    const picture = new Image();
    picture.onload = () => resolve(picture);
    picture.onerror = () => reject(new Error(`Could not load ${url}`));
    picture.src = url;
  });
}

export async function geography() {
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
}
