// Opus 5.5 addition: the one tile shader shared by the Atlas globe and the Sand table.
// Per-vertex attributes (all built in atlas.js / sandtable.js):
//   color  linear RGB of the tile        edge  1 at the tile centre -> 0 on its outer side,
//   tile   tile index (honeycomb order)        -1 on column walls (no lines drawn there)
//   book   book index (geography order)  line  0 same Part, 1 Part (province) border, 2 book border
// Lines are drawn with screen-space derivatives, so they stay a constant number of
// pixels wide at every zoom: no texture, no blur, no stretching anywhere on the ball.
import * as THREE from 'three';

const vertexShader = /* glsl */`
  attribute float edge; attribute float tile; attribute float book; attribute float line;
  varying vec3 vColor; varying vec3 vNormalW; varying vec3 vWorld;
  varying float vEdge; varying float vTile; varying float vBook; varying float vLine;
  #include <clipping_planes_pars_vertex>
  void main() {
    vColor = color; vEdge = edge; vTile = tile; vBook = book; vLine = line;
    vec4 world = modelMatrix * vec4(position, 1.0);
    vWorld = world.xyz; vNormalW = normalize(mat3(modelMatrix) * normal);
    vec4 mvPosition = viewMatrix * world;
    gl_Position = projectionMatrix * mvPosition;
    #include <clipping_planes_vertex>
  }`;

const fragmentShader = /* glsl */`
  uniform vec3 uLight; uniform float uHover; uniform float uHoverBook; uniform float uSelected;
  uniform float uOpacity; uniform float uToon; uniform float uTime; uniform vec3 uBorder; uniform vec3 uRim;
  varying vec3 vColor; varying vec3 vNormalW; varying vec3 vWorld;
  varying float vEdge; varying float vTile; varying float vBook; varying float vLine;
  #include <clipping_planes_pars_fragment>
  void main() {
    #include <clipping_planes_fragment>
    vec3 n = normalize(vNormalW);
    float ndl = max(dot(n, uLight), 0.0);
    float lit = uToon > 0.5 ? (ndl > 0.6 ? 1.06 : ndl > 0.2 ? 0.84 : 0.62) : 0.40 + 0.70 * ndl;
    vec3 c = vColor * lit;
    vec3 toEye = normalize(cameraPosition - vWorld);
    float rim = pow(1.0 - max(dot(n, toEye), 0.0), 3.0);
    c += uRim * rim;
    if (abs(vBook - uHoverBook) < 0.5) c *= 1.10;
    if (abs(vTile - uHover) < 0.5) c = mix(c, vec3(1.0), 0.38);
    if (vEdge >= 0.0) {
      float w = max(fwidth(vEdge), 1e-4);
      c *= 0.80 + 0.20 * smoothstep(0.0, 0.30, vEdge);              // soft bevel: tiles look raised
      c = mix(c, c * 0.38, (1.0 - smoothstep(0.5 * w, 1.5 * w, vEdge)) * 0.85);  // thin grout
      if (vLine > 0.5 && vLine < 1.5) c = mix(c, c * 0.55 + vec3(0.06), 1.0 - smoothstep(1.0 * w, 2.0 * w, vEdge));
      if (vLine > 1.5) c = mix(c, uBorder, 1.0 - smoothstep(1.6 * w, 2.8 * w, vEdge));
      if (abs(vTile - uSelected) < 0.5) {
        float ring = 1.0 - smoothstep(2.0 * w, 4.5 * w, vEdge);
        c = mix(c, vec3(1.0, 0.95, 0.55), ring * 0.9);
      }
    } else {
      if (uOpacity < 0.99) discard;                 // glass planet: column walls vanish, tops stay
      if (abs(vTile - uHover) < 0.5) c = mix(c, vec3(1.0), 0.25);
    }
    gl_FragColor = vec4(c, uOpacity);
    #include <colorspace_fragment>
  }`;

export function tileMaterial({ toon = false, border = '#fff8e6', rim = '#2e5d9c', rimStrength = 0.35 } = {}) {
  const material = new THREE.ShaderMaterial({
    vertexShader, fragmentShader, vertexColors: true, clipping: true, transparent: true,
    uniforms: {
      uLight: { value: new THREE.Vector3(0, 0, 1) }, uHover: { value: -1 }, uHoverBook: { value: -1 },
      uSelected: { value: -1 }, uOpacity: { value: 1 }, uToon: { value: toon ? 1 : 0 }, uTime: { value: 0 },
      uBorder: { value: new THREE.Color(border) }, uRim: { value: new THREE.Color(rim).multiplyScalar(rimStrength) },
    },
  });
  return material;
}

// Linear-space colour of a tile, from the territory colours in geography.json.
export function tileColour(world, tile, variant = 'atlas') {
  const colour = new THREE.Color();
  if (tile.kind === 'pole') return colour.set(variant === 'sand' ? '#3d8fd8' : '#2f6fb8');   // the 12 pentagons: little lakes
  if (tile.kind === 'name') return colour.set(world.books[tile.book].colour_hex).lerp(new THREE.Color('#ffffff'), 0.55);
  return colour.set(tile.territory.colour_hex);
}

// Which kind of line sits on the side between tile a and its neighbour b.
export function lineKind(a, b) {
  if (a.kind === 'pole' || b?.kind === 'pole') return 0;
  if (!b || a.book !== b.book) return 2;
  const pa = a.kind === 'district' ? a.territory.parent : null, pb = b.kind === 'district' ? b.territory.parent : null;
  return pa && pb && pa !== pb ? 1 : 0;
}

// Fresnel glow for atmospheres and entity shells.
export function glowMaterial(colour, { power = 2.5, strength = 1, opacity = 1, side = THREE.BackSide, additive = true } = {}) {
  return new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, side, clipping: true,
    blending: additive ? THREE.AdditiveBlending : THREE.NormalBlending,
    uniforms: { uColour: { value: new THREE.Color(colour) }, uPower: { value: power }, uStrength: { value: strength }, uOpacity: { value: opacity } },
    vertexShader: /* glsl */`
      varying vec3 vN; varying vec3 vW;
      #include <clipping_planes_pars_vertex>
      void main() { vN = normalize(mat3(modelMatrix) * normal); vec4 w = modelMatrix * vec4(position, 1.0); vW = w.xyz;
        vec4 mvPosition = viewMatrix * w; gl_Position = projectionMatrix * mvPosition;
        #include <clipping_planes_vertex>
      }`,
    fragmentShader: /* glsl */`
      uniform vec3 uColour; uniform float uPower; uniform float uStrength; uniform float uOpacity;
      varying vec3 vN; varying vec3 vW;
      #include <clipping_planes_pars_fragment>
      void main() {
        #include <clipping_planes_fragment>
        float f = pow(1.0 - abs(dot(normalize(vN), normalize(cameraPosition - vW))), uPower);
        gl_FragColor = vec4(uColour * f * uStrength, f * uOpacity);
        #include <colorspace_fragment>
      }`,
  });
}
