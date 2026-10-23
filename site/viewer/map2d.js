import { W, H, lonLatToPixel, radiusPx, drawSpot } from './geo.js';
import { image } from './data.js';

export async function createMap(canvas, world, select, hover) {
  const picture = await image(world.textureURL(innerWidth < 900));
  const context = canvas.getContext('2d');
  let width = 1, height = 1, fitScale = 1, scale = 1, tx = 0, ty = 0;
  let spots = [], placed = [], highlighted = null, start = null, gesture = false;
  const pointers = new Map();
  function draw() {
    if (canvas.hidden) return;
    context.fillStyle = '#0b0f1a'; context.fillRect(0, 0, width, height);
    context.drawImage(picture, tx, ty, W * scale, H * scale);
    placed = [];
    for (const spot of spots) {
      if (spots.length > 4000 && spot.lit && scale <= fitScale * 2) continue;
      const [px, py] = lonLatToPixel(spot.lon, spot.lat);
      const x = tx + px * scale + spot.offset[0], y = ty + py * scale + spot.offset[1];
      if (x < -40 || y < -40 || x > width + 40 || y > height + 40) continue;
      drawSpot(context, spot, x, y, highlighted === spot || highlighted === spot.other_slug);
      placed.push({ x, y, spot, radius: spot.lit ? 8 : radiusPx(spot.f) + 6 });
    }
  }
  function fit() { scale = fitScale; tx = (width - W * scale) / 2; ty = (height - H * scale) / 2; draw(); }
  function resize() {
    const rect = canvas.getBoundingClientRect();
    if (!rect.width || !rect.height) return;
    const atFit = Math.abs(scale - fitScale) < 0.0001;
    const cx = (width / 2 - tx) / scale, cy = (height / 2 - ty) / scale;
    const ratio = Math.min(devicePixelRatio, 2), oldFit = fitScale;
    width = rect.width; height = rect.height;
    canvas.width = Math.round(width * ratio); canvas.height = Math.round(height * ratio);
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    fitScale = Math.min(width / W, height / H);
    if (atFit) fit();
    else { scale = Math.max(fitScale, Math.min(fitScale * 16, scale / oldFit * fitScale)); tx = width / 2 - cx * scale; ty = height / 2 - cy * scale; draw(); }
  }
  function point(event) {
    const rect = canvas.getBoundingClientRect();
    return { x: event.clientX - rect.left, y: event.clientY - rect.top };
  }
  function hit(event) {
    const { x, y } = point(event);
    let best = null, distance = Infinity;
    for (const item of placed) {
      const d = Math.hypot(x - item.x, y - item.y);
      if (d <= item.radius && d < distance) { best = item.spot; distance = d; }
    }
    if (best) return best;
    const px = (x - tx) / scale, py = (y - ty) / scale;
    return px >= 0 && py >= 0 && px < W && py < H ? world.districtAt(px, py) : null;
  }
  function zoom(factor, x = width / 2, y = height / 2) {
    const next = Math.max(fitScale, Math.min(fitScale * 16, scale * factor));
    tx = x - (x - tx) * next / scale; ty = y - (y - ty) * next / scale; scale = next; draw();
  }
  canvas.addEventListener('wheel', event => {
    event.preventDefault(); const p = point(event); zoom(event.deltaY < 0 ? 1.15 : 1 / 1.15, p.x, p.y);
  }, { passive: false });
  canvas.addEventListener('pointerdown', event => {
    canvas.setPointerCapture(event.pointerId); pointers.set(event.pointerId, point(event));
    gesture = pointers.size > 1;
    if (gesture) start = null;
    else start = { ...point(event), time: performance.now(), moved: false };
    hover(null);
  });
  canvas.addEventListener('pointermove', event => {
    const next = point(event), old = pointers.get(event.pointerId);
    if (!old) {
      const value = hit(event); highlighted = value?.district_id ? value : null;
      canvas.style.cursor = value?.other_slug ? 'pointer' : 'grab'; draw(); hover(value, event); return;
    }
    if (start && Math.hypot(next.x - start.x, next.y - start.y) >= 6) start.moved = true;
    if (pointers.size === 2) {
      const other = [...pointers.entries()].find(([id]) => id !== event.pointerId)[1];
      const before = Math.hypot(old.x - other.x, old.y - other.y);
      const after = Math.hypot(next.x - other.x, next.y - other.y);
      if (before > 0 && after > 0) {
        const mx = (old.x + other.x) / 2, my = (old.y + other.y) / 2;
        zoom(after / before, mx, my); tx += (next.x - old.x) / 2; ty += (next.y - old.y) / 2;
      }
    } else { tx += next.x - old.x; ty += next.y - old.y; }
    pointers.set(event.pointerId, next); draw();
  });
  function release(event, cancelled = false) {
    const p = point(event);
    if (!cancelled && !gesture && start && !start.moved && performance.now() - start.time < 400 && Math.hypot(p.x - start.x, p.y - start.y) < 6) {
      const value = hit(event); if (value) select(value, event);
    }
    pointers.delete(event.pointerId); start = null;
    if (!pointers.size) gesture = false;
  }
  canvas.addEventListener('pointerup', e => release(e));
  canvas.addEventListener('pointercancel', e => release(e, true));
  canvas.addEventListener('lostpointercapture', e => { pointers.delete(e.pointerId); start = null; });
  canvas.addEventListener('pointerleave', () => { if (!pointers.size) { highlighted = null; draw(); hover(null); } });
  new ResizeObserver(resize).observe(canvas.parentElement);
  return { resize, zoom, fit, render(entity, nextSpots = []) { spots = nextSpots; highlighted = null; resize(); draw(); },
    highlight(slug) { highlighted = slug; draw(); } };
}
