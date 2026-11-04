// SITE FOLDER LAW proof (BIBLE Part 9 section 9.S): a FRESH CLONE from GitHub is a working website.
// Run (from any folder):
//   rm -rf /tmp/opencode/so-test && git clone https://github.com/strulovitz/second-opinion.git /tmp/opencode/so-test
//   (cd /tmp/opencode/so-test/site && python3 -m http.server 8799 &) ; node /tmp/opencode/so-test/kitchen/test_published_clone.mjs
// It searches "hernia" in #search, opens the first result and saves a 3-D screenshot with the columns.
import assert from 'node:assert/strict';
import { writeFile } from 'node:fs/promises';
import { browser, until } from './browser_cdp.mjs';

const base = process.env.VIEWER_URL || 'http://127.0.0.1:8799/viewer/';
const shotFile = process.env.SHOT || '/tmp/opencode/fresh-clone-hernia.png';
const client = await browser();
const { send, evaluate } = client;
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
try {
  await send('Emulation.setDeviceMetricsOverride', { width: 1400, height: 900, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url: base + '#/globe' });
  await until(() => evaluate("document.body.dataset.state === 'ready'"), 'viewer startup', 60000);
  await evaluate("document.querySelector('[data-group=\"diseases-and-conditions\"]')?.click()");
  await evaluate("(() => { const s = document.getElementById('search'); s.value = 'hernia'; s.dispatchEvent(new Event('input')); })()");
  await delay(800);   // the search box waits 120 ms after typing before it filters
  await until(() => evaluate("document.querySelectorAll('#results a').length > 0"), 'search results for hernia', 30000);
  const n = await evaluate("document.querySelectorAll('#results a').length");
  const pick = "[...document.querySelectorAll('#results a')].find(a => /hernia/i.test(a.textContent))";
  const first = await evaluate(`${pick}.textContent`);
  console.log(`PASS search "hernia": ${n} results, first hernia result = ${first.trim().slice(0, 80)}`);
  await evaluate(`${pick}.click()`);
  await until(() => evaluate("(document.querySelector('#info h2')?.textContent || '').length > 0"), 'entity card', 30000);
  await delay(2500);
  console.log(`PASS opened: ${await evaluate("document.querySelector('#info h2').textContent")}; mode=${await evaluate('document.body.dataset.mode')}`);
  const { data } = await send('Page.captureScreenshot', { format: 'png' });
  await writeFile(shotFile, Buffer.from(data, 'base64'));
  console.log(`screenshot: ${shotFile}`);
  assert.equal(client.errors.length, 0, JSON.stringify(client.errors));
} finally { await client.close(); }
