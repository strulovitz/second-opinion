// Opus 5.5 rewrite of the 3-D globe (BIBLE Part 7 section 8; Amendment 3.6 and Nir's
// decisions of 24 Oct 2026). One scene, two looks:
//   'sand'  the Sand table: books are mountains, clouds and satellites mark the layers
//   'atlas' the Atlas: flat tiles and fine lines, for reading exact places
// Both draw the SAME tiles from honeycomb.json, so a click means the same chapter in both.
// The planet never turns by itself; only the camera moves (BIBLE 8.5).
import * as THREE from 'three';
import { OrbitControls } from '../assets/three/OrbitControls.js';
import { lonLatToXYZ } from './geo.js';
import { buildAtlas } from './atlas.js';
import { buildSandTable } from './sandtable.js';
import { createLayers } from './layers.js';
import { createLabels } from './labels.js';

function stars(count, seed) {
  let s = seed; const rand = () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
  const p = [], c = [];
  for (let i = 0; i < count; i++) {
    const z = 2 * rand() - 1, a = rand() * Math.PI * 2, r = 45 + 20 * rand(), q = Math.sqrt(1 - z * z);
    p.push(r * q * Math.cos(a), r * z, r * q * Math.sin(a));
    const tint = new THREE.Color().setHSL(0.55 + 0.12 * rand(), 0.5, 0.65 + 0.35 * rand());
    c.push(tint.r, tint.g, tint.b);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(p, 3)); g.setAttribute('color', new THREE.Float32BufferAttribute(c, 3));
  return new THREE.Points(g, new THREE.PointsMaterial({ size: 1.6, sizeAttenuation: false, vertexColors: true, transparent: true, opacity: 0.85, depthWrite: false }));
}

export async function createGlobe(canvas, world, select, hover, { style = 'sand', wording = {} } = {}) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2)); renderer.setClearColor(0x000000, 0);
  renderer.localClippingEnabled = true;
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(40, 1, 0.01, 200);
  camera.position.fromArray(lonLatToXYZ(0, 15, 4.6));
  scene.add(camera);
  const sun = new THREE.DirectionalLight(0xffffff, 2.2); sun.position.set(-2, 2.5, 3); camera.add(sun);
  scene.add(new THREE.HemisphereLight(0xdfeaff, 0x40304a, 1.1));
  const controls = new OrbitControls(camera, canvas);
  Object.assign(controls, { enableDamping: true, dampingFactor: 0.08, minDistance: 1.18, maxDistance: 12, enablePan: false });
  const sky = stars(2600, 7); scene.add(sky);
  const layers = createLayers(scene, world);
  const looks = {};
  const look = name => (looks[name] ||= name === 'atlas' ? buildAtlas(world) : buildSandTable(world));
  let current = null, layersOn = false, motion = !matchMedia('(prefers-reduced-motion: reduce)').matches, cut = false;
  const stage = canvas.parentElement;
  const labels = createLabels(stage, world, camera, wording);
  const lightDirection = new THREE.Vector3();
  const raycaster = new THREE.Raycaster();
  let frame = null, start = null, tween = null, pointer = null, last = performance.now();
  let hoverTile = null, selectedTile = null;
  const pointers = new Set();

  function setStyle(name) {
    if (current) scene.remove(current.group);
    current = look(name); scene.add(current.group);
    current.layers.visible = layersOn;
    current.setHover(hoverTile?.index, hoverTile?.book); current.setSelected(selectedTile?.index);
    current.setGlass(!!layers.active && layers.active.altitude < 1);
    current.setClipping(cut ? layers.planes : null);
    layers.setBead(name === 'sand'); layers.setInteriorPalette(current.interiorPalette);
    if (layers.active) layers.highlight(null);
    stage.dataset.look = name; requestRender();
  }
  function fitDistance(radius = Math.max(1.1, layers.active?.altitude || 1)) {
    const rect = canvas.getBoundingClientRect();
    const half = THREE.MathUtils.degToRad(camera.fov / 2);
    const angle = Math.min(half, Math.atan(Math.tan(half) * (rect.width / rect.height || 1)));
    return Math.min(12, Math.max(4.2, radius / Math.sin(angle) * 1.12));
  }
  function resize() {
    const rect = canvas.getBoundingClientRect();
    if (!rect.width || !rect.height) return;
    renderer.setSize(rect.width, rect.height, false);
    camera.aspect = rect.width / rect.height; camera.updateProjectionMatrix();
    layers.resize(rect.height, camera.fov); requestRender();
  }
  function surface(event) {
    const rect = canvas.getBoundingClientRect();
    raycaster.setFromCamera(new THREE.Vector2((event.clientX - rect.left) / rect.width * 2 - 1, -(event.clientY - rect.top) / rect.height * 2 + 1), camera);
    // Analytic picking (no triangle search): walk along the ray from the top of the
    // highest mountain down to the sea and stop at the first tile top that is reached.
    const { origin, direction: d } = raycaster.ray;
    const enter = (R) => { const b = origin.dot(d), c = origin.lengthSq() - R * R, q = b * b - c; return q < 0 ? null : [-b - Math.sqrt(q), -b + Math.sqrt(q)]; };
    const outer = enter(current.name === 'sand' ? 1.1 : 1.0), inner = enter(0.999);
    if (!outer) return { hit: null, tile: null };
    const p = new THREE.Vector3();
    if (current.name !== 'sand') {
      p.copy(origin).addScaledVector(d, outer[0]);
      return { hit: { distance: outer[0] }, tile: world.tileAt(p.clone().normalize().toArray()) };
    }
    const stop = inner ? inner[0] : outer[1];
    for (let s = outer[0]; s <= stop + 1e-6; s += 0.0025) {
      p.copy(origin).addScaledVector(d, s);
      const tile = world.tileAt(p.clone().normalize().toArray());
      if (tile && p.length() <= current.top(tile) + 1e-4) return { hit: { distance: s }, tile };
    }
    return inner ? { hit: { distance: inner[0] }, tile: world.tileAt(p.copy(origin).addScaledVector(d, inner[0]).normalize().toArray()) } : { hit: null, tile: null };
  }
  function hit(event) {
    const { hit: h, tile } = surface(event);
    if (layers.active) { const spot = layers.pick(raycaster, camera, h); if (spot) return { value: spot.spot, tile: spot.tile }; }
    if (!tile || tile.kind === 'pole') return { value: null, tile: null };
    return { value: world.territoryOfTile(tile), tile };
  }
  function setHoverTile(tile) {
    if (tile === hoverTile) return;
    hoverTile = tile; current.setHover(tile?.index, tile?.book); requestRender();
  }
  function render(time) {
    frame = null;
    const dt = Math.min(100, time - last); last = time;
    if (tween) {
      const t = Math.min(1, (time - tween.start) / 700), eased = t * t * (3 - 2 * t);
      const rotation = new THREE.Quaternion().slerp(tween.rotation, eased);
      camera.position.copy(tween.from.clone().applyQuaternion(rotation).normalize().multiplyScalar(tween.d0 + (tween.distance - tween.d0) * eased));
      if (t === 1) tween = null;
    }
    const changing = controls.update();
    const distance = camera.position.length();
    controls.rotateSpeed = THREE.MathUtils.clamp((distance - 1) / 3.2, 0.06, 1);
    controls.zoomSpeed = THREE.MathUtils.clamp((distance - 1) / 2, 0.25, 1);
    camera.updateMatrixWorld();
    lightDirection.set(-2, 2.5, 3).applyQuaternion(camera.quaternion).normalize();
    current.setLight(lightDirection);
    layers.update(camera);
    const animating = current.update(time, dt, motion, distance, !!layers.active);
    if (!canvas.hidden) {
      renderer.render(scene, camera);
      const rect = canvas.getBoundingClientRect();
      labels.update({ top: current.top, summit: current.summits ? t => current.summits.get(t.book) : null, layers: layersOn || !!layers.active, cutaway: cut, width: rect.width, height: rect.height });
    }
    if (pointer) { const h = hit(pointer); setHoverTile(h.tile); hover(h.value, pointer); pointer = null; }
    if (!canvas.hidden && (changing || tween || pointers.size || animating)) requestRender();
  }
  function requestRender() { if (frame === null) frame = requestAnimationFrame(render); }
  controls.addEventListener('change', requestRender);
  controls.addEventListener('start', () => { tween = null; });
  canvas.addEventListener('pointerdown', event => {
    pointers.add(event.pointerId); tween = null;
    start = pointers.size === 1 ? { x: event.clientX, y: event.clientY, time: performance.now(), moved: false } : null;
    hover(null); requestRender();
  });
  canvas.addEventListener('pointermove', event => {
    if (start && Math.hypot(event.clientX - start.x, event.clientY - start.y) >= 6) start.moved = true;
    pointer = pointers.size ? null : event; requestRender();
  });
  canvas.addEventListener('pointerleave', () => { hover(null); setHoverTile(null); });
  canvas.addEventListener('pointercancel', event => { pointers.delete(event.pointerId); start = null; });
  canvas.addEventListener('lostpointercapture', event => { pointers.delete(event.pointerId); start = null; });
  canvas.addEventListener('pointerup', event => {
    pointers.delete(event.pointerId);
    if (start && !start.moved && performance.now() - start.time < 400) {
      const h = hit(event);
      if (h.value) select(h.value, event);
    }
    start = null; requestRender();
  });
  new ResizeObserver(resize).observe(stage);
  setStyle(style); resize();

  function direction(territory) {
    const tile = world.tileOf.get(territory.territory_id);
    return tile ? new THREE.Vector3(...tile.centre).normalize() : new THREE.Vector3(...lonLatToXYZ(territory.lon, territory.lat)).normalize();
  }
  function focus(territory, immediate = false, distance = camera.position.length()) {
    controls.enableDamping = false; controls.update(); controls.enableDamping = true;
    const target = direction(territory);
    if (immediate || matchMedia('(prefers-reduced-motion: reduce)').matches) { camera.position.copy(target.multiplyScalar(distance)); tween = null; }
    else {
      const from = camera.position.clone().normalize();
      tween = { from, rotation: new THREE.Quaternion().setFromUnitVectors(from, target), d0: camera.position.length(), distance, start: performance.now() };
    }
    requestRender();
  }
  return {
    focus, setStyle, get style() { return current.name; },
    homeDistance: () => fitDistance(1.15),
    mark(territory) {
      selectedTile = territory ? world.tileOf.get(territory.territory_id) || null : null;
      current.setSelected(selectedTile?.index); requestRender();
    },
    zoom(factor) { tween = null; camera.position.multiplyScalar(factor).clampLength(controls.minDistance, 12); requestRender(); },
    fit() { focus({ territory_id: null, lon: 0, lat: 15 }, false, fitDistance()); },
    home(territory) { focus(territory, false, fitDistance()); },
    showGlobe() {
      layers.clear(); current.setGlass(false); controls.minDistance = 1.18; requestRender();
    },
    showShell(entity, spots) {
      if (!Number.isFinite(entity.altitude) || entity.altitude <= 0 || entity.altitude > 3) throw new Error('This entity has no valid exported altitude yet');
      layers.show(entity, spots, t => (t ? current.top(t) : 1));
      const rect = canvas.getBoundingClientRect(); layers.resize(rect.height, camera.fov);
      current.setGlass(entity.altitude < 1);
      controls.minDistance = Math.max(1.18, entity.altitude + 0.15);
      const target = [...spots].sort((a, b) => (b.f ?? -1) - (a.f ?? -1))[0];
      const territory = target ? world.byId.get(target.district_id) : null;
      focus(territory || { lon: 0, lat: 15 }, false, Math.max(camera.position.length(), entity.altitude + 1.8, fitDistance()));
    },
    highlight(slug) { layers.highlight(slug); requestRender(); },
    guides(show) { layersOn = show; current.layers.visible = show; requestRender(); },
    cutaway(on) { cut = on; const planes = layers.cutaway(on, camera); current.setClipping(planes); requestRender(); },
    motion(on) { motion = on; requestRender(); },
    // The book you are looking at: the 2-D flower map is centred on it.
    viewBook() {
      const tile = world.tileAt(camera.position.clone().normalize().toArray());
      if (tile && tile.book >= 0) return world.books[tile.book].book_id;
      const near = tile?.neighbors.map(n => world.tiles[n]).find(t => t.book >= 0);
      return near ? world.books[near.book].book_id : world.books[0].book_id;
    },
    resize,
    // Test hook: where a territory's tile appears on the screen (client pixels).
    screenOf(territory) {
      const tile = world.tileOf.get(territory.territory_id); if (!tile) return null;
      const p = new THREE.Vector3(...tile.centre).normalize().multiplyScalar(current.top(tile)).project(camera);
      const rect = canvas.getBoundingClientRect();
      return { x: rect.left + (p.x + 1) / 2 * rect.width, y: rect.top + (1 - p.y) / 2 * rect.height };
    },
    alignment(territory) {
      const tile = world.tileAt(lonLatToXYZ(territory.lon, territory.lat));
      return tile?.book_id === territory.book_id;
    },
  };
}
