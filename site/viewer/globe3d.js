import * as THREE from 'three';
import { OrbitControls } from '../assets/three/OrbitControls.js';
import { W, H, lonLatToXYZ } from './geo.js';

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
  const planet = new THREE.Mesh(new THREE.SphereGeometry(1, 96, 64), new THREE.MeshBasicMaterial({ map: texture }));
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
  const raycaster = new THREE.Raycaster();
  let frame = null, pointerDown = false, start = null, tween = null, pointer = null;

  function resize() {
    const rect = canvas.getBoundingClientRect();
    if (!rect.width || !rect.height) return;
    renderer.setSize(rect.width, rect.height, false);
    camera.aspect = rect.width / rect.height;
    camera.updateProjectionMatrix();
    requestRender();
  }
  function hit(event) {
    const rect = canvas.getBoundingClientRect();
    const point = new THREE.Vector2((event.clientX - rect.left) / rect.width * 2 - 1, -(event.clientY - rect.top) / rect.height * 2 + 1);
    raycaster.setFromCamera(point, camera);
    const intersection = raycaster.intersectObject(planet)[0];
    return intersection ? world.districtAt(intersection.uv.x * W, (1 - intersection.uv.y) * H) : null;
  }
  function render(time) {
    frame = null;
    if (tween) {
      const t = Math.min(1, (time - tween.start) / 600), eased = t * t * (3 - 2 * t);
      const direction = tween.from.clone().lerp(tween.to, eased);
      if (direction.lengthSq() < 1e-8) direction.copy(tween.to);
      camera.position.copy(direction.normalize().multiplyScalar(tween.distance));
      if (t === 1) tween = null;
    }
    const changing = controls.update();
    renderer.render(scene, camera);
    if (pointer) { hover(hit(pointer), pointer); pointer = null; }
    if (changing || tween || pointerDown) requestRender();
  }
  function requestRender() { if (frame === null) frame = requestAnimationFrame(render); }
  controls.addEventListener('change', requestRender);
  canvas.addEventListener('pointerdown', event => {
    pointerDown = true; tween = null;
    start = { x: event.clientX, y: event.clientY, time: performance.now() }; requestRender();
  });
  canvas.addEventListener('pointermove', event => { pointer = event; requestRender(); });
  canvas.addEventListener('pointerleave', () => hover(null));
  canvas.addEventListener('pointercancel', () => { pointerDown = false; start = null; });
  canvas.addEventListener('pointerup', event => {
    pointerDown = false;
    if (start && performance.now() - start.time < 400 && Math.hypot(event.clientX - start.x, event.clientY - start.y) < 6) {
      const district = hit(event);
      if (district) select(district);
    }
    start = null; requestRender();
  });
  const observer = new ResizeObserver(resize);
  observer.observe(canvas.parentElement);
  resize();
  return {
    focus(territory, immediate = false) {
      const target = new THREE.Vector3(...lonLatToXYZ(territory.lon, territory.lat));
      if (immediate) { camera.position.copy(target.multiplyScalar(4.6)); tween = null; }
      else tween = { from: camera.position.clone().normalize(), to: target, distance: camera.position.length(), start: performance.now() };
      requestRender();
    },
    mark(territory) {
      marker.position.fromArray(lonLatToXYZ(territory.lon, territory.lat, 1.006));
      marker.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), marker.position.clone().normalize());
      marker.visible = true; requestRender();
    },
    zoom(factor) { camera.position.multiplyScalar(factor).clampLength(1.3, 12); requestRender(); },
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
