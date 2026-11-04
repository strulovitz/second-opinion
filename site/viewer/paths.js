// BIBLE Part 0 sections 12.5 and 13: the golden connections drawn as curved ARROWS.
// Only two inputs start a walk:
//   BLUE walk from a SYMPTOM:     symptom -> disease (that presents with it) -> treatment,
//                                 plus the causes under that disease (cause -> disease)
//   YELLOW walk from a TREATMENT: treatment -> what it causes -> that thing's symptoms,
//                                 and on through the prescription cascade (a harm that is
//                                 treated by another drug, which harms again ...)
// The colour belongs to the WALK, not to the stored fact. Grey = mistaken for, green =
// same chemical, shown with any walk. Thickness = F-scale, dashed = frequency not stated,
// red glow = the source's severity words. The website only DISPLAYS golden.json.
import { json } from './data.js?v=8dfde9d-202611041435';

export const WALK_COLOUR = { blue: '#3d8bff', yellow: '#ffc21a', grey: '#a0a0a0', green: '#3fd16b', red: '#ff3b30' };
const STORED_COLOUR = { PRESENTS_WITH: 'blue', TREATED_BY: 'blue', HARMS: 'yellow', LEADS_TO: 'yellow', MISTAKEN_FOR: 'grey', SAME_CHEMICAL: 'green' };
export const VERB = { PRESENTS_WITH: 'shows as', TREATED_BY: 'is treated by', HARMS: 'can cause', LEADS_TO: 'leads to', MISTAKEN_FOR: 'is mistaken for', SAME_CHEMICAL: 'is the same chemical as' };
let golden = { nodes: {}, connections: [] };

export async function loadGolden() {
  try { golden = await json('../data/golden.json'); } catch (error) { if (!error.missing) console.error(error); }
  return golden;
}
export const goldenNode = slug => golden.nodes[slug] || null;

export function walkFor(slug) {
  const g = golden, start = g.nodes[slug];
  if (!start) return null;
  const out = (s, rel) => g.connections.filter(c => c.from === s && c.rel === rel);
  const into = (s, rel) => g.connections.filter(c => c.to === s && c.rel === rel);
  const arrows = [], seen = new Set(), steps = new Map([[slug, 0]]);
  const add = (conn, a, b, colour, step) => {
    const key = `${conn.id}:${a}`; if (seen.has(key)) return false;
    seen.add(key); arrows.push({ conn, from: a, to: b, colour, step });
    if (!steps.has(a)) steps.set(a, step - 1);
    if (!steps.has(b)) steps.set(b, step);
    return true;
  };
  const kind = start.group === 'symptoms-and-signs' ? 'blue' : start.group === 'treatments-and-drugs' ? 'yellow' : 'neutral';
  if (kind === 'blue') {
    for (const c of into(slug, 'PRESENTS_WITH')) {
      add(c, slug, c.from, 'blue', 1);
      for (const t of out(c.from, 'TREATED_BY')) add(t, c.from, t.to, 'blue', 2);
      for (const k of into(c.from, 'LEADS_TO')) add(k, k.from, c.from, 'blue', 2);
    }
    for (const c of out(slug, 'TREATED_BY')) add(c, slug, c.to, 'blue', 1);
  } else if (kind === 'yellow') {
    const frontier = [[slug, 0]];
    while (frontier.length) {
      const [s, d] = frontier.shift(); if (d >= 8) continue;
      const next = g.nodes[s]?.group === 'treatments-and-drugs' ? out(s, 'HARMS')
        : [...out(s, 'LEADS_TO'), ...out(s, 'PRESENTS_WITH'), ...(d > 0 ? out(s, 'TREATED_BY') : [])];
      for (const c of next) if (add(c, s, c.to, 'yellow', d + 1)) frontier.push([c.to, d + 1]);
    }
    for (const c of into(slug, 'TREATED_BY')) add(c, c.from, slug, 'blue', 1);   // what it is used for
  } else {
    for (const c of g.connections) if (c.from === slug || c.to === slug) {
      if (c.rel === 'PRESENTS_WITH' || c.rel === 'HARMS' || c.rel === 'TREATED_BY' || c.rel === 'LEADS_TO') add(c, c.from, c.to, STORED_COLOUR[c.rel], 1);
    }
  }
  for (const c of g.connections) {
    if (c.rel !== 'SAME_CHEMICAL' && c.rel !== 'MISTAKEN_FOR') continue;
    const step = steps.get(c.from) ?? steps.get(c.to);
    if (step !== undefined) add(c, c.from, c.to, STORED_COLOUR[c.rel], step + 1);
  }
  const nodes = [...steps.keys()].map(s => ({ ...g.nodes[s], slug: s, step: steps.get(s) })).filter(n => n.name);
  return { kind, start: slug, arrows, nodes };
}

// The chapters that discuss the diseases on a walk light up faintly (BIBLE 13.2).
export async function litDistricts(walk, entityOf) {
  const ids = new Set();
  for (const n of walk.nodes.filter(n => n.place === 'surface').slice(0, 12)) {
    try { for (const s of (await entityOf(n.slug)).lit_spots || []) ids.add(s.district_id); } catch { /* not exported */ }
  }
  return ids;
}

// Where each node sits: its anchor tile, nudged apart when several share one tile.
export function anchorsOf(walk, world) {
  const count = new Map(), place = new Map();
  for (const n of walk.nodes) {
    const tile = world.tileOf.get(n.anchor); if (!tile) continue;
    const k = count.get(tile.index) || 0; count.set(tile.index, k + 1);
    place.set(n.slug, { tile, k });
  }
  return place;
}

export const width2d = f => (f ? 1.5 + 0.9 * f : 2.5);
export function fade(step) { return Math.max(0.35, 1 - 0.13 * Math.max(0, step - 1)); }

// Cartoon marks: a cloud for a symptom, a satellite for a treatment, a hexagon for a
// disease, a dark diamond for a cause under the ground. Shared by the 2-D map and 3-D sprites.
export function drawIcon(c, node, x, y, s, active = false) {
  c.save(); c.translate(x, y); c.lineWidth = Math.max(1.5, s / 8);
  const place = node.place;
  if (place === 'air') {
    c.fillStyle = '#f4f8ff'; c.strokeStyle = '#3d8bff';
    c.beginPath(); c.arc(-s * 0.35, s * 0.1, s * 0.32, 0, 7); c.arc(0, -s * 0.12, s * 0.42, 0, 7); c.arc(s * 0.38, s * 0.1, s * 0.3, 0, 7);
    c.rect(-s * 0.35, s * 0.1, s * 0.73, s * 0.3); c.fill(); c.stroke();
  } else if (place === 'orbit') {
    c.fillStyle = '#d9dde6'; c.strokeStyle = '#ffc21a'; c.fillRect(-s * 0.2, -s * 0.2, s * 0.4, s * 0.4); c.strokeRect(-s * 0.2, -s * 0.2, s * 0.4, s * 0.4);
    c.fillStyle = '#2f5fbf'; c.fillRect(-s * 0.75, -s * 0.13, s * 0.45, s * 0.26); c.fillRect(s * 0.3, -s * 0.13, s * 0.45, s * 0.26);
    c.strokeRect(-s * 0.75, -s * 0.13, s * 0.45, s * 0.26); c.strokeRect(s * 0.3, -s * 0.13, s * 0.45, s * 0.26);
  } else if (place === 'underground') {
    c.fillStyle = '#4a2a18'; c.strokeStyle = '#ff7a3a';
    c.beginPath(); c.moveTo(0, -s * 0.5); c.lineTo(s * 0.45, 0); c.lineTo(0, s * 0.5); c.lineTo(-s * 0.45, 0); c.closePath(); c.fill(); c.stroke();
  } else {
    c.fillStyle = '#ff7a50'; c.strokeStyle = '#fff4e0';
    c.beginPath(); for (let i = 0; i < 6; i++) { const a = Math.PI / 6 + i * Math.PI / 3; c.lineTo(Math.cos(a) * s * 0.5, Math.sin(a) * s * 0.5); } c.closePath(); c.fill(); c.stroke();
  }
  if (active) { c.strokeStyle = '#ffffff'; c.lineWidth = 2; c.beginPath(); c.arc(0, 0, s * 0.85, 0, 7); c.stroke(); }
  c.restore();
}
export function drawLabel(c, name, x, y, size = 12) {
  c.save(); c.font = `600 ${size}px system-ui, sans-serif`; c.textAlign = 'center'; c.textBaseline = 'middle';
  const label = name.length > 34 ? `${name.slice(0, 33)}…` : name, w = c.measureText(label).width + 10;
  c.fillStyle = 'rgba(8,12,24,.78)'; c.beginPath(); c.roundRect(x - w / 2, y - size * 0.8, w, size * 1.6, size * 0.6); c.fill();
  c.fillStyle = '#ffffff'; c.fillText(label, x, y + 1); c.restore();
}

// 2-D: quadratic curves with arrowheads. pos(slug) -> [x, y] in screen pixels or null.
// Returns the hit list: nodes (centre, radius) and arrows (sample points).
export function drawWalk2d(c, walk, pos, hovered) {
  const hits = { nodes: [], arrows: [] }, pair = new Map();
  for (const a of walk.arrows) {
    const p = pos(a.from), q = pos(a.to); if (!p || !q) continue;
    const key = [a.from, a.to].sort().join('|'), k = pair.get(key) || 0; pair.set(key, k + 1);
    const dx = q[0] - p[0], dy = q[1] - p[1], len = Math.hypot(dx, dy) || 1, ux = dx / len, uy = dy / len;
    const s = [p[0] + ux * 16, p[1] + uy * 16], e = [q[0] - ux * 18, q[1] - uy * 18];
    const bend = (0.22 + 0.14 * k) * len * (k % 2 ? -1 : 1);
    const m = [(s[0] + e[0]) / 2 - uy * bend, (s[1] + e[1]) / 2 + ux * bend];
    const colour = WALK_COLOUR[a.colour], w = width2d(a.conn.f_scale), alpha = fade(a.step);
    c.save(); c.globalAlpha = alpha; c.lineCap = 'round';
    if (a.conn.severity) { c.shadowColor = WALK_COLOUR.red; c.shadowBlur = 14; }
    if (a === hovered) { c.shadowColor = '#ffffff'; c.shadowBlur = 10; }
    c.strokeStyle = colour; c.lineWidth = w; c.setLineDash(a.conn.f_scale ? [] : [8, 6]);
    c.beginPath(); c.moveTo(...s); c.quadraticCurveTo(...m, ...e); c.stroke(); c.setLineDash([]);
    const tx = e[0] - m[0], ty = e[1] - m[1], tl = Math.hypot(tx, ty) || 1, hx = tx / tl, hy = ty / tl, h = 9 + w * 1.6;
    const heads = a.conn.rel === 'SAME_CHEMICAL' || a.conn.rel === 'MISTAKEN_FOR' ? [[e, hx, hy], [s, (s[0] - m[0]) / Math.hypot(s[0] - m[0], s[1] - m[1]), (s[1] - m[1]) / Math.hypot(s[0] - m[0], s[1] - m[1])]] : [[e, hx, hy]];
    c.fillStyle = colour;
    for (const [pt, ax, ay] of heads) {
      c.beginPath(); c.moveTo(pt[0] + ax * 2, pt[1] + ay * 2);
      c.lineTo(pt[0] - ax * h - ay * h * 0.55, pt[1] - ay * h + ax * h * 0.55); c.lineTo(pt[0] - ax * h + ay * h * 0.55, pt[1] - ay * h - ax * h * 0.55); c.closePath(); c.fill();
    }
    c.restore();
    const samples = [];
    for (let i = 0; i <= 16; i++) { const t = i / 16, u = 1 - t; samples.push([u * u * s[0] + 2 * u * t * m[0] + t * t * e[0], u * u * s[1] + 2 * u * t * m[1] + t * t * e[1]]); }
    hits.arrows.push({ arrow: a, samples, width: w });
  }
  for (const n of walk.nodes) {
    const p = pos(n.slug); if (!p) continue;
    c.save(); c.globalAlpha = fade(n.step); drawIcon(c, n, p[0], p[1], n.slug === walk.start ? 30 : 24, n.slug === walk.start); c.restore();
    drawLabel(c, n.name, p[0], p[1] + 24);
    hits.nodes.push({ node: n, x: p[0], y: p[1], r: 16 });
  }
  return hits;
}
export function hitWalk2d(hits, x, y) {
  for (const h of hits.nodes) if (Math.hypot(h.x - x, h.y - y) <= h.r) return nodeValue(h.node);
  let best = null, bd = Infinity;
  for (const h of hits.arrows) for (const [sx, sy] of h.samples) { const d = Math.hypot(sx - x, sy - y); if (d < bd && d <= h.width + 7) { bd = d; best = h.arrow; } }
  return best ? arrowValue(best) : null;
}
// Values handed to app.js: other_slug makes the existing click/touch logic open that thing.
export const nodeValue = node => ({ walkNode: node, other_slug: node.slug });
export const arrowValue = arrow => ({ walkArrow: arrow, other_slug: arrow.to });
