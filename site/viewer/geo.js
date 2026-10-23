export const W = 2048, H = 1024;
export const COLOUR = { blue: '#1f5fbf', yellow: '#e0a800', grey: '#6b6b6b', red: '#b3261e', lit: '#ffffff' };
export const RELATION_COLOUR = { PRESENTS_WITH: 'blue', TREATED_BY: 'blue', HARMS: 'yellow', LEADS_TO: 'yellow', MISTAKEN_FOR: 'grey' };

export function radiusPx(f) { return 3 + 2.2 * (f === 0 ? 3 : f); }
export function sunflower(i, n, base) {
  if (n <= 1) return [0, 0];
  const a = i * 2.39996323, r = base * 1.3 * Math.sqrt(i + 1);
  return [r * Math.cos(a), r * Math.sin(a)];
}
export function normalize(value) {
  return String(value ?? '').normalize('NFKD').replace(/\p{M}/gu, '').toLocaleLowerCase();
}
export function parseRoute(hash) {
  try {
    if (!hash.startsWith('#/')) return { route: 'globe' };
    const parts = hash.replace(/^#/, '').split('/');
    if (parts.length === 2 && parts[1] === 'globe') return { route: 'globe' };
    if (parts.length === 3 && parts[1] === 'district' && parts[2]) return { route: 'district', territoryId: decodeURIComponent(parts[2]) };
    if ((parts.length === 3 || (parts.length === 4 && parts[3] === '3d')) && parts[1] === 'map' && parts[2]) {
      return { route: parts.length === 4 ? 'map3d' : 'map', slug: decodeURIComponent(parts[2]) };
    }
  } catch { /* Malformed URI: the caller replaces it with the home route. */ }
  return { route: 'globe' };
}

export function spotsFor(entity, geography) {
  const spots = [], occupied = new Set();
  for (const edge of entity?.edges || []) {
    const districts = new Map();
    for (const statement of edge.statements || []) {
      if (!districts.has(statement.district_id)) districts.set(statement.district_id, []);
      districts.get(statement.district_id).push(statement);
    }
    for (const [id, statements] of districts) {
      const territory = geography.byId.get(id);
      if (!territory || !RELATION_COLOUR[edge.relation]) continue;
      const top = [...statements].sort((a, b) => (b.f_scale ?? 0) - (a.f_scale ?? 0))[0];
      const f = Math.max(...statements.map(s => s.f_scale ?? 0));
      spots.push({ ...edge, district_id: id, lon: territory.lon, lat: territory.lat,
        colour: RELATION_COLOUR[edge.relation], f, dashed: f === 0,
        severity: statements.some(s => s.severity), statement: top, count: statements.length });
      occupied.add(id);
    }
  }
  for (const lit of entity?.lit_spots || []) {
    const territory = geography.byId.get(lit.district_id);
    if (territory && !occupied.has(lit.district_id)) {
      spots.push({ ...lit, lon: territory.lon, lat: territory.lat, lit: true });
    }
  }
  const grouped = new Map();
  for (const spot of spots) {
    if (!grouped.has(spot.district_id)) grouped.set(spot.district_id, []);
    grouped.get(spot.district_id).push(spot);
  }
  const order = { blue: 0, yellow: 1, grey: 2 };
  for (const group of grouped.values()) {
    group.sort((a, b) => (order[a.colour] ?? 3) - (order[b.colour] ?? 3) || (b.f ?? 0) - (a.f ?? 0) || String(a.other_slug).localeCompare(String(b.other_slug)));
    const base = Math.max(...group.map(s => s.lit ? 3 : radiusPx(s.f))) * (spots.length > 4000 ? 0.7 : 1);
    group.forEach((s, i) => { s.offset = sunflower(i, group.length, base); });
  }
  return [...grouped.values()].flat().sort((a, b) => Number(!!a.severity) - Number(!!b.severity));
}

// Shared drawing rules for 2-D circles and generated Three.js sprite textures.
export function drawSpot(context, spot, x, y, highlighted = false) {
  const r = spot.lit ? 3 : radiusPx(spot.f);
  context.save();
  context.beginPath(); context.arc(x, y, r, 0, Math.PI * 2);
  context.strokeStyle = COLOUR[spot.colour] || COLOUR.lit;
  context.lineWidth = spot.lit ? 1.5 : 2;
  if (!spot.lit) {
    context.globalAlpha = spot.dashed ? 0.35 : 0.92;
    context.fillStyle = COLOUR[spot.colour]; context.fill(); context.globalAlpha = 1;
    if (spot.dashed) context.setLineDash([4, 3]);
  }
  if (spot.lit || spot.dashed) context.stroke();
  context.setLineDash([]);
  for (const [enabled, offset, colour, width] of [[spot.severity, 2, COLOUR.red, 3], [highlighted, 4, '#ffffff', 1.5]]) {
    if (!enabled) continue;
    context.beginPath(); context.arc(x, y, r + offset, 0, Math.PI * 2);
    context.strokeStyle = colour;
    context.lineWidth = width; context.stroke();
  }
  context.restore();
}

export function lonLatToPixel(lon, lat) {
  return [(lon + 180) / 360 * W, (90 - lat) / 180 * H];
}

export function pixelToLonLat(x, y) {
  return [x / W * 360 - 180, 90 - y / H * 180];
}

export function districtCode(imageData, px, py) {
  const x = Math.max(0, Math.min(W - 1, Math.floor(px)));
  const y = Math.max(0, Math.min(H - 1, Math.floor(py)));
  const k = (y * W + x) * 4;
  return imageData.data[k] * 256 + imageData.data[k + 1];
}

export function lonLatToXYZ(lon, lat, radius = 1) {
  const la = lat * Math.PI / 180, lo = lon * Math.PI / 180;
  return [radius * Math.cos(la) * Math.cos(lo), radius * Math.sin(la), -radius * Math.cos(la) * Math.sin(lo)];
}
