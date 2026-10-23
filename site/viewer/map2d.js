import { W, H } from './geo.js';
import { image } from './data.js';

export async function createMap(canvas, world, select, hover) {
  const picture = await image(world.textureURL());
  let fit = { x: 0, y: 0, w: 1, h: 1 };
  function resize() {
    const rect = canvas.getBoundingClientRect();
    if (!rect.width || !rect.height) return;
    const ratio = Math.min(devicePixelRatio, 2);
    canvas.width = Math.round(rect.width * ratio); canvas.height = Math.round(rect.height * ratio);
    const width = Math.min(rect.width, rect.height * 2);
    fit = { x: (rect.width - width) / 2, y: (rect.height - width / 2) / 2, w: width, h: width / 2 };
    const context = canvas.getContext('2d');
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.fillStyle = '#0b0f1a'; context.fillRect(0, 0, rect.width, rect.height);
    context.drawImage(picture, fit.x, fit.y, fit.w, fit.h);
  }
  function hit(event) {
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left - fit.x, y = event.clientY - rect.top - fit.y;
    return x >= 0 && y >= 0 && x < fit.w && y < fit.h ? world.districtAt(x / fit.w * W, y / fit.h * H) : null;
  }
  canvas.addEventListener('click', event => { const district = hit(event); if (district) select(district); });
  canvas.addEventListener('pointermove', event => hover(hit(event), event));
  canvas.addEventListener('pointerleave', () => hover(null));
  const observer = new ResizeObserver(resize);
  observer.observe(canvas.parentElement);
  return { resize };
}
