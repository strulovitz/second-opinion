// Opus 5.5 addition: crisp HTML labels laid over the 3-D view (never painted into a texture).
// Book names sit on each book's name tile (Atlas) or summit flag (Sand table); chapter
// names appear only when you fly close; band and orbit names appear with the layers.
import * as THREE from 'three';
import { BANDS, SUBBANDS } from './geo.js';
import { ORBIT_TILTS } from './atlas.js';

export function createLabels(stage, world, camera, wording) {
  const root = document.createElement('div'); root.id = 'labels'; stage.append(root);
  const make = (text, className) => { const e = document.createElement('div'); e.className = `label ${className}`; e.textContent = text; root.append(e); return e; };
  const sizes = world.books.map(b => world.tiles.filter(t => t.book_id === b.book_id).length);
  const books = world.tiles.filter(t => t.kind === 'name').map(t => ({ tile: t, el: make(world.books[t.book].name, 'book') }));
  for (const b of books) b.el.style.fontSize = `${11 + 5 * Math.sqrt(sizes[b.tile.book] / 520)}px`;
  const chapters = Array.from({ length: 36 }, () => make('', 'chapter'));
  const bands = [
    { el: make(`${BANDS[1].label} · ${BANDS[1].where}`, 'band symptoms'), r: 1.3, side: 0.82, lift: 0.57 },
    { el: make(`${BANDS[2].label} · ${BANDS[2].where}`, 'band treatments'), r: 2.05, side: 0.55, lift: 0.83 },
    { el: make(`${BANDS[0].label} · ${BANDS[0].where}`, 'band diseases'), r: 0.6, side: 0.2, lift: -0.4, inside: true },
  ];
  const orbits = SUBBANDS.map((s, i) => {
    const m = new THREE.Matrix4().makeRotationFromEuler(new THREE.Euler(ORBIT_TILTS[i][0], ORBIT_TILTS[i][1], 0));
    return { el: make(wording.heaviness_labels?.[s.key] || s.key, 'orbit'), r: (s.min + s.max) / 2, m };
  });
  const v = new THREE.Vector3(), eye = new THREE.Vector3();
  function place(el, point, opacity, width, height, taken = null) {
    v.copy(point).project(camera);
    if (v.z > 1 || opacity <= 0.02) { el.style.opacity = '0'; el.hidden = true; return; }
    const x = (v.x * 0.5 + 0.5) * width, y = (-v.y * 0.5 + 0.5) * height;
    if (taken) {                                   // never let two labels sit on top of each other
      el.hidden = false;
      if (el.dataset.text !== el.textContent) { el.dataset.text = el.textContent; el.dataset.w = el.offsetWidth; el.dataset.h = el.offsetHeight; }
      const w = +el.dataset.w / 2 + 3, h = +el.dataset.h / 2 + 2;
      if (taken.some(r => Math.abs(r[0] - x) < r[2] + w && Math.abs(r[1] - y) < r[3] + h)) { el.style.opacity = '0'; el.hidden = true; return; }
      taken.push([x, y, w, h]);
    }
    el.hidden = false;
    el.style.transform = `translate(${x}px, ${y}px) translate(-50%, -50%)`;
    el.style.opacity = String(Math.min(1, opacity));
  }
  return {
    update({ top, summit, layers, cutaway, width, height }) {
      eye.copy(camera.position); const distance = eye.length(), view = eye.clone().normalize();
      const taken = [];
      const ordered = [...books].sort((a, b) => sizes[b.tile.book] - sizes[a.tile.book]);
      for (const b of ordered) {
        const n = new THREE.Vector3(...b.tile.centre).normalize();
        const facing = n.dot(view), p = n.clone().multiplyScalar(summit ? summit(b.tile) : top(b.tile) + 0.005);
        const occluded = facing < 0.18;
        place(b.el, p, occluded ? 0 : THREE.MathUtils.smoothstep(facing, 0.18, 0.45) * (distance < 1.7 ? 0.55 : 1), width, height, taken);
      }
      const near = distance < 2.05 ? world.tiles.filter(t => t.kind === 'district')
        .map(t => [new THREE.Vector3(...t.centre).normalize().dot(view), t]).filter(([d]) => d > Math.cos(0.42 * (distance - 1))).sort((a, b) => b[0] - a[0]).slice(0, chapters.length) : [];
      chapters.forEach((el, i) => {
        const item = near[i];
        if (!item) { el.hidden = true; return; }
        const [, t] = item, name = t.territory.name;
        el.textContent = name.length > 22 ? `${name.slice(0, 21)}…` : name;
        place(el, new THREE.Vector3(...t.centre).normalize().multiplyScalar(top(t) + 0.003), THREE.MathUtils.smoothstep(2.05 - distance, 0, 0.25), width, height, taken);
      });
      const right = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 0), up = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 1);
      for (const b of bands) {
        const show = layers && (!b.inside || cutaway);
        place(b.el, right.clone().multiplyScalar(b.side * b.r).addScaledVector(up, b.lift * b.r), show ? 1 : 0, width, height, taken);
      }
      for (const o of orbits) {
        const p = new THREE.Vector3(o.r, 0, 0).applyMatrix4(o.m);
        place(o.el, p, layers && p.dot(view) > -0.2 ? 0.9 : 0, width, height, taken);
      }
    },
  };
}
