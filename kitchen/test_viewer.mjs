import test from 'node:test';
import assert from 'node:assert/strict';
import { lonLatToPixel, pixelToLonLat, lonLatToXYZ, radiusPx, sunflower, spotsFor, parseRoute, normalize } from '../site/viewer/geo.js';

test('shared projection preserves east, north, seam and inverse coordinates', () => {
  assert.deepEqual(lonLatToPixel(-180, 90), [0, 0]);
  assert.deepEqual(lonLatToPixel(180, -90), [2048, 1024]);
  for (const [lon, lat] of [[0, 0], [71.5, -33.2], [-179.9, 89]]) {
    const result = pixelToLonLat(...lonLatToPixel(lon, lat));
    assert.ok(Math.abs(result[0] - lon) < 1e-10 && Math.abs(result[1] - lat) < 1e-10);
  }
  assert.deepEqual(lonLatToXYZ(0, 0), [1, 0, -0]);
  assert.ok(Math.abs(lonLatToXYZ(90, 0)[2] + 1) < 1e-10);
  assert.ok(Math.abs(lonLatToXYZ(0, 90)[1] - 1) < 1e-10);
});

test('district-specific F/severity cannot leak from another district', () => {
  const world = { byId: new Map(['A', 'B', 'C'].map((id, i) => [id, { lon: i * 10, lat: i }])) };
  const entity = { edges: [{ relation: 'HARMS', other_slug: 'synthetic-b', direction: 'out', f_scale: 5, severity: true,
    statements: [{ district_id: 'A', f_scale: 0, severity: false }, { district_id: 'B', f_scale: 5, severity: true }] }],
    lit_spots: [{ district_id: 'A', book_id: 'SYNTHETIC', pages: [1] }, { district_id: 'C', book_id: 'SYNTHETIC', pages: [2] }] };
  const result = spotsFor(entity, world);
  assert.equal(result.length, 3);
  const a = result.find(s => s.district_id === 'A');
  assert.equal(a.f, 0); assert.equal(a.dashed, true); assert.equal(a.severity, false);
  assert.equal(result.find(s => s.district_id === 'C').lit, true);
  assert.equal(result.at(-1).severity, true);
});

test('overlapping connections retain deterministic offsets and separate directions', () => {
  const world = { byId: new Map([['D', { lon: 0, lat: 0 }]]) };
  const make = (relation, other_slug) => ({ relation, other_slug, statements: [{ district_id: 'D', f_scale: 2 }] });
  const entity = { edges: [make('HARMS', 'z'), make('PRESENTS_WITH', 'a')] };
  const spots = spotsFor(entity, world);
  assert.equal(spots[0].colour, 'blue'); assert.notDeepEqual(spots[0].offset, spots[1].offset);
  assert.deepEqual(spots, spotsFor(entity, world));
  assert.deepEqual(sunflower(0, 1, 10), [0, 0]);
  assert.equal(radiusPx(0), radiusPx(3)); assert.ok(radiusPx(5) > radiusPx(1));
});

test('routes handle Back-compatible forms and malformed escapes without crashing', () => {
  assert.deepEqual(parseRoute('#/map/test-slug/3d'), { route: 'map3d', slug: 'test-slug' });
  assert.deepEqual(parseRoute('#/district/C01.P01.D001'), { route: 'district', territoryId: 'C01.P01.D001' });
  for (const hash of ['#/district/%ZZ', '#/map/a/extra', '#/unknown', '#junk/map/slug', '']) assert.equal(parseRoute(hash).route, 'globe');
  assert.equal(normalize('FÉVER'), 'fever');
});
