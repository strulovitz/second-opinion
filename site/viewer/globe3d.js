import * as THREE from 'three';
import { OrbitControls } from '../assets/three/OrbitControls.js';
import { W, H, lonLatToXYZ, radiusPx, drawSpot } from './geo.js';

export async function createGlobe(canvas, world, select, hover) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.setClearColor('#0b0f1a');
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(40, 1, 0.01, 100);
  camera.position.fromArray(lonLatToXYZ(0, 15, 4.6));
  const controls = new OrbitControls(camera, canvas);
  Object.assign(controls, { enableDamping: true, dampingFactor: 0.08, minDistance: 1.3, maxDistance: 12, enablePan: false });
  const small = renderer.capabilities.maxTextureSize < 4096 || innerWidth < 900;
  const texture = await new THREE.TextureLoader().loadAsync(world.textureURL(small));
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = renderer.capabilities.getMaxAnisotropy();
  const planet = new THREE.Mesh(new THREE.SphereGeometry(1, 96, 64), new THREE.MeshBasicMaterial({ map: texture, transparent: true }));
  scene.add(planet);
  const guides = new THREE.Group();
  for (const radius of [1.5, 1.8, 2.1, 2.4, 2.7, 3.0]) {
    guides.add(new THREE.Mesh(new THREE.SphereGeometry(radius, 48, 32),
      new THREE.MeshBasicMaterial({ wireframe: true, transparent: true, opacity: 0.07, color: 0xffffff, depthWrite: false })));
  }
  guides.visible = false;
  scene.add(guides);
  const marker = new THREE.Mesh(new THREE.TorusGeometry(0.017, 0.003, 8, 32), new THREE.MeshBasicMaterial({ color: 0xffffff }));
  marker.visible = false;
  scene.add(marker);
  const shell = new THREE.Group(); scene.add(shell);
  const spriteTextures = new Map();
  let sprites = [], activeEntity = null, highlighted = null;
  const raycaster = new THREE.Raycaster();
  let frame = null, start = null, tween = null, pointer = null;
  const pointers = new Set();
  function fitDistance(radius = Math.max(1, activeEntity?.altitude || 1)) {
    const rect = canvas.getBoundingClientRect();
    const halfFov = THREE.MathUtils.degToRad(camera.fov / 2);
    const angle = Math.min(halfFov, Math.atan(Math.tan(halfFov) * (rect.width / rect.height || 1)));
    return Math.min(12, Math.max(4.6, radius / Math.sin(angle) * 1.1));
  }
  function spriteSize() {
    const height = canvas.getBoundingClientRect().height || 1;
    for (const sprite of sprites) {
      // Canvas texture includes the severity/hover ring and transparent margin.
      const size = 40 / height * 2 * Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
      sprite.scale.set(size, size, 1);
    }
  }

  function resize() {
    const rect = canvas.getBoundingClientRect();
    if (!rect.width || !rect.height) return;
    renderer.setSize(rect.width, rect.height, false);
    const narrower = rect.width / rect.height < camera.aspect;
    camera.aspect = rect.width / rect.height;
    camera.updateProjectionMatrix();
    if (narrower) {
      const distance = fitDistance();
      camera.position.clampLength(distance, 12);
      if (tween) tween.distance = Math.max(distance, tween.distance);
    }
    spriteSize();
    requestRender();
  }
  function hit(event) {
    const rect = canvas.getBoundingClientRect();
    const point = new THREE.Vector2((event.clientX - rect.left) / rect.width * 2 - 1, -(event.clientY - rect.top) / rect.height * 2 + 1);
    raycaster.setFromCamera(point, camera);
    const intersection = raycaster.intersectObject(planet)[0];
    for (const result of raycaster.intersectObjects(sprites)) {
      const sprite = result.object, spot = sprite.userData;
      if (sprite.position.dot(camera.position) <= 0) continue;
      if (activeEntity?.altitude >= 1 && intersection && result.distance > intersection.distance) continue;
      // Raycaster tests the sprite's square; reject the transparent corners.
      const radius = (spot.lit ? 8 : radiusPx(spot.f) + 6) / 40;
      if (Math.hypot(result.uv.x - 0.5, result.uv.y - 0.5) <= radius) return spot;
    }
    return intersection ? world.districtAt(intersection.uv.x * W, (1 - intersection.uv.y) * H) : null;
  }
  function render(time) {
    frame = null;
    if (tween) {
      const t = Math.min(1, (time - tween.start) / 600), eased = t * t * (3 - 2 * t);
      const rotation = new THREE.Quaternion().slerp(tween.rotation, eased);
      const direction = tween.from.clone().applyQuaternion(rotation);
      camera.position.copy(direction.normalize().multiplyScalar(tween.distance));
      if (t === 1) tween = null;
    }
    const changing = controls.update();
    if (!canvas.hidden) renderer.render(scene, camera);
    if (pointer) { hover(hit(pointer), pointer); pointer = null; }
    if (!canvas.hidden && (changing || tween || pointers.size)) requestRender();
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
  canvas.addEventListener('pointerleave', () => hover(null));
  canvas.addEventListener('pointercancel', event => { pointers.delete(event.pointerId); start = null; });
  canvas.addEventListener('lostpointercapture', event => { pointers.delete(event.pointerId); start = null; });
  canvas.addEventListener('pointerup', event => {
    pointers.delete(event.pointerId);
    if (start && !start.moved && performance.now() - start.time < 400 && Math.hypot(event.clientX - start.x, event.clientY - start.y) < 6) {
      const district = hit(event);
      if (district) select(district, event);
    }
    start = null; requestRender();
  });
  const observer = new ResizeObserver(resize);
  observer.observe(canvas.parentElement);
  resize();
  function focus(territory, immediate = false, distance = camera.position.length()) {
      // Consume residual damping before starting a programmatic camera move.
      controls.enableDamping = false; controls.update(); controls.enableDamping = true;
      const target = new THREE.Vector3(...lonLatToXYZ(territory.lon, territory.lat));
      if (immediate) distance = Math.max(distance, fitDistance());
      if (immediate || matchMedia('(prefers-reduced-motion: reduce)').matches) { camera.position.copy(target.multiplyScalar(distance)); tween = null; }
      else {
        const from = camera.position.clone().normalize();
        tween = { from, rotation: new THREE.Quaternion().setFromUnitVectors(from, target), distance, start: performance.now() };
      }
      requestRender();
  }
  function clearShell() {
    for (const object of [...shell.children]) {
      shell.remove(object); object.geometry?.dispose(); object.material?.dispose();
    }
    sprites = []; activeEntity = null; highlighted = null;
    planet.material.opacity = 1; planet.material.depthWrite = true; controls.minDistance = 1.3;
  }
  function spotTexture(spot, highlight = false) {
    const key = [spot.lit, spot.colour, spot.f, spot.dashed, spot.severity, highlight].join(':');
    if (!spriteTextures.has(key)) {
      const image = document.createElement('canvas'); image.width = image.height = 80;
      const context = image.getContext('2d'); context.scale(2, 2); drawSpot(context, spot, 20, 20, highlight);
      const texture = new THREE.CanvasTexture(image); texture.colorSpace = THREE.SRGBColorSpace;
      spriteTextures.set(key, texture);
    }
    return spriteTextures.get(key);
  }
  return {
    focus,
    mark(territory) {
      if (!territory) { marker.visible = false; requestRender(); return; }
      marker.position.fromArray(lonLatToXYZ(territory.lon, territory.lat, 1.006));
      marker.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), marker.position.clone().normalize());
      marker.visible = true; requestRender();
    },
    zoom(factor) { tween = null; camera.position.multiplyScalar(factor).clampLength(controls.minDistance, 12); requestRender(); },
    fit() { focus({ lon: 0, lat: 15 }, false, fitDistance()); },
    home(territory) { focus(territory, false, fitDistance()); },
    showGlobe() { clearShell(); marker.visible = false; requestRender(); },
    showShell(entity, spots) {
      clearShell(); marker.visible = false;
      if (!Number.isFinite(entity.altitude) || entity.altitude <= 0 || entity.altitude > 3) throw new Error('This entity has no valid exported altitude yet');
      activeEntity = entity;
      const tint = { 'symptoms-and-signs': 0x2fae6a, 'diseases-and-conditions': 0xc0533a, 'treatments-and-drugs': 0x4a6bd6 };
      shell.add(new THREE.Mesh(new THREE.SphereGeometry(entity.altitude, 64, 48),
        new THREE.MeshBasicMaterial({ transparent: true, opacity: 0.10, color: tint[entity.group], side: THREE.DoubleSide, depthWrite: false })));
      planet.material.opacity = entity.altitude < 1 ? 0.35 : 1;
      planet.material.depthWrite = entity.altitude >= 1;
      controls.minDistance = Math.max(1.3, entity.altitude + 0.15);
      for (const spot of spots) {
        const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: spotTexture(spot), sizeAttenuation: false, depthTest: true, depthWrite: false }));
        const lat = THREE.MathUtils.degToRad(spot.lat), lon = THREE.MathUtils.degToRad(spot.lon);
        sprite.position.fromArray(lonLatToXYZ(spot.lon, spot.lat, entity.altitude));
        const east = new THREE.Vector3(-Math.sin(lon), 0, -Math.cos(lon));
        const north = new THREE.Vector3(-Math.sin(lat) * Math.cos(lon), Math.cos(lat), Math.sin(lat) * Math.sin(lon));
        sprite.position.addScaledVector(east, spot.offset[0] / 400).addScaledVector(north, -spot.offset[1] / 400);
        sprite.userData = spot; shell.add(sprite); sprites.push(sprite);
      }
      spriteSize();
      const target = [...spots].sort((a, b) => (b.f ?? -1) - (a.f ?? -1))[0] || { lon: 0, lat: 15 };
      focus(target, false, Math.max(camera.position.length(), entity.altitude + 1.8, fitDistance()));
      requestRender();
    },
    highlight(slug) {
      highlighted = slug;
      for (const sprite of sprites) sprite.material.map = spotTexture(sprite.userData, highlighted === sprite.userData.other_slug);
      requestRender();
    },
    guides(show) { guides.visible = show; requestRender(); },
    resize,
    alignment(territory) {
      const direction = new THREE.Vector3(...lonLatToXYZ(territory.lon, territory.lat));
      raycaster.set(direction.clone().multiplyScalar(4), direction.clone().negate());
      const intersection = raycaster.intersectObject(planet)[0];
      return intersection && world.districtAt(intersection.uv.x * W, (1 - intersection.uv.y) * H)?.book_id === territory.book_id;
    },
  };
}
