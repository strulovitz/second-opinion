// BIBLE Part 0 12.5(d) and 13: the same arrows DRAWN in 3-D between the heights.
// Nothing moves: no flight, no camera animation. A curve goes from the point on A's
// height above A's anchor tile to the point on B's height, with the arrowhead at B.
// Diseases sit on their hexagon; symptoms in the air; treatments in orbit; causes under
// the ground (drawn see-through so the visitor can find them; no glass planet).
import * as THREE from 'three';
import { WALK_COLOUR, drawIcon, drawLabel, anchorsOf, fade, nodeValue, arrowValue } from './paths.js?v=8dfde9d-202611041435';

function iconTexture(node, active) {
  const image = document.createElement('canvas'); image.width = 512; image.height = 192;
  const c = image.getContext('2d'); c.scale(2, 2);
  drawIcon(c, node, 128, 34, active ? 44 : 36, active); drawLabel(c, node.name, 128, 76, 15);
  const t = new THREE.CanvasTexture(image); t.colorSpace = THREE.SRGBColorSpace; return t;
}

export function createPaths3d(scene, world) {
  const group = new THREE.Group(); group.renderOrder = 6; scene.add(group);
  let picks = [], sprites = [];
  function clear() {
    for (const o of [...group.children]) { group.remove(o); o.geometry?.dispose(); o.material?.map?.dispose(); o.material?.dispose(); }
    picks = []; sprites = [];
  }
  function point(node, place, topOf) {
    const dir = new THREE.Vector3(...place.tile.centre).normalize();
    if (place.k) {                                     // several things on one tile: spread them a little
      const up = Math.abs(dir.y) < 0.95 ? new THREE.Vector3(0, 1, 0) : new THREE.Vector3(1, 0, 0);
      const east = new THREE.Vector3().crossVectors(up, dir).normalize(), north = new THREE.Vector3().crossVectors(dir, east);
      const a = place.k * 2.39996;
      dir.addScaledVector(east, 0.022 * Math.sqrt(place.k) * Math.cos(a)).addScaledVector(north, 0.022 * Math.sqrt(place.k) * Math.sin(a)).normalize();
    }
    const top = topOf(place.tile);
    const r = node.place === 'surface' ? top + 0.012 : node.place === 'underground' ? Math.min(node.altitude, 0.97)
      : Math.max(node.altitude, top + 0.03);
    return dir.multiplyScalar(r);
  }
  function tube(curve, radius, colour, opacity, see, from = 0, to = 1) {
    const part = from === 0 && to === 1 ? curve : new THREE.CatmullRomCurve3(Array.from({ length: 9 }, (_, i) => curve.getPointAt(from + (to - from) * i / 8)));
    const m = new THREE.Mesh(new THREE.TubeGeometry(part, 40, radius, 8, false),
      new THREE.MeshBasicMaterial({ color: colour, transparent: true, opacity, depthTest: !see, depthWrite: false }));
    group.add(m); return m;
  }
  return {
    clear,
    show(walk, topOf) {
      clear(); if (!walk) return;
      const places = anchorsOf(walk, world), at = new Map();
      for (const n of walk.nodes) { const p = places.get(n.slug); if (p) at.set(n.slug, point(n, p, topOf)); }
      const byNode = new Map(walk.nodes.map(n => [n.slug, n]));
      const pair = new Map();
      for (const a of walk.arrows) {
        const p = at.get(a.from), q = at.get(a.to); if (!p || !q) continue;
        const key = [a.from, a.to].sort().join('|'), k = pair.get(key) || 0; pair.set(key, k + 1);
        const see = byNode.get(a.from)?.place === 'underground' || byNode.get(a.to)?.place === 'underground';
        // An arc over the surface along the great circle (never through the far side), lifted in the middle.
        const da = p.clone().normalize(), db = q.clone().normalize(), angle = da.angleTo(db), dist = p.distanceTo(q);
        const axis = new THREE.Vector3().crossVectors(da, db); if (axis.lengthSq() < 1e-9) axis.set(0, 1, 0).cross(da);
        axis.normalize();
        const sideways = new THREE.Vector3().crossVectors(axis, da);
        const lift = see ? 0 : 0.08 + 0.35 * angle / Math.PI, wiggle = (k % 2 ? -1 : 1) * 0.03 * (1 + k);
        const pts = [];
        for (let i = 0; i <= 32; i++) {
          const t = i / 32, dir = da.clone().applyAxisAngle(axis, angle * t);
          if (k) dir.addScaledVector(axis, wiggle * Math.sin(Math.PI * t)).normalize();
          pts.push(dir.multiplyScalar(p.length() + (q.length() - p.length()) * t + lift * Math.sin(Math.PI * t)));
        }
        if (angle < 1e-3) pts.forEach((v, i) => v.addScaledVector(sideways, 0.04 * Math.sin(Math.PI * i / 32)));
        const curve = new THREE.CatmullRomCurve3(pts);
        const colour = new THREE.Color(WALK_COLOUR[a.colour]), opacity = 0.95 * fade(a.step) * (see ? 0.8 : 1);
        const f = a.conn.f_scale || 0, radius = f ? 0.0035 + 0.0016 * f : 0.005;
        const len = curve.getLength(), headLen = Math.min(0.07, len * 0.3), end = 1 - headLen / len;
        if (f) tube(curve, radius, colour, opacity, see, 0, end);
        else for (let i = 0; i < 10; i++) tube(curve, radius, colour, opacity, see, end * i / 10, end * (i + 0.55) / 10);
        if (a.conn.severity) {
          const glow = tube(curve, radius * 2.8, new THREE.Color(WALK_COLOUR.red), 0.32, see, 0, end);
          glow.material.blending = THREE.AdditiveBlending;
        }
        // Arrowheads: a big one at B, small ones along the way, so the direction is always clear.
        const both = a.conn.rel === 'SAME_CHEMICAL' || a.conn.rel === 'MISTAKEN_FOR';
        const heads = [[end, 1, headLen, 1], [0.38, 0.38 + 0.4 * headLen / len, headLen * 0.55, 1], [0.62, 0.62 + 0.4 * headLen / len, headLen * 0.55, 1]];
        if (both) heads.push([headLen / len, 0, headLen, 1]);
        for (const [t0, t1, h, sign] of heads) {
          const base = curve.getPointAt(t0), tip = curve.getPointAt(t1);
          const cone = new THREE.Mesh(new THREE.ConeGeometry(Math.max(radius * 3.2, h * 0.38), h, 14),
            new THREE.MeshBasicMaterial({ color: colour, transparent: true, opacity, depthTest: !see, depthWrite: false }));
          cone.position.copy(base.clone().add(tip).multiplyScalar(0.5));
          cone.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), tip.clone().sub(base).multiplyScalar(sign).normalize());
          group.add(cone);
        }
        const pick = new THREE.Mesh(new THREE.TubeGeometry(curve, 24, 0.02, 6, false), new THREE.MeshBasicMaterial({ visible: false }));
        pick.userData = arrowValue(a); group.add(pick); picks.push(pick);
      }
      for (const n of walk.nodes) {
        const p = at.get(n.slug); if (!p) continue;
        const under = n.place === 'underground';
        const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: iconTexture(n, n.slug === walk.start), sizeAttenuation: false,
          transparent: true, depthWrite: false, depthTest: !under, opacity: fade(n.step) }));
        sprite.center.set(0.5, 0.82); sprite.position.copy(p); sprite.userData = nodeValue(n); sprite.renderOrder = 7;
        group.add(sprite); sprites.push(sprite); picks.push(sprite);
        if (n.place === 'air' || n.place === 'orbit') {         // only the shells of the things on the walk
          const shell = new THREE.Mesh(new THREE.SphereGeometry(n.altitude, 64, 40), new THREE.MeshBasicMaterial({
            color: n.place === 'air' ? 0x5fc8ff : 0xffd36b, transparent: true, opacity: 0.045, side: THREE.DoubleSide, depthWrite: false }));
          group.add(shell);
        }
      }
    },
    resize(height, fov) {
      const s = 96 / height * 2 * Math.tan(THREE.MathUtils.degToRad(fov / 2));
      for (const sp of sprites) sp.scale.set(s * 2.667, s, 1);
    },
    pick(raycaster, camera) {
      for (const hit of raycaster.intersectObjects(picks, false)) {
        const o = hit.object;
        if (o.isSprite && o.material.depthTest && o.position.dot(camera.position) <= 0) continue;
        return o.userData;
      }
      return null;
    },
  };
}
