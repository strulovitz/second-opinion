// Programmer integration proof for the Opus 5.5 viewer (Amendment 3.6 + Part 7 additions).
// Not the human's multi-browser Checkpoint 7.1. Uses installed Chrome in an isolated,
// disposable profile. Entity data come ONLY from the labelled DEMO file (site/data/demo/).
// Run:  .venv/bin/python kitchen/open_globe.py --no-open && node kitchen/test_viewer_browser.mjs
import assert from 'node:assert/strict';
import { writeFile } from 'node:fs/promises';
import { browser, until } from './browser_cdp.mjs';

const base = process.env.VIEWER_URL || 'http://127.0.0.1:8765/viewer/';
const client = await browser();
const { send, evaluate } = client;
const results = [];
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
async function check(name, work) { await work(); results.push(name); console.log(`PASS ${name}`); }
const ready = () => until(() => evaluate("document.body.dataset.state === 'ready'"), 'viewer startup', 60000);
const shot = async name => { const { data } = await send('Page.captureScreenshot', { format: 'png' }); await writeFile(new URL(`./logs/opus-${name}.png`, import.meta.url), Buffer.from(data, 'base64')); };
const go = async (hash, route) => { await evaluate(`location.hash = ${JSON.stringify(hash)}`); await until(() => evaluate(`document.body.dataset.route === ${JSON.stringify(route)}`), hash); await delay(1200); };
async function click(point) {
  for (const type of ['mouseMoved', 'mousePressed', 'mouseReleased']) {
    await send('Input.dispatchMouseEvent', { type, x: point.x, y: point.y, button: 'left', clickCount: 1, pointerType: 'mouse' });
    await delay(60);
  }
  await delay(400);
}
const infoTitle = () => evaluate("document.querySelector('#info h2')?.textContent || ''");
try {
  await send('Emulation.setDeviceMetricsOverride', { width: 1400, height: 900, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url: base + '#/globe' }); await ready();

  await check('Goldberg globe starts in WebGL, aligned, with the real counts', async () => {
    assert.equal(await evaluate('document.body.dataset.mode'), '3d');
    assert.equal(await evaluate('document.body.dataset.alignment'), 'passed');
    assert.match(await evaluate("document.getElementById('counts').textContent"), /37 books.*4,763/);
    assert.equal(await evaluate('window.secondOpinion.world.tiles.length'), 4812);
    assert.ok(await evaluate("document.querySelectorAll('#labels .book:not([hidden])').length") > 5);
    await shot('sand-globe');
  });
  await check('Atlas and Sand table looks switch on the same tiles', async () => {
    await evaluate("document.getElementById('look-atlas').click()"); await delay(800);
    assert.equal(await evaluate("document.getElementById('stage').dataset.look"), 'atlas'); await shot('atlas-globe');
    await evaluate("document.getElementById('look-sand').click()"); await delay(800);
    assert.equal(await evaluate("document.getElementById('stage').dataset.look"), 'sand');
  });
  await check('clicking a chapter tile on the globe opens exactly that chapter', async () => {
    const id = await evaluate("window.secondOpinion.world.districts.filter(d => d.book_id === 'HARRISON-22')[20].territory_id");
    const name = await evaluate(`window.secondOpinion.world.byId.get(${JSON.stringify(id)}).name`);
    await evaluate(`window.secondOpinion.globe.focus(window.secondOpinion.world.byId.get(${JSON.stringify(id)}), true, 3)`); await delay(600);
    await click(await evaluate(`window.secondOpinion.globe.screenOf({territory_id:${JSON.stringify(id)}})`));
    await until(async () => (await infoTitle()) === name, 'district card after globe click');
  });
  await check('2-D flower map is centred on the viewed book and its tiles are clickable', async () => {
    await go('#/globe', 'globe');
    await evaluate("document.getElementById('view-2d').click()");
    await until(() => evaluate("document.body.dataset.mode === '2d' && !!window.secondOpinion.map.viewBook"), 'flower map');
    const id = await evaluate("window.secondOpinion.world.districts.find(d => d.book_id === window.secondOpinion.map.viewBook).territory_id");
    const name = await evaluate(`window.secondOpinion.world.byId.get(${JSON.stringify(id)}).name`);
    await click(await evaluate(`window.secondOpinion.map.screenOf(${JSON.stringify(id)})`));
    await until(async () => (await infoTitle()) === name, 'district card after flower click');
    await shot('flowers');
    await evaluate("document.getElementById('view-3d').click()"); await delay(600);
  });
  await check('DEMO entities show shells in 3-D with the banner, and the cascade works in 2-D', async () => {
    await evaluate("document.getElementById('demo').click()");
    await until(() => evaluate("!document.getElementById('demo-banner').hidden"), 'demo banner');
    for (const slug of ['demo-disease-c', 'demo-symptom-a', 'demo-treatment-f']) {
      await go(`#/map/${slug}/3d`, 'map3d');
      assert.match(await infoTitle(), /^DEMO /);
      await shot(`demo-${slug}`);
    }
    await go('#/map/demo-symptom-a', 'map');
    const spot = await evaluate('window.secondOpinion.map.firstSpot()');
    assert.ok(spot, 'a demo light is drawn on the flower map');
    await click(spot);
    await until(() => evaluate(`location.hash === ${JSON.stringify('#/map/' + spot.other_slug)}`), 'cascade to the other entity');
  });
  await check('Look inside and layers toggle without errors', async () => {
    await go('#/globe', 'globe');
    await evaluate("document.getElementById('cutaway').click()"); await delay(800); await shot('cutaway');
    await evaluate("document.getElementById('cutaway').click()"); await evaluate("document.getElementById('demo').click()"); await delay(500);
    assert.equal(await evaluate("document.getElementById('demo-banner').hidden"), true);
  });
  await check('phone layout never scrolls sideways', async () => {
    await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
    await send('Page.reload'); await ready(); await delay(800);
    assert.ok(await evaluate('document.documentElement.scrollWidth <= innerWidth + 1'));
    await shot('phone');
  });
  await check('without WebGL the viewer says so and shows the flower map', async () => {
    await send('Emulation.setDeviceMetricsOverride', { width: 1400, height: 900, deviceScaleFactor: 1, mobile: false });
    const { identifier } = await send('Page.addScriptToEvaluateOnNewDocument', { source: "const g = HTMLCanvasElement.prototype.getContext; HTMLCanvasElement.prototype.getContext = function (k, ...a) { return /webgl/.test(k) ? null : g.call(this, k, ...a); };" });
    await send('Page.reload'); await ready();
    assert.equal(await evaluate('document.body.dataset.mode'), '2d');
    assert.equal(await evaluate("document.getElementById('view-3d').disabled"), true);
    await send('Page.removeScriptToEvaluateOnNewDocument', { identifier });
  });
  assert.deepEqual(client.errors, [], 'no uncaught exceptions');
  await writeFile(new URL('./logs/opus-viewer-browser-results.json', import.meta.url), JSON.stringify({ passed: results }, null, 1));
  console.log(`${results.length} browser checks passed`);
} finally { await client.close(); }
