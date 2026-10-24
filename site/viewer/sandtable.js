// Opus 5.5 addition: the SAND TABLE style ("the war-room model for everyone").
// Every book is a mountain of hexagon columns: its border chapters are the foothills,
// its name tile is the summit with a flag. The 12 pentagon poles are little lakes.
// Above: cartoon clouds in the symptom atmosphere and cartoon satellites on the five
// treatment orbits. Clouds and satellites are DECORATION that shows where the bands
// are; real entity lights never move (they are drawn by layers.js at fixed places).
import * as THREE from 'three';
import { tileMaterial, tileColour, glowMaterial } from './materials.js';
import { tileGeometry, ORBIT_TILTS } from './atlas.js';
import { BANDS, SUBBANDS } from './geo.js';

function random(seed) { let s = seed >>> 0; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }
export function toonRamp() {
  const data = new Uint8Array([90, 90, 90, 255, 170, 170, 170, 255, 255, 255, 255, 255]);
  const texture = new THREE.DataTexture(data, 3, 1, THREE.RGBAFormat);
  texture.minFilter = texture.magFilter = THREE.NearestFilter; texture.needsUpdate = true;
  return texture;
}
function frame(normal) {
  const up = Math.abs(normal.y) < 0.95 ? new THREE.Vector3(0, 1, 0) : new THREE.Vector3(1, 0, 0);
  const east = new THREE.Vector3().crossVectors(up, normal).normalize();
  const north = new THREE.Vector3().crossVectors(normal, east);
  return new THREE.Matrix4().makeBasis(east, normal, north);
}

// Height of every tile above the surface: depth in steps from the book's border.
export function heights(world) {
  const depth = new Map(), out = new Float32Array(world.tiles.length);
  const queue = [];
  for (const t of world.tiles) {
    if (t.kind === 'pole') continue;
    if (t.neighbors.some(n => world.tiles[n].book !== t.book)) { depth.set(t.index, 0); queue.push(t.index); }
  }
  for (let q = 0; q < queue.length; q++) {
    const t = world.tiles[queue[q]];
    for (const n of t.neighbors) if (!depth.has(n) && world.tiles[n].book === t.book) { depth.set(n, depth.get(t.index) + 1); queue.push(n); }
  }
  const deepest = new Map(), size = new Map();
  for (const t of world.tiles) if (t.book >= 0) {
    deepest.set(t.book, Math.max(deepest.get(t.book) || 0, depth.get(t.index) || 0));
    size.set(t.book, (size.get(t.book) || 0) + 1);
  }
  const relief = new Map([...size].map(([b, n]) => [b, 0.022 + 0.10 * Math.sqrt(n / 520)]));
  for (const t of world.tiles) {
    if (t.kind === 'pole') { out[t.index] = 0; continue; }
    const s = (depth.get(t.index) || 0) / Math.max(1, deepest.get(t.book));
    out[t.index] = 0.006 + relief.get(t.book) * Math.pow(s, 0.9);
  }
  return { height: out, relief, depth, deepest };
}

function colourOf(world, t, h, relief) {
  const c = tileColour(world, t, 'sand');
  if (t.kind === 'pole') return c;
  const top = relief.get(t.book), s = (h - 0.006) / top;
  c.multiplyScalar(0.82 + 0.3 * s);
  if (top > 0.05 && s > 0.82) c.lerp(new THREE.Color('#ffffff'), 0.55 + 0.4 * (s - 0.82) / 0.18);   // snow caps on the big books
  return c;
}

function satelliteModel(materials) {
  const s = new THREE.Group();
  const body = new THREE.Mesh(new THREE.BoxGeometry(1, 1.2, 1), materials.gold); s.add(body);
  for (const side of [-1, 1]) {
    const arm = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.8), materials.metal);
    arm.rotation.z = Math.PI / 2; arm.position.x = side * 0.9; s.add(arm);
    const panel = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.05, 0.9), materials.panel);
    panel.position.x = side * 2.1; s.add(panel);
  }
  const dish = new THREE.Mesh(new THREE.ConeGeometry(0.45, 0.35, 20, 1, true), materials.metal);
  dish.position.y = -0.85; dish.rotation.x = Math.PI; s.add(dish);
  const antenna = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.7), materials.metal);
  antenna.position.y = 0.95; s.add(antenna);
  return s;
}

export function buildSandTable(world) {
  const { height, relief } = heights(world);
  const material = tileMaterial({ toon: true, border: '#fffbea', rim: '#ffd8a8', rimStrength: 0.18 });
  // Hill shading: each tile top leans away from the uphill side, so slopes catch the light.
  const normalOf = t => {
    const n = new THREE.Vector3(...t.centre).normalize(), g = new THREE.Vector3();
    for (const j of t.neighbors) {
      const o = world.tiles[j]; if (o.book !== t.book) continue;
      const d = new THREE.Vector3(...o.centre).normalize().sub(n);
      g.addScaledVector(d.normalize(), (height[j] - height[t.index]) / 0.05);
    }
    return n.addScaledVector(g, -4.0).normalize();
  };
  const terrain = new THREE.Mesh(tileGeometry(world, t => 1 + height[t.index], t => colourOf(world, t, height[t.index], relief), { walls: true, normalOf }), material);
  const group = new THREE.Group(); group.add(terrain);
  const ramp = toonRamp();
  const toon = (colour, extra = {}) => new THREE.MeshToonMaterial({ color: colour, gradientMap: ramp, ...extra });
  const atmosphere = new THREE.Mesh(new THREE.SphereGeometry(1.1, 96, 64), glowMaterial('#8fd3ff', { power: 2.6, strength: 0.9 }));
  group.add(atmosphere);

  // Trees on the middle slopes (about one chapter in seven, chosen by a fixed hash).
  const rand = random(4812), dummy = new THREE.Object3D();
  const slopes = world.tiles.filter(t => t.kind === 'district' && (t.index * 2654435761 >>> 0) % 9 === 0);
  const crowns = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(0.0085, 1), toon('#ffffff'), slopes.length);
  const trunks = new THREE.InstancedMesh(new THREE.CylinderGeometry(0.0016, 0.0022, 0.012, 6), toon('#7a5230'), slopes.length);
  const greens = ['#3f9b4f', '#4cae5e', '#2f8f46', '#5bbd6a'].map(c => new THREE.Color(c));
  slopes.forEach((t, i) => {
    const n = new THREE.Vector3(...t.centre).normalize(), r = 1 + height[t.index], s = 0.8 + 0.5 * rand();
    const m = frame(n); dummy.position.copy(n).multiplyScalar(r + 0.017 * s); dummy.quaternion.setFromRotationMatrix(m); dummy.scale.setScalar(s); dummy.updateMatrix();
    crowns.setMatrixAt(i, dummy.matrix); crowns.setColorAt(i, greens[i % greens.length]);
    dummy.position.copy(n).multiplyScalar(r + 0.006 * s); dummy.updateMatrix(); trunks.setMatrixAt(i, dummy.matrix);
  });
  group.add(crowns, trunks);

  // A flag on every summit (the book's name tile).
  const flags = new THREE.Group(), summits = new Map();
  for (const t of world.tiles.filter(x => x.kind === 'name')) {
    const n = new THREE.Vector3(...t.centre).normalize(), r = 1 + height[t.index];
    const f = new THREE.Group(); f.position.copy(n).multiplyScalar(r); f.quaternion.setFromRotationMatrix(frame(n));
    const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.0009, 0.0009, 0.045, 6), toon('#e8e2d0')); pole.position.y = 0.0225; f.add(pole);
    const cloth = new THREE.Mesh(new THREE.PlaneGeometry(0.026, 0.016), toon(world.books[t.book].colour_hex, { side: THREE.DoubleSide }));
    cloth.position.set(0.013, 0.037, 0); f.add(cloth);
    flags.add(f); summits.set(t.book, r + 0.05);
  }
  group.add(flags);

  // Decoration for the future layers: clouds (symptoms) and satellites (treatments).
  const layers = new THREE.Group(); group.add(layers);
  const clouds = new THREE.Group(); layers.add(clouds);
  const puffMaterial = toon('#ffffff', { transparent: true, opacity: 0.94 });
  const count = 44, puffs = [];
  for (let i = 0; i < count; i++) {
    const y = 1 - 2 * (i + 0.5) / count, rr = Math.sqrt(1 - y * y), a = i * 2.399963;
    const n = new THREE.Vector3(Math.cos(a) * rr, y, Math.sin(a) * rr);
    const radius = BANDS[1].min + 0.1 + (BANDS[1].max - BANDS[1].min - 0.2) * rand(), size = 0.028 + 0.03 * rand();
    const m = frame(n), k = 5 + Math.floor(rand() * 4);
    for (let j = 0; j < k; j++) {
      const local = new THREE.Vector3((j - (k - 1) / 2) * 0.9 + (rand() - 0.5) * 0.4, (rand() - 0.2) * 0.5, (rand() - 0.5) * 0.9).multiplyScalar(size);
      local.applyMatrix4(m);
      puffs.push({ p: n.clone().multiplyScalar(radius).add(local), s: size * (0.75 + 0.6 * rand()) });
    }
  }
  const puffMesh = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(1, 2), puffMaterial, puffs.length);
  puffs.forEach((p, i) => { dummy.position.copy(p.p); dummy.quaternion.identity(); dummy.scale.set(p.s, p.s * 0.78, p.s); dummy.updateMatrix(); puffMesh.setMatrixAt(i, dummy.matrix); });
  clouds.add(puffMesh);

  const parts = { gold: toon('#e8b33b'), metal: toon('#c9d2dc'), panel: toon('#2f5fd0') };
  const orbits = [];
  for (const [i, sub] of SUBBANDS.entries()) {
    const r = (sub.min + sub.max) / 2, orbit = new THREE.Group();
    orbit.rotation.set(ORBIT_TILTS[i][0], ORBIT_TILTS[i][1], 0);
    const points = []; for (let k = 0; k <= 256; k++) { const a = k / 256 * Math.PI * 2; points.push(new THREE.Vector3(Math.cos(a) * r, 0, Math.sin(a) * r)); }
    const path = new THREE.Line(new THREE.BufferGeometry().setFromPoints(points), new THREE.LineDashedMaterial({ color: '#ffe28a', transparent: true, opacity: 0.55, dashSize: 0.04, gapSize: 0.03 }));
    path.computeLineDistances(); orbit.add(path);
    const sats = [];
    for (let k = 0; k < 3; k++) {
      const s = satelliteModel(parts); s.scale.setScalar(0.022 + 0.004 * i); orbit.add(s);
      sats.push({ s, phase: k * Math.PI * 2 / 3 + i });
    }
    orbits.push({ orbit, sats, r, speed: 0.05 * Math.pow(1.5 / r, 1.5) });
    layers.add(orbit);
  }
  function placeSatellites(t) {
    for (const o of orbits) for (const x of o.sats) {
      const a = x.phase + t * o.speed;
      x.s.position.set(Math.cos(a) * o.r, 0, Math.sin(a) * o.r); x.s.lookAt(0, 0, 0);
    }
  }
  placeSatellites(0);
  let elapsed = 0;
  return {
    name: 'sand', group, pickMesh: terrain, layers, summits,
    top: t => 1 + height[t.index],
    setLight(direction) { material.uniforms.uLight.value.copy(direction); },
    setHover(tile, book) { material.uniforms.uHover.value = tile ?? -1; material.uniforms.uHoverBook.value = book ?? -1; },
    setSelected(tile) { material.uniforms.uSelected.value = tile ?? -1; },
    setGlass(on) {
      material.uniforms.uOpacity.value = on ? 0.3 : 1; material.depthWrite = !on;
      crowns.visible = trunks.visible = flags.visible = atmosphere.visible = !on;
    },
    setClipping(planes) {
      for (const m of [material, crowns.material, trunks.material]) { m.clippingPlanes = planes; m.clipIntersection = true; m.needsUpdate = true; }
      flags.visible = !planes;
    },
    // Decoration motion only (Nir, 24 Oct 2026: the sand table may be playful).
    update(time, dt, motion, cameraDistance, busy = false) {
      puffMaterial.opacity = (busy ? 0.42 : 0.94) * THREE.MathUtils.smoothstep(cameraDistance, 1.55, 2.4);
      clouds.visible = puffMaterial.opacity > 0.02 && !busy;   // an open entity shell gets a clear view
      crowns.visible = trunks.visible = cameraDistance < 2.7 && material.uniforms.uOpacity.value === 1;   // trees only when you fly close
      if (!motion || !layers.visible) return false;
      elapsed += dt / 1000;
      clouds.rotation.y = elapsed * 0.012;
      placeSatellites(elapsed);
      return true;
    },
    interiorPalette: ['#fff1a8', '#ffc247', '#ff8a2a', '#d9481f', '#7a3b22'],
  };
}
