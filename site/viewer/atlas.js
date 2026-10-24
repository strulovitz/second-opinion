// Opus 5.5 addition: the ATLAS style ("the topographic map for experts").
// Flat honeycomb tiles on a lit ball, crisp lines, glass layer guides.
import * as THREE from 'three';
import { tileMaterial, tileColour, lineKind, glowMaterial } from './materials.js';
import { BANDS, SUBBANDS } from './geo.js';

// Shared by both styles: one fan of triangles per tile. top(tile) gives the radius
// of the tile's top face; walls(tile, i) may add column walls (sand table only).
export function tileGeometry(world, radiusOf, colourOf, { walls = false, base = 0.965, normalOf = null } = {}) {
  const pos = [], nor = [], col = [], edge = [], tileA = [], bookA = [], lineA = [];
  const v = new THREE.Vector3(), a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3();
  const push = (p, n, colour, e, t, line) => {
    pos.push(p.x, p.y, p.z); nor.push(n.x, n.y, n.z); col.push(colour.r, colour.g, colour.b);
    edge.push(e); tileA.push(t.index); bookA.push(t.book); lineA.push(line);
  };
  const neighbourAcross = new Map();
  for (const t of world.tiles) {
    // The tile across side i is the neighbour that owns both corner vertices of that side.
    const mine = t.vertices;
    for (const n of t.neighbors) {
      const other = world.tiles[n], shared = other.vertices.filter(x => mine.includes(x));
      if (shared.length !== 2) continue;
      for (let i = 0; i < mine.length; i++) {
        const p = mine[i], q = mine[(i + 1) % mine.length];
        if (shared.includes(p) && shared.includes(q)) neighbourAcross.set(`${t.index}:${i}`, other);
      }
    }
  }
  for (const t of world.tiles) {
    const r = radiusOf(t), colour = colourOf(t), centre = new THREE.Vector3(...t.centre).normalize();
    const k = t.vertices.length, shade = normalOf ? normalOf(t) : null;
    for (let i = 0; i < k; i++) {
      a.fromArray(world.vertices[t.vertices[i]]).normalize();
      b.fromArray(world.vertices[t.vertices[(i + 1) % k]]).normalize();
      const other = neighbourAcross.get(`${t.index}:${i}`), line = lineKind(t, other);
      // Top face (normal = sphere normal at each vertex: smooth light over the ball).
      push(c.copy(centre).multiplyScalar(r), shade || centre, colour, 1, t, line);
      push(v.copy(a).multiplyScalar(r), shade || a, colour, 0, t, line);
      push(v.copy(b).multiplyScalar(r), shade || b, colour, 0, t, line);
      if (walls) {
        const lower = other ? Math.min(r, radiusOf(other)) : base;
        if (r - lower > 1e-5) {
          const n = new THREE.Vector3().addVectors(a, b).normalize().sub(centre).normalize();
          const wall = colour.clone().multiplyScalar(0.62), bottom = Math.max(base, lower - 0.002);
          const a0 = a.clone().multiplyScalar(bottom), b0 = b.clone().multiplyScalar(bottom);
          const a1 = a.clone().multiplyScalar(r), b1 = b.clone().multiplyScalar(r);
          push(a0, n, wall, -1, t, 0); push(b0, n, wall, -1, t, 0); push(b1, n, wall, -1, t, 0);
          push(a0, n, wall, -1, t, 0); push(b1, n, wall, -1, t, 0); push(a1, n, wall, -1, t, 0);
        }
      }
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
  g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
  g.setAttribute('edge', new THREE.Float32BufferAttribute(edge, 1));
  g.setAttribute('tile', new THREE.Float32BufferAttribute(tileA, 1));
  g.setAttribute('book', new THREE.Float32BufferAttribute(bookA, 1));
  g.setAttribute('line', new THREE.Float32BufferAttribute(lineA, 1));
  g.computeBoundingSphere();
  return g;
}

function ring(radius, colour, opacity, dashed = false) {
  const points = [];
  for (let i = 0; i <= 256; i++) { const a = i / 256 * Math.PI * 2; points.push(new THREE.Vector3(Math.cos(a) * radius, 0, Math.sin(a) * radius)); }
  const g = new THREE.BufferGeometry().setFromPoints(points);
  const m = dashed ? new THREE.LineDashedMaterial({ color: colour, transparent: true, opacity, dashSize: 0.03, gapSize: 0.025, depthWrite: false })
    : new THREE.LineBasicMaterial({ color: colour, transparent: true, opacity, depthWrite: false });
  const line = new THREE.Line(g, m); if (dashed) line.computeLineDistances();
  return line;
}
// Deterministic orbit tilts so the five orbit groups never look like one flat disc.
export const ORBIT_TILTS = [[0.35, 0.2], [-0.5, 1.1], [0.62, 2.3], [-0.28, 3.4], [0.48, 4.6]];

export function buildAtlas(world) {
  const material = tileMaterial({ toon: false, rim: '#3a6db5', rimStrength: 0.45 });
  const planet = new THREE.Mesh(tileGeometry(world, () => 1, t => tileColour(world, t, 'atlas')), material);
  planet.renderOrder = 1;
  const group = new THREE.Group(); group.add(planet);
  const atmosphere = new THREE.Mesh(new THREE.SphereGeometry(1.075, 96, 64), glowMaterial('#5aa9ff', { power: 3.2, strength: 1.25 }));
  group.add(atmosphere);
  // The future layers, drawn as faint glass so they never hide the map.
  const layers = new THREE.Group(); layers.visible = false; group.add(layers);
  layers.add(new THREE.Mesh(new THREE.SphereGeometry(BANDS[1].max, 72, 48), glowMaterial(BANDS[1].tint, { power: 4, strength: 0.55, side: THREE.FrontSide })));
  for (const [i, sub] of SUBBANDS.entries()) {
    const r = (sub.min + sub.max) / 2, orbit = new THREE.Group();
    orbit.add(ring(r, BANDS[2].tint, 0.55, true));
    orbit.rotation.set(ORBIT_TILTS[i][0], ORBIT_TILTS[i][1], 0);
    layers.add(orbit);
  }
  return {
    name: 'atlas', group, pickMesh: planet, layers,
    top: () => 1,
    setLight(direction) { material.uniforms.uLight.value.copy(direction); },
    setHover(tile, book) { material.uniforms.uHover.value = tile ?? -1; material.uniforms.uHoverBook.value = book ?? -1; },
    setSelected(tile) { material.uniforms.uSelected.value = tile ?? -1; },
    setGlass(on) { material.uniforms.uOpacity.value = on ? 0.32 : 1; material.depthWrite = !on; atmosphere.visible = !on; },
    setClipping(planes) { material.clippingPlanes = planes; material.clipIntersection = true; material.needsUpdate = true; },
    update() { return false; },
    interiorPalette: ['#0d2a52', '#174a85', '#2c6fb4', '#56a0de', '#9bd0f5'],
  };
}
