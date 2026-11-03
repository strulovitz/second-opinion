// Part 0 section 6 (Claude Fable, 3 Nov 2026): the 2-D map is ONE generic projection,
// the same code for every point on the planet. It replaces the "flower" map.
//   Projection: Lambert azimuthal equal-area, centred on the point you were looking at
//   (the globe camera direction, or the chosen book). Areas are true everywhere, there
//   are no stretched poles, and dragging simply moves the centre: any place on the
//   globe can be the middle of the map. Same tiles as the globe (honeycomb.json), so a
//   click means the same chapter in both views.
import { radiusPx, drawSpot } from './geo.js?v=686363d-202611031550';

const LIMIT = Math.PI * 0.62;                         // how far from the centre tiles are still drawn (radians)
const neon = hex => { const n = parseInt(hex.slice(1), 16), r = n >> 16, g = (n >> 8) & 255, b = n & 255;
  const max = Math.max(r, g, b, 1); return `rgb(${Math.min(255, Math.round(r / max * 255 * 0.5 + 128 * (r === max)))},${Math.min(255, Math.round(g / max * 255 * 0.5 + 128 * (g === max)))},${Math.min(255, Math.round(b / max * 255 * 0.5 + 128 * (b === max)))})`; };

export async function createMap(canvas, world, select, hover) {
  const context = canvas.getContext('2d');
  let width = 1, height = 1, scale = 1, fitScale = 1;
  let centre = [1, 0, 0], east = [0, 0, 1], north = [0, 1, 0];
  let spots = [], placed = [], highlighted = null, hoverTile = null, start = null, gesture = false, viewBook = null;
  const pointers = new Map();
  const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const unit = v => { const l = Math.hypot(...v) || 1; return [v[0] / l, v[1] / l, v[2] / l]; };

  // Book borders: tile edges whose neighbour belongs to another book (computed once).
  const borders = [];
  for (const t of world.tiles) {
    for (const n of t.neighbors) {
      const o = world.tiles[n]; if (o.index < t.index || o.book === t.book) continue;
      const shared = t.vertices.filter(v => o.vertices.includes(v));
      if (shared.length === 2) borders.push(shared);
    }
  }
  const nameTiles = world.tiles.filter(t => t.kind === 'name');

  function setCentre(p) {
    centre = unit(p);
    const up = Math.abs(centre[1]) < 0.95 ? [0, 1, 0] : [1, 0, 0];
    east = unit(cross(up, centre)); north = unit(cross(centre, east));
    const tile = world.tileAt(centre);
    viewBook = tile && tile.book >= 0 ? world.books[tile.book].book_id : viewBook;
  }
  // Lambert azimuthal equal-area, forward and inverse (unit sphere, map units, centre = 0,0).
  function project(p) {
    const c = dot(centre, p); if (c < -0.999) return null;
    const k = Math.sqrt(2 / (1 + c));
    return [k * dot(p, east), k * dot(p, north), Math.acos(Math.max(-1, Math.min(1, c)))];
  }
  function unproject(x, y) {
    const rho = Math.hypot(x, y); if (rho > 2) return null;
    const c = 2 * Math.asin(rho / 2), s = Math.sin(c), cc = Math.cos(c);
    const ex = rho ? x / rho : 0, ey = rho ? y / rho : 0;
    return unit([0, 1, 2].map(i => cc * centre[i] + s * (ex * east[i] + ey * north[i])));
  }
  const sx = x => width / 2 + x * scale, sy = y => height / 2 - y * scale;
  const screenToSphere = (X, Y) => unproject((X - width / 2) / scale, (height / 2 - Y) / scale);

  function tilePath(path, t) {
    const pts = [];
    for (const v of t.vertices) { const q = project(world.vertices[v]); if (!q || q[2] > LIMIT + 0.2) return false; pts.push(q); }
    path.moveTo(sx(pts[0][0]), sy(pts[0][1]));
    for (let i = 1; i < pts.length; i++) path.lineTo(sx(pts[i][0]), sy(pts[i][1]));
    path.closePath(); return true;
  }
  function draw() {
    if (canvas.hidden) return;
    context.clearRect(0, 0, width, height);
    // the planet's disc
    context.fillStyle = 'rgba(12,18,36,.9)'; context.beginPath(); context.arc(width / 2, height / 2, 2 * scale, 0, Math.PI * 2); context.fill();
    const byColour = new Map(), visible = [];
    for (const t of world.tiles) {
      const c = dot(centre, t.centre); if (c < Math.cos(LIMIT)) continue;
      visible.push(t);
      const colour = t.kind === 'pole' ? '#16304a' : t.book >= 0 ? world.books[t.book].colour_hex : '#333333';
      if (!byColour.has(colour)) byColour.set(colour, new Path2D());
      tilePath(byColour.get(colour), t);
    }
    for (const [colour, path] of byColour) { context.fillStyle = colour; context.fill(path); }
    if (scale > 120) {                                   // tile grout when zoomed in
      const grout = new Path2D(); for (const t of visible) tilePath(grout, t);
      context.strokeStyle = 'rgba(10,14,28,.35)'; context.lineWidth = 1; context.stroke(grout);
    }
    const edge = new Path2D();
    for (const [a, b] of borders) {
      const p = project(world.vertices[a]), q = project(world.vertices[b]);
      if (!p || !q || p[2] > LIMIT || q[2] > LIMIT) continue;
      edge.moveTo(sx(p[0]), sy(p[1])); edge.lineTo(sx(q[0]), sy(q[1]));
    }
    context.strokeStyle = '#fbf6e6'; context.lineWidth = Math.max(1, Math.min(3, scale / 250)); context.lineCap = 'round'; context.stroke(edge);
    // lit chapters: the whole tile glows in its book's neon colour (the 2-D twin of the 3-D columns)
    const litTiles = new Map();
    for (const s of spots) if (s.lit) { const t = world.tileOf.get(s.district_id); if (t) litTiles.set(t.index, t); }
    for (const t of litTiles.values()) {
      const p = new Path2D(); if (!tilePath(p, t)) continue;
      context.fillStyle = neon(world.books[t.book]?.colour_hex || '#ffffff'); context.fill(p);
      context.strokeStyle = '#ffffff'; context.lineWidth = 1.5; context.stroke(p);
    }
    if (hoverTile) { const p = new Path2D(); if (tilePath(p, hoverTile)) { context.fillStyle = 'rgba(255,255,255,.45)'; context.fill(p); } }
    if (scale > 900) {                                   // chapter names when zoomed in
      context.font = '11px system-ui, sans-serif'; context.textAlign = 'center'; context.textBaseline = 'middle'; context.fillStyle = 'rgba(15,18,30,.85)';
      for (const t of visible) {
        if (!t.territory) continue; const q = project(t.centre); const name = t.territory.name;
        context.fillText(name.length > 14 ? `${name.slice(0, 13)}…` : name, sx(q[0]), sy(q[1]), scale * 0.03);
      }
    }
    context.textAlign = 'center'; context.textBaseline = 'middle';
    for (const t of nameTiles) {
      const q = project(t.centre); if (!q || q[2] > LIMIT * 0.85) continue;
      const book = world.books[t.book]; if (!book) continue;
      const size = 13; context.font = `600 ${size}px system-ui, sans-serif`;
      const w = context.measureText(book.name).width + 12, X = sx(q[0]), Y = sy(q[1]);
      context.fillStyle = 'rgba(8,12,24,.72)'; context.beginPath(); context.roundRect(X - w / 2, Y - size * 0.8, w, size * 1.6, size * 0.8); context.fill();
      context.fillStyle = '#ffffff'; context.fillText(book.name, X, Y + 1);
    }
    placed = [];
    for (const spot of spots) {
      const t = world.tileOf.get(spot.district_id); if (!t) continue;
      const q = project(t.centre); if (!q || q[2] > LIMIT) continue;
      const cx = sx(q[0]) + spot.offset[0], cy = sy(q[1]) + spot.offset[1];
      if (cx < -40 || cy < -40 || cx > width + 40 || cy > height + 40) continue;
      drawSpot(context, spot, cx, cy, highlighted === spot || highlighted === spot.other_slug);
      placed.push({ x: cx, y: cy, spot, radius: spot.lit ? 8 : radiusPx(spot.f) + 6 });
    }
  }
  function fit() { scale = fitScale; draw(); }
  function resize() {
    const rect = canvas.getBoundingClientRect(); if (!rect.width || !rect.height) return;
    const ratio = window.devicePixelRatio || 1, atFit = scale === fitScale;
    width = rect.width; height = rect.height;
    canvas.width = Math.round(width * ratio); canvas.height = Math.round(height * ratio);
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    fitScale = Math.min(width, height) / 2 / 1.72;     // the drawn disc (about 112 degrees) fills the view
    if (atFit) scale = fitScale; else scale = Math.max(fitScale * 0.8, Math.min(fitScale * 40, scale));
    draw();
  }
  const point = event => { const r = canvas.getBoundingClientRect(); return { x: event.clientX - r.left, y: event.clientY - r.top }; };
  function hit(event) {
    const { x, y } = point(event);
    let best = null, bd = Infinity;
    for (const item of placed) { const d = Math.hypot(item.x - x, item.y - y); if (d <= item.radius && d < bd) { bd = d; best = item.spot; } }
    if (best) return { value: best, tile: world.tileOf.get(best.district_id) };
    const p = screenToSphere(x, y); if (!p || Math.acos(Math.max(-1, Math.min(1, dot(p, centre)))) > LIMIT) return { value: null, tile: null };
    const tile = world.tileAt(p);
    if (!tile || tile.kind === 'pole') return { value: null, tile: null };
    return { value: world.territoryOfTile(tile), tile };
  }
  function zoom(factor, x = width / 2, y = height / 2) {
    const before = screenToSphere(x, y);
    scale = Math.max(fitScale * 0.8, Math.min(fitScale * 40, scale * factor));
    if (before) {                                        // keep the point under the cursor fixed
      const q = project(before); if (q) panBy(sx(q[0]) - x, sy(q[1]) - y);
    }
    draw();
  }
  function panBy(dx, dy) {                              // move the centre so the map slides by (dx, dy) pixels
    const p = screenToSphere(width / 2 + dx, height / 2 + dy); if (p) setCentre(p);
  }
  canvas.addEventListener('wheel', event => { event.preventDefault(); zoom(event.deltaY < 0 ? 1.2 : 1 / 1.2, ...Object.values(point(event))); }, { passive: false });
  canvas.addEventListener('pointerdown', event => {
    canvas.setPointerCapture(event.pointerId); pointers.set(event.pointerId, point(event));
    start = { ...point(event), moved: false, pinch: pointers.size === 2 ? [...pointers.values()] : null }; gesture = false;
  });
  canvas.addEventListener('pointermove', event => {
    const p = point(event);
    if (!pointers.has(event.pointerId)) {
      const h = hit(event); const tile = h.value && !h.value.other_slug ? h.tile : null;
      if (tile !== hoverTile) { hoverTile = tile; draw(); }
      hover(h.value, event); return;
    }
    const last = pointers.get(event.pointerId); pointers.set(event.pointerId, p);
    if (pointers.size === 2) {
      const [a, b] = [...pointers.values()]; const d = Math.hypot(a.x - b.x, a.y - b.y);
      if (start?.pinch) { const d0 = Math.hypot(start.pinch[0].x - start.pinch[1].x, start.pinch[0].y - start.pinch[1].y); if (d0) zoom(d / d0, (a.x + b.x) / 2, (a.y + b.y) / 2); start.pinch = [a, b]; }
      gesture = true; return;
    }
    if (Math.hypot(p.x - start.x, p.y - start.y) > 3) start.moved = true;
    if (start.moved) { panBy(-(p.x - last.x), -(p.y - last.y)); draw(); }
  });
  function release(event, cancelled = false) {
    pointers.delete(event.pointerId);
    if (!cancelled && start && !start.moved && !gesture && pointers.size === 0) { const h = hit(event); if (h.value) select(h.value, event); }
    if (pointers.size === 0) { start = null; gesture = false; }
  }
  canvas.addEventListener('pointerup', release); canvas.addEventListener('pointercancel', e => release(e, true));
  canvas.addEventListener('pointerleave', () => { if (!pointers.size) { hoverTile = null; highlighted = null; draw(); hover(null); } });

  setCentre(world.tiles.find(t => t.kind === 'name')?.centre || [1, 0, 0]);
  return {
    resize, zoom, fit,
    get viewBook() { return viewBook; },
    // Centre the map on a direction (the globe camera) or on a book; same routine for any point.
    async setView(bookOrDirection) {
      if (Array.isArray(bookOrDirection)) setCentre(bookOrDirection);
      else { const t = nameTiles.find(t => world.books[t.book]?.book_id === bookOrDirection); if (t) setCentre(t.centre); }
      resize(); fit();
    },
    render(entity, nextSpots = []) { spots = nextSpots; highlighted = null; draw(); },
    highlight(slug) { highlighted = slug; draw(); },
    screenOf(id) { const t = world.tileOf.get(id), r = canvas.getBoundingClientRect(); const q = t && project(t.centre); return q ? { x: r.left + sx(q[0]), y: r.top + sy(q[1]) } : null; },
    firstSpot() { const p = placed.find(item => item.spot.other_slug), r = canvas.getBoundingClientRect(); return p ? { x: r.left + p.x, y: r.top + p.y, other_slug: p.spot.other_slug } : null; },
  };
}
