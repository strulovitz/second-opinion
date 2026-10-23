// Programmer integration proof, not the human's multi-browser Checkpoint 7.1.
// Synthetic entity data is injected into the isolated browser's fetch only.
import assert from 'node:assert/strict';
import { writeFile } from 'node:fs/promises';
import { browser, until } from './browser_cdp.mjs';

const base = process.env.VIEWER_URL || 'http://127.0.0.1:8765/viewer/';
const prefix = process.env.VIEWER_EVIDENCE_PREFIX || '';
const client = await browser();
const { send, evaluate: evaluate } = client;
const results = [];
async function check(name, work) { await work(); results.push(name); console.log(`PASS ${name}`); }
const ready = () => until(() => evaluate("document.body.dataset.state === 'ready'"), 'viewer startup');
const click = expression => evaluate(`${expression}.click()`);
const go = async hash => { await evaluate(`location.hash = ${JSON.stringify(hash)}`); await until(() => evaluate(`location.hash === ${JSON.stringify(hash)} && document.body.dataset.route === ${JSON.stringify(hash.includes('/map/') ? hash.endsWith('/3d') ? 'map3d' : 'map' : hash.includes('/district/') ? 'district' : 'globe')}`), hash); };
const screenshot = async name => { const { data } = await send('Page.captureScreenshot', { format: 'png' }); await writeFile(new URL(`./logs/${prefix}${name}.png`, import.meta.url), Buffer.from(data, 'base64')); };
const settleCamera = () => evaluate('new Promise(resolve => setTimeout(resolve, 750))');
const mapSpotPoint = () => evaluate(`(async () => {
  const world=await (await fetch('../data/geography/geography.json')).json();
  const d=world.find(t=>t.level==='district' && t.book_id==='HARRISON-22');
  const r=document.getElementById('map').getBoundingClientRect(), scale=Math.min(r.width/2048,r.height/1024);
  return {x:r.left+(r.width-2048*scale)/2+(d.lon+180)/360*2048*scale,y:r.top+(r.height-1024*scale)/2+(90-d.lat)/180*1024*scale};
})()`);
try {
  await send('Emulation.setDeviceMetricsOverride', { width: 1400, height: 950, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url: base + '#/globe' }); await ready();
  await check('real approved globe starts in WebGL with Harrison alignment', async () => {
    assert.equal(await evaluate('document.body.dataset.mode'), '3d');
    assert.equal(await evaluate('document.body.dataset.alignment'), 'passed');
    assert.match(await evaluate("document.getElementById('counts').textContent"), /37 books.*4,763/);
    assert.equal(await evaluate("!!document.getElementById('globe').getContext('webgl2')"), true);
    if (process.env.VIEWER_EXPECT_HONEYCOMB) {
      assert.deepEqual(await evaluate(`(async () => {
        const rows=await (await fetch('../data/geography/geography.json')).json();
        return [rows.filter(t=>t.tile_sides===6).length,rows.filter(t=>t.tile_sides===5).length];
      })()`), [4751, 12]);
    }
    await screenshot('viewer-real-globe');
    await go('#/district/C01'); await settleCamera();
    await screenshot('viewer-harrison-alignment');
    await go('#/globe');
  });
  await check('Three.js sphere UVs agree with shared projection at asymmetric points', async () => {
    assert.equal(await evaluate(`(async () => {
      const THREE = await import('three'); const geo = await import('./geo.js');
      const planet = new THREE.Mesh(new THREE.SphereGeometry(1,96,64)); const ray = new THREE.Raycaster();
      for (const [lon,lat] of [[0,0],[70,25],[-110,-30]]) {
        const v = new THREE.Vector3(...geo.lonLatToXYZ(lon,lat)); ray.set(v.clone().multiplyScalar(4),v.clone().negate());
        const hit=ray.intersectObject(planet)[0], [x,y]=geo.lonLatToPixel(lon,lat);
        if (!hit || Math.abs(hit.uv.x*2048-x)>1 || Math.abs((1-hit.uv.y)*1024-y)>1) return false;
      } planet.geometry.dispose(); planet.material.dispose(); return true;
    })()`), true);
  });
  const centre = await evaluate("(() => { const r=document.getElementById('globe').getBoundingClientRect(); return {x:r.left+r.width/2,y:r.top+r.height/2}; })()");
  await check('real globe click selects a raster district and home clears marker/card', async () => {
    await send('Input.dispatchMouseEvent', { type: 'mousePressed', ...centre, button: 'left', clickCount: 1 });
    await send('Input.dispatchMouseEvent', { type: 'mouseReleased', ...centre, button: 'left', clickCount: 1 });
    await until(() => evaluate('location.hash.startsWith("#/district/") && document.body.dataset.selected'), 'district click');
    assert.match(await evaluate("document.getElementById('info').textContent"), /Book:/);
    await click("document.getElementById('home')"); await until(() => evaluate('location.hash === "#/globe" && !document.body.dataset.selected'), 'home');
  });
  await check('drag does not click; specialty navigation, 2-D toggle and malformed routes work', async () => {
    await send('Input.dispatchMouseEvent', { type: 'mousePressed', ...centre, button: 'left', clickCount: 1 });
    await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: centre.x + 90, y: centre.y + 30, button: 'left', buttons: 1 });
    await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: centre.x + 90, y: centre.y + 30, button: 'left', clickCount: 1 });
    assert.equal(await evaluate('location.hash'), '#/globe');
    await evaluate("document.getElementById('book-search').value='Cardiology'; document.getElementById('book-search').dispatchEvent(new Event('input'))");
    assert.ok(await evaluate("document.querySelectorAll('#book-list a').length") > 0);
    await click("document.querySelector('#book-list a')"); await until(() => evaluate("document.getElementById('info').textContent.includes('Cardiology')"), 'specialty card');
    await click("document.getElementById('view-2d')"); assert.equal(await evaluate('document.body.dataset.mode'), '2d');
    await evaluate("location.hash = '#/district/%ZZ'"); await until(() => evaluate('location.hash === "#/globe"'), 'invalid hash normalization');
  });
  // Deliberately artificial fixtures; no real medical assertion and no site files written.
  const injection = `(() => {
    const realFetch = window.fetch.bind(window);
    const group='symptoms-and-signs', a='synthetic-alpha', b='synthetic-beta';
    let worldPromise;
    window.fetch = async (url, options) => {
      const path=new URL(String(url),location.href).pathname;
      if (!path.endsWith('/search.json') && !path.includes('/entities/synthetic-') && !path.includes('/districts/')) return realFetch(url,options);
      worldPromise ||= realFetch('../data/geography/geography.json').then(r=>r.json());
      const world=await worldPromise, d=world.find(t=>t.level==='district' && t.book_id==='HARRISON-22');
      const response = object => new Response(JSON.stringify(object),{status:200,headers:{'Content-Type':'application/json'}});
      const statement={book_id:'SYNTHETIC-TEST-NOT-A-BOOK',district_id:d.territory_id,district_name:d.name,page_number:7,quote:'Artificial browser test statement.',image_file:'synthetic.png',frequency_phrase:'synthetic wording',f_scale:0,severity:true};
      if (path.endsWith('/search.json')) return response([a,b].map((slug,i)=>({slug,group:i ? 'diseases-and-conditions':group,canonical_name:i?'Synthetic Beta':'Synthetic Alpha',aliases:i?[]:['Sýnthetic alias'],altitude:i?0.7:1.1,rank:1,lit_spot_count:1,edge_count:1,has_text:false})));
      if (path.includes('/entities/')) {
        const beta=path.includes(b), other=beta?a:b;
        return response({slug:beta?b:a,group:beta?'diseases-and-conditions':group,canonical_name:beta?'Synthetic Beta':'Synthetic Alpha',aliases:['Sýnthetic alias'],altitude:beta?0.7:1.1,ordering_value:1,books_total:1,lit_spots:[],edges:[{relation:'HARMS',direction:'out',subtype:null,other_slug:other,other_name:beta?'Synthetic Alpha':'Synthetic Beta',other_group:beta?group:'diseases-and-conditions',f_scale:0,severity:true,statements:[statement]}]});
      }
      return response({...d,entities:[{slug:a,canonical_name:'Synthetic Alpha',group,mentions:1,edges_here:1,pages:[7]}]});
    };
  })();`;
  await send('Page.addScriptToEvaluateOnNewDocument', { source: injection });
  await send('Page.reload'); await ready();
  await check('synthetic registry: accent-insensitive alias search, Enter and entity 2-D map', async () => {
    await evaluate("document.getElementById('search').value='synthetic alias'; document.getElementById('search').dispatchEvent(new KeyboardEvent('keydown',{key:'Enter'}))");
    await until(() => evaluate("document.getElementById('info').textContent.includes('Showing 1 lights')"), 'entity card');
    assert.equal(await evaluate('location.hash'), '#/map/synthetic-alpha/3d');
    await click("document.getElementById('view-2d')");
    await until(() => evaluate('document.body.dataset.mode === "2d"'), 'entity 2d');
    assert.match(await evaluate("document.getElementById('info').textContent"), /frequency not stated/);
    await screenshot('viewer-synthetic-map');
  });
  await check('synthetic edge card cascade and browser Back preserve entity routes', async () => {
    await click("document.getElementById('btn-fit')");
    const p = await mapSpotPoint();
    await send('Input.dispatchMouseEvent', { type: 'mouseMoved', ...p });
    await until(() => evaluate("!document.getElementById('tooltip').hidden && document.getElementById('tooltip').textContent.includes('SYNTHETIC-TEST-NOT-A-BOOK')"), 'spot provenance tooltip');
    await send('Input.dispatchMouseEvent', { type: 'mousePressed', ...p, button: 'left', clickCount: 1 });
    await send('Input.dispatchMouseEvent', { type: 'mouseReleased', ...p, button: 'left', clickCount: 1 });
    await until(() => evaluate("document.getElementById('info').textContent.includes('Synthetic Beta') && location.hash === '#/map/synthetic-beta'"), 'cascade');
    await evaluate('history.back()'); await until(() => evaluate("location.hash === '#/map/synthetic-alpha' && document.getElementById('info').textContent.includes('Synthetic Alpha')"), 'browser back');
    await click("document.getElementById('view-3d')");
    await until(() => evaluate('document.body.dataset.mode === "3d" && document.getElementById("info").textContent.includes("Altitude 1.100")'), 'entity shell');
    await settleCamera();
    await screenshot('viewer-synthetic-shell');
    await send('Input.dispatchMouseEvent', { type: 'mouseMoved', ...centre });
    await until(() => evaluate("!document.getElementById('tooltip').hidden && document.getElementById('tooltip').textContent.includes('Synthetic Beta')"), '3d spot tooltip');
    await send('Input.dispatchMouseEvent', { type: 'mousePressed', ...centre, button: 'left', clickCount: 1 });
    await send('Input.dispatchMouseEvent', { type: 'mouseReleased', ...centre, button: 'left', clickCount: 1 });
    await until(() => evaluate("location.hash === '#/map/synthetic-beta/3d'"), '3d spot cascade');
    await until(() => evaluate("document.getElementById('info').textContent.includes('Altitude 0.700')"), 'glass disease shell');
    await settleCamera();
    await screenshot('viewer-synthetic-glass');
  });
  await check('phone-sized layout has a working bottom sheet and no horizontal overflow', async () => {
    await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
    await until(() => evaluate("document.getElementById('globe').width === 390"), 'phone canvas resize');
    await settleCamera(); await screenshot('viewer-phone-globe');
    await click("document.getElementById('btn-panel')");
    assert.equal(await evaluate("document.getElementById('panel').classList.contains('open')"), true);
    assert.equal(await evaluate('document.documentElement.scrollWidth <= innerWidth'), true);
    await evaluate('new Promise(resolve => setTimeout(resolve, 220))');
    await screenshot('viewer-phone'); await click("document.getElementById('btn-panel')");
  });
  await check('touch first tap shows provenance, second tap follows the connection', async () => {
    await go('#/map/synthetic-alpha');
    await until(() => evaluate("document.getElementById('info').textContent.includes('Altitude 1.100')"), 'touch entity map');
    await click("document.getElementById('btn-fit')");
    await send('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 2 });
    const p = await mapSpotPoint();
    const tap = async () => { await send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ ...p, id: 1 }] }); await send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] }); };
    await tap();
    await until(() => evaluate("!document.getElementById('tooltip').hidden && !!document.querySelector('#tooltip a')"), 'touch tooltip');
    assert.equal(await evaluate('location.hash'), '#/map/synthetic-alpha');
    await tap(); await until(() => evaluate("location.hash === '#/map/synthetic-beta'"), 'second tap cascade');
  });
  await check('missing entity exports keep the geography usable with an explicit message', async () => {
    await go('#/map/not-an-exported-entity');
    await until(() => evaluate("document.getElementById('status').textContent.includes('not been built yet')"), 'missing export status');
    assert.match(await evaluate("document.getElementById('info').textContent"), /Entity data unavailable/);
  });
  await check('unavailable WebGL redirects entity shells to the working 2-D map', async () => {
    await send('Page.addScriptToEvaluateOnNewDocument', { source: `(() => {
      const original=HTMLCanvasElement.prototype.getContext;
      HTMLCanvasElement.prototype.getContext=function(kind,...args){return /webgl/.test(kind)?null:original.call(this,kind,...args)};
    })();` });
    await evaluate("location.hash = '#/map/synthetic-alpha/3d'; document.body.dataset.state='reloading'");
    await send('Page.reload', { ignoreCache: true }); await ready();
    assert.equal(await evaluate('document.body.dataset.mode'), '2d');
    assert.equal(await evaluate('location.hash'), '#/map/synthetic-alpha');
    assert.equal(await evaluate("document.getElementById('view-3d').disabled"), true);
    assert.match(await evaluate("document.getElementById('status').textContent"), /3-D view is not available/);
  });
  assert.deepEqual(client.errors, []);
  assert.deepEqual(client.events.filter(e => e.method === 'Network.loadingFailed' && !e.params.canceled), []);
  await writeFile(new URL(`./logs/${prefix}viewer-browser-results.json`, import.meta.url), JSON.stringify({ date: new Date().toISOString(), url: base, passed: results, exceptions: client.errors }, null, 2) + '\n');
} finally { await client.close(); }
