export const W = 2048, H = 1024;

export function lonLatToPixel(lon, lat) {
  return [(lon + 180) / 360 * W, (90 - lat) / 180 * H];
}

export function pixelToLonLat(x, y) {
  return [x / W * 360 - 180, 90 - y / H * 180];
}

export function districtCode(imageData, px, py) {
  const x = Math.max(0, Math.min(W - 1, Math.floor(px)));
  const y = Math.max(0, Math.min(H - 1, Math.floor(py)));
  const k = (y * W + x) * 4;
  return imageData.data[k] * 256 + imageData.data[k + 1];
}

export function lonLatToXYZ(lon, lat, radius = 1) {
  const la = lat * Math.PI / 180, lo = lon * Math.PI / 180;
  return [radius * Math.cos(la) * Math.cos(lo), radius * Math.sin(la), -radius * Math.cos(la) * Math.sin(lo)];
}
