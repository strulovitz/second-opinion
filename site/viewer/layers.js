// Opus 5.5 addition: the layers above and below the map (BIBLE Part 1 section 3.3).
//  - showShell(entity, spots): one entity = one shell at its frozen altitude, with a
//    light ("bead") at every district where the books connect it to something.
//    Radius = entity.altitude, direction = the district's tile centre. NEVER invent
//    either: both come from the exported data (or the clearly labelled demo file).
//  - cutaway(on): opens a wedge of the planet towards the viewer and shows the
//    disease strata inside (deep = multisystem, near the crust = local).
import * as THREE from 'three';
import { radiusPx, drawSpot, COLOUR, GROUP_TINT, BANDS } from './geo.js';
import { glowMaterial } from './materials.js';

function spotCanvas(spot, highlight, bead) {
  const image = document.createElement('canvas'); image.width = image.height = 96;
  const c = image.getContext('2d'); c.scale(2, 2);
  const r = spot.lit ? 3 : radiusPx(spot.f);
  const glow = c.createRadialGradient(24, 24, r * 0.5, 24, 24, r + 10);
  glow.addColorStop(0, spot.lit ? 'rgba(255,255,255,.35)' : `${COLOUR[spot.colour]}aa`); glow.addColorStop(1, 'rgba(0,0,0,0)');
  c.fillStyle = glow; c.fillRect(0, 0, 48, 48);
  drawSpot(c, spot, 24, 24, highlight);
  if (bead && !spot.lit && !spot.dashed) {             // a shiny highlight turns the circle into a bead
    const shine = c.createRadialGradient(24 - r * 0.35, 24 - r * 0.4, 0, 24 - r * 0.35, 24 - r * 0.4, r * 0.8);
    shine.addColorStop(0, 'rgba(255,255,255,.75)'); shine.addColorStop(1, 'rgba(255,255,255,0)');
    c.fillStyle = shine; c.beginPath(); c.arc(24, 24, r, 0, Math.PI * 2); c.fill();
  }
  const texture = new THREE.CanvasTexture(image); texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

export function createLayers(scene, world) {
  const shell = new THREE.Group(); scene.add(shell);
  const textures = new Map();
  let sprites = [], active = null, bead = false;
  const texture = (spot, highlight) => {
    const key = [spot.lit, spot.colour, spot.f, spot.dashed, spot.severity, highlight, bead].join(':');
    if (!textures.has(key)) textures.set(key, spotCanvas(spot, highlight, bead));
    return textures.get(key);
  };
  // ---- interior strata (cutaway) ----
  const interior = new THREE.Group(); interior.visible = false; scene.add(interior);
  const capMaterial = new THREE.ShaderMaterial({
    side: THREE.DoubleSide, uniforms: { uColours: { value: [0, 1, 2, 3, 4].map(() => new THREE.Color()) } },
    vertexShader: 'varying vec3 vP; void main(){ vP = position; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
    fragmentShader: /* glsl */`
      uniform vec3 uColours[5]; varying vec3 vP;
      void main() {
        float r = length(vP.xy);
        float k = clamp((r - 0.0) / 1.0, 0.0, 0.9999) * 4.0;
        int i = int(floor(k)); float f = fract(k);
        vec3 a = uColours[0]; vec3 b = uColours[1];
        if (i == 1) { a = uColours[1]; b = uColours[2]; } else if (i == 2) { a = uColours[2]; b = uColours[3]; } else if (i >= 3) { a = uColours[3]; b = uColours[4]; }
        vec3 c = mix(a, b, smoothstep(0.0, 1.0, f));
        float bands = 1.0;
        for (int j = 0; j < 4; j++) bands -= 0.35 * (1.0 - smoothstep(0.0, 0.006, abs(r - (0.30 + 0.17 * float(j)))));
        c = mix(c, c * 0.55, smoothstep(0.975, 0.99, r));    // the crust
        gl_FragColor = vec4(c * bands, 1.0);
        #include <colorspace_fragment>
      }`,
  });
  const caps = [0, 1].map(() => { const m = new THREE.Mesh(new THREE.CircleGeometry(1, 96, -Math.PI / 2, Math.PI), capMaterial); interior.add(m); return m; });
  const planes = [new THREE.Plane(), new THREE.Plane()];
  let cut = false;
  function updateCut(camera) {
    if (!cut) return;
    const v = camera.position.clone().normalize();
    const up = new THREE.Vector3(0, 1, 0).addScaledVector(v, -v.y).normalize();
    const side = new THREE.Vector3().crossVectors(up, v).normalize();
    const half = Math.PI / 4;
    [1, -1].forEach((sign, i) => {
      const d = v.clone().multiplyScalar(Math.cos(half)).addScaledVector(side, sign * Math.sin(half));
      const m = new THREE.Vector3().crossVectors(up, d).normalize();
      if (m.dot(v) < 0) m.negate();                   // m points into the removed wedge
      planes[i].set(m.clone().negate(), 0);           // keep n.p >= 0; clipIntersection removes the wedge
      const normal = new THREE.Vector3().crossVectors(d, up).normalize();
      caps[i].matrix.makeBasis(d, up, normal); caps[i].matrixAutoUpdate = false; caps[i].matrixWorldNeedsUpdate = true;
    });
  }
  return {
    planes,
    setBead(on) { bead = on; },
    setInteriorPalette(colours) { colours.forEach((c, i) => capMaterial.uniforms.uColours.value[i].set(c)); },
    cutaway(on, camera) { cut = on; interior.visible = on; updateCut(camera); return on ? planes : null; },
    update(camera) {
      updateCut(camera);
      // Inside the glass planet, lights on the far side of the shell would show through: hide them.
      if (active && active.altitude < 1) { const view = camera.position.clone().normalize(); for (const s of sprites) s.visible = s.position.dot(view) > -0.02; }
    },
    get active() { return active; },
    clear() {
      for (const o of [...shell.children]) { shell.remove(o); o.geometry?.dispose(); if (!o.isSprite) o.material?.dispose(); }
      sprites = []; active = null;
    },
    show(entity, spots, heightOf) {
      this.clear(); active = entity;
      const tint = GROUP_TINT[entity.group] || '#ffffff';
      const sphere = new THREE.Mesh(new THREE.SphereGeometry(entity.altitude, 96, 64), glowMaterial(tint, { power: 2.2, strength: 0.7, opacity: 0.55, side: THREE.DoubleSide, additive: true }));
      shell.add(sphere);
      for (const spot of spots) {
        const tile = world.tileOf.get(spot.district_id);
        const n = new THREE.Vector3(...(tile ? tile.centre : [1, 0, 0])).normalize();
        const up = Math.abs(n.y) < 0.95 ? new THREE.Vector3(0, 1, 0) : new THREE.Vector3(1, 0, 0);
        const east = new THREE.Vector3().crossVectors(up, n).normalize(), north = new THREE.Vector3().crossVectors(n, east);
        const r = entity.altitude >= 1 ? Math.max(entity.altitude, heightOf(tile) + 0.004) : entity.altitude;
        const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: texture(spot, false), sizeAttenuation: false, depthWrite: false, transparent: true }));
        sprite.position.copy(n).multiplyScalar(r).addScaledVector(east, spot.offset[0] / 400).addScaledVector(north, -spot.offset[1] / 400);
        sprite.userData = { spot, tile }; sprite.renderOrder = 5; shell.add(sprite); sprites.push(sprite);
      }
    },
    resize(height, fov) {
      const size = 48 / height * 2 * Math.tan(THREE.MathUtils.degToRad(fov / 2));
      for (const s of sprites) s.scale.set(size, size, 1);
    },
    highlight(slug) { for (const s of sprites) s.material.map = texture(s.userData.spot, slug && s.userData.spot.other_slug === slug); },
    pick(raycaster, camera, surfaceHit) {
      for (const result of raycaster.intersectObjects(sprites)) {
        const s = result.object, spot = s.userData.spot;
        if (s.position.dot(camera.position) <= 0) continue;
        if (active.altitude >= 1 && surfaceHit && result.distance > surfaceHit.distance) continue;
        const radius = (spot.lit ? 8 : radiusPx(spot.f) + 6) / 48;
        if (Math.hypot(result.uv.x - 0.5, result.uv.y - 0.5) <= radius) return s.userData;
      }
      return null;
    },
    bands: BANDS,
  };
}
