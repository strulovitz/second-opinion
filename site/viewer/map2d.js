// Opus 5.5 rewrite of the 2-D map: Nir's FLOWER MAP (24 Oct 2026; replaces the
// equirectangular texture of BIBLE Part 7 section 7). Each book is one round blob of
// perfect hexagons; the book you were looking at sits in the middle with its globe
// neighbours as petals; flowers never touch. The layouts are computed once in the
// kitchen (kitchen/flower_map.py) and read from site/data/geography/flowers/<BOOK>.json,
// so the same book always gives exactly the same picture.
import { radiusPx, drawSpot } from './geo.js';
import * as data from './data.js';

const SQRT3 = Math.sqrt(3);
const HEX = Array.from({ length: 6 }, (_, i) => { const a = Math.PI / 180 * (60 * i + 30); return [Math.cos(a) / SQRT3, Math.sin(a) / SQRT3]; });

export async function createMap(canvas, world, select, hover) {
  const context = canvas.getContext('2d');
  let width = 1, height = 1, fitScale = 1, scale = 1, tx = 0, ty = 0;
  let layout = null, spots = [], placed = [], highlighted = null, hoverDistrict = null, start = null, gesture = false;
  let byColour = new Map(), borders = [], grid = new Map();
  const pointers = new Map();
  const xy = i => layout.xy[i];

  function prepare(next) {
    layout = next; byColour = new Map(); borders = []; grid = new Map();
    const key = (x, y) => `${Math.round(x * 20)},${Math.round(y * 20)}`, at = new Map();
    world.districts.forEach((d, i) => { const [x, y] = xy(i); at.set(key(x, y), d.book_id); });
    world.districts.forEach((d, i) => {
      const [x, y] = xy(i);
      if (!byColour.has(d.colour_hex)) byColour.set(d.colour_hex, []);
      byColour.get(d.colour_hex).push(i);
      const cell = `${Math.floor(x)},${Math.floor(y)}`;
      if (!grid.has(cell)) grid.set(cell, []); grid.get(cell).push(i);
      for (let k = 0; k < 6; k++) {
        const a = Math.PI / 3 * k, nx = x + Math.cos(a), ny = y + Math.sin(a);
        if (at.get(key(nx, ny)) !== d.book_id) borders.push([x, y, a]);
      }
    });
  }
  const sx = x => tx + x * scale, sy = y => ty - y * scale;   // layout y points up
  function hexPath(path, x, y, shrink = 1) {
    const cx = sx(x), cy = sy(y);
    path.moveTo(cx + HEX[0][0] * scale * shrink, cy - HEX[0][1] * scale * shrink);
    for (let k = 1; k < 6; k++) path.lineTo(cx + HEX[k][0] * scale * shrink, cy - HEX[k][1] * scale * shrink);
    path.closePath();
  }
  function draw() {
    if (canvas.hidden) return;
    context.clearRect(0, 0, width, height);
    if (!layout) return;
    for (const [colour, list] of byColour) {
      const path = new Path2D(); for (const i of list) hexPath(path, ...xy(i));
      context.fillStyle = colour; context.fill(path);
    }
    if (scale > 5) {
      const grout = new Path2D(); for (let i = 0; i < world.districts.length; i++) hexPath(grout, ...xy(i));
      context.strokeStyle = 'rgba(10,14,28,.35)'; context.lineWidth = Math.min(1.2, scale / 20); context.stroke(grout);
    }
    const edge = new Path2D(), half = 0.5 / SQRT3;
    for (const [x, y, a] of borders) {
      const mx = x + Math.cos(a) / 2, my = y + Math.sin(a) / 2, px = -Math.sin(a) * half, py = Math.cos(a) * half;
      edge.moveTo(sx(mx - px), sy(my - py)); edge.lineTo(sx(mx + px), sy(my + py));
    }
    context.strokeStyle = '#fbf6e6'; context.lineWidth = Math.max(1.2, Math.min(3, scale / 9)); context.lineCap = 'round'; context.stroke(edge);
    if (hoverDistrict != null) {
      const p = new Path2D(); hexPath(p, ...xy(hoverDistrict)); context.fillStyle = 'rgba(255,255,255,.45)'; context.fill(p);
    }
    if (scale > 46) {                                    // chapter names when you zoom in
      context.font = `${Math.min(11, scale / 6)}px system-ui, sans-serif`; context.textAlign = 'center'; context.textBaseline = 'middle';
      context.fillStyle = 'rgba(15,18,30,.85)';
      for (let i = 0; i < world.districts.length; i++) {
        const [x, y] = xy(i), cx = sx(x), cy = sy(y);
        if (cx < -scale || cy < -scale || cx > width + scale || cy > height + scale) continue;
        const name = world.districts[i].name;
        context.fillText(name.length > 14 ? `${name.slice(0, 13)}…` : name, cx, cy, scale * 0.9);
      }
    }
    context.textAlign = 'center'; context.textBaseline = 'middle';
    for (const book of world.books) {
      const p = layout.books[book.book_id]; if (!p) continue;
      const size = Math.max(10, Math.min(18, scale * 0.9));
      context.font = `600 ${size}px system-ui, sans-serif`;
      const w = context.measureText(book.name).width + 12;
      context.fillStyle = 'rgba(8,12,24,.72)';
      context.beginPath(); context.roundRect(sx(p[0]) - w / 2, sy(p[1]) - size * 0.8, w, size * 1.6, size * 0.8); context.fill();
      context.fillStyle = '#ffffff'; context.fillText(book.name, sx(p[0]), sy(p[1]) + 1);
    }
    placed = [];
    for (const spot of spots) {
      const i = world.districtIndex.get(spot.district_id); if (i == null) continue;
      const [x, y] = xy(i), cx = sx(x) + spot.offset[0], cy = sy(y) + spot.offset[1];
      if (cx < -40 || cy < -40 || cx > width + 40 || cy > height + 40) continue;
      drawSpot(context, spot, cx, cy, highlighted === spot || highlighted === spot.other_slug);
      placed.push({ x: cx, y: cy, spot, radius: spot.lit ? 8 : radiusPx(spot.f) + 6 });
    }
  }
  function fit() {
    if (!layout) return;
    scale = fitScale; tx = (width - layout.width * scale) / 2; ty = (height + layout.height * scale) / 2; draw();
  }
  function resize() {
    const rect = canvas.getBoundingClientRect();
    if (!rect.width || !rect.height) return;
    const atFit = Math.abs(scale - fitScale) < 1e-6;
    const ratio = Math.min(devicePixelRatio, 2), oldFit = fitScale;
    const cx = (width / 2 - tx) / scale, cy = (ty - height / 2) / scale;
    width = rect.width; height = rect.height;
    canvas.width = Math.round(width * ratio); canvas.height = Math.round(height * ratio);
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    fitScale = layout ? Math.min(width / layout.width, height / layout.height) * 0.96 : 1;
    if (atFit || !layout) fit();
    else { scale = Math.max(fitScale, Math.min(fitScale * 20, scale / oldFit * fitScale)); tx = width / 2 - cx * scale; ty = height / 2 + cy * scale; draw(); }
  }
  const point = event => { const r = canvas.getBoundingClientRect(); return { x: event.clientX - r.left, y: event.clientY - r.top }; };
  function districtAt(x, y) {
    const lx = (x - tx) / scale, ly = (ty - y) / scale;
    let best = null, distance = 0.58;
    for (let gx = Math.floor(lx) - 1; gx <= Math.floor(lx) + 1; gx++) for (let gy = Math.floor(ly) - 1; gy <= Math.floor(ly) + 1; gy++) {
      for (const i of grid.get(`${gx},${gy}`) || []) { const [px, py] = xy(i), d = Math.hypot(px - lx, py - ly); if (d < distance) { distance = d; best = i; } }
    }
    return best;
  }
  function hit(event) {
    const { x, y } = point(event);
    let best = null, distance = Infinity;
    for (const item of placed) { const d = Math.hypot(x - item.x, y - item.y); if (d <= item.radius && d < distance) { best = item.spot; distance = d; } }
    if (best) return { value: best, index: world.districtIndex.get(best.district_id) };
    if (!layout) return { value: null, index: null };
    const i = districtAt(x, y);
    return { value: i == null ? null : world.districts[i], index: i };
  }
  function zoom(factor, x = width / 2, y = height / 2) {
    const next = Math.max(fitScale, Math.min(fitScale * 20, scale * factor));
    tx = x - (x - tx) * next / scale; ty = y - (y - ty) * next / scale; scale = next; draw();
  }
  canvas.addEventListener('wheel', event => { event.preventDefault(); const p = point(event); zoom(event.deltaY < 0 ? 1.15 : 1 / 1.15, p.x, p.y); }, { passive: false });
  canvas.addEventListener('pointerdown', event => {
    canvas.setPointerCapture(event.pointerId); pointers.set(event.pointerId, point(event));
    gesture = pointers.size > 1; start = gesture ? null : { ...point(event), time: performance.now(), moved: false };
    hover(null);
  });
  canvas.addEventListener('pointermove', event => {
    const next = point(event), old = pointers.get(event.pointerId);
    if (!old) {
      const h = hit(event); hoverDistrict = h.index; highlighted = h.value?.other_slug ? h.value : null;
      canvas.style.cursor = h.value?.other_slug ? 'pointer' : 'grab'; draw(); hover(h.value, event); return;
    }
    if (start && Math.hypot(next.x - start.x, next.y - start.y) >= 6) start.moved = true;
    if (pointers.size === 2) {
      const other = [...pointers.entries()].find(([id]) => id !== event.pointerId)[1];
      const before = Math.hypot(old.x - other.x, old.y - other.y), after = Math.hypot(next.x - other.x, next.y - other.y);
      if (before > 0 && after > 0) { zoom(after / before, (old.x + other.x) / 2, (old.y + other.y) / 2); tx += (next.x - old.x) / 2; ty += (next.y - old.y) / 2; }
    } else { tx += next.x - old.x; ty += next.y - old.y; }
    pointers.set(event.pointerId, next); draw();
  });
  function release(event, cancelled = false) {
    const p = point(event);
    if (!cancelled && !gesture && start && !start.moved && performance.now() - start.time < 400 && Math.hypot(p.x - start.x, p.y - start.y) < 6) {
      const h = hit(event); if (h.value) select(h.value, event);
    }
    pointers.delete(event.pointerId); start = null; if (!pointers.size) gesture = false;
  }
  canvas.addEventListener('pointerup', e => release(e));
  canvas.addEventListener('pointercancel', e => release(e, true));
  canvas.addEventListener('lostpointercapture', e => { pointers.delete(e.pointerId); start = null; });
  canvas.addEventListener('pointerleave', () => { if (!pointers.size) { hoverDistrict = null; highlighted = null; draw(); hover(null); } });
  new ResizeObserver(resize).observe(canvas.parentElement);
  let viewBook = null;
  return {
    resize, zoom, fit,
    get viewBook() { return viewBook; },
    async setView(book) {
      if (book === viewBook && layout) return;
      const next = await data.flowers(book);
      viewBook = book; prepare(next); scale = fitScale = 0; resize(); fit();
    },
    render(entity, nextSpots = []) { spots = nextSpots; highlighted = null; draw(); },
    highlight(slug) { highlighted = slug; draw(); },
    // Test hooks (client pixels).
    screenOf(id) { const i = world.districtIndex.get(id), r = canvas.getBoundingClientRect(); return i == null || !layout ? null : { x: r.left + sx(xy(i)[0]), y: r.top + sy(xy(i)[1]) }; },
    firstSpot() { const p = placed.find(item => item.spot.other_slug), r = canvas.getBoundingClientRect(); return p ? { x: r.left + p.x, y: r.top + p.y, other_slug: p.spot.other_slug } : null; },
  };
}
