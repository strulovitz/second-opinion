import * as data from './data.js';
import { createMap } from './map2d.js';
import { normalize, parseRoute, spotsFor } from './geo.js';
import { text, link, groups, mapURL, districtURL, intro, entityCard, districtCard, tooltipContent, legend } from './ui.js';

const $ = id => document.getElementById(id);
const state = { route: 'globe', slug: null, entity: null, territoryId: null, hover: null, group: groups[0], query: '' };
let world, rows = [], wording = {}, globe = null, map, mode = '3d', generation = 0, panelGeneration = 0;
let geographyMode = '3d', touchTarget = null, ledgerDate = null, fallbackMessage = '';
function status(message = '') { $('status').textContent = message; $('status').hidden = !message; }
function report(error) {
  console.error(error);
  status(error.missing ? `This part of the data has not been built yet: ${error.message}. The rest of the viewer still works.` : `Could not load this view: ${error.message}`);
}
function openPanel(open = true) { $('panel').classList.toggle('open', open); $('btn-panel').setAttribute('aria-expanded', String(open)); }
function showMode(next) {
  mode = next === '3d' && globe ? '3d' : '2d';
  $('globe').hidden = mode !== '3d'; $('map').hidden = mode !== '2d';
  $('view-3d').setAttribute('aria-pressed', String(mode === '3d'));
  $('view-2d').setAttribute('aria-pressed', String(mode === '2d'));
  $('guides').disabled = mode !== '3d';
  document.body.dataset.mode = mode;
  $('gesture-help').textContent = `${mode === '3d' ? 'Drag to rotate' : 'Drag to pan'} · Scroll or pinch to zoom · Click a chapter or light`;
  requestAnimationFrame(() => mode === '3d' ? globe.resize() : map.resize());
}
function hover(value, event, touch = false) {
  if (touchTarget && !touch) return;
  const tooltip = $('tooltip');
  tooltip.hidden = !value; state.hover = value;
  if (!value || !event) return;
  tooltip.classList.toggle('touch', touch);
  tooltipContent(tooltip, value, world, wording, state.entity);
  if (touch && value.other_slug) tooltip.append(link('Open', mapURL(value.other_slug, mode)));
  const box = $('stage').getBoundingClientRect();
  tooltip.style.left = `${Math.max(8, Math.min(box.width - tooltip.offsetWidth - 8, event.clientX - box.left + 14))}px`;
  tooltip.style.top = `${Math.max(8, Math.min(box.height - tooltip.offsetHeight - 8, event.clientY - box.top + 14))}px`;
}
async function showDistrict(id, asRoute = false) {
  const territory = world.byId.get(id); if (!territory) return;
  const token = ++panelGeneration, routeToken = generation;
  districtCard($('info'), territory, world, null, wording, mode, asRoute ? null : state.entity);
  document.body.dataset.selected = id;
  if (asRoute) { globe?.focus(territory); globe?.mark(territory); }
  if (territory.level !== 'district') return;
  try {
    const detail = await data.district(id);
    if (token === panelGeneration && routeToken === generation) districtCard($('info'), territory, world, detail, wording, mode, asRoute ? null : state.entity);
  } catch (error) { if (token === panelGeneration && routeToken === generation) report(error); }
}
function select(value, event) {
  if (value.other_slug) {
    if (event.pointerType === 'touch' && touchTarget !== value) { touchTarget = value; hover(value, event, true); return; }
    touchTarget = null; location.hash = mapURL(value.other_slug, mode); return;
  }
  touchTarget = null; hover(null);
  const id = value.district_id || value.territory_id;
  if (state.entity) { showDistrict(id); openPanel(); }
  else { location.hash = districtURL(id); openPanel(); }
}
function highlight(slug) { map.highlight(slug); globe?.highlight(slug); }
async function route() {
  const token = ++generation; panelGeneration++;
  const parsed = parseRoute(location.hash);
  if (parsed.route === 'globe' && location.hash !== '#/globe') history.replaceState(null, '', '#/globe');
  if (parsed.route === 'district' && !world.byId.has(parsed.territoryId)) { history.replaceState(null, '', '#/globe'); parsed.route = 'globe'; }
  if (parsed.route === 'map3d' && !globe) {
    history.replaceState(null, '', mapURL(parsed.slug)); parsed.route = 'map';
  }
  Object.assign(state, { route: parsed.route, slug: parsed.slug || null, territoryId: parsed.territoryId || null, entity: null, hover: null });
  document.body.dataset.route = state.route; delete document.body.dataset.selected;
  touchTarget = null; hover(null); status(fallbackMessage);
  globe?.showGlobe(); map.render(null);
  $('btn-back').hidden = !state.slug; $('dense-note').hidden = true;
  if (!state.slug) {
    showMode(state.route === 'district' ? '3d' : geographyMode);
    if (state.route === 'district') await showDistrict(state.territoryId, true);
    else intro($('info'), world, rows, wording, ledgerDate);
    return;
  }
  showMode(state.route === 'map3d' ? '3d' : '2d');
  $('info').replaceChildren(text('p', `Loading ${state.slug}…`)); status(`Loading ${state.slug}.json…`);
  try {
    const entity = await data.entity(state.slug); if (token !== generation) return;
    const spots = spotsFor(entity, world); state.entity = entity;
    map.render(entity, spots);
    status(fallbackMessage);
    if (mode === '3d') {
      try { globe.showShell(entity, spots); }
      catch (error) { showMode('2d'); history.replaceState(null, '', mapURL(state.slug)); state.route = 'map'; report(error); }
    }
    entityCard($('info'), entity, spots, mode, wording, highlight);
    $('dense-note').hidden = spots.length <= 4000;
  } catch (error) {
    if (token !== generation) return;
    $('info').replaceChildren(text('h2', 'Entity data unavailable'), text('p', 'This entity export has not been built yet. You can still explore the textbook geography.'));
    report(error);
  }
}
function elevator() {
  const query = normalize(state.query.trim());
  const matches = rows.filter(row => row.group === state.group && (!query || [row.canonical_name, ...(row.aliases || [])].some(name => normalize(name).includes(query))))
    .sort((a, b) => (a.rank ?? Infinity) - (b.rank ?? Infinity) || (a.altitude ?? Infinity) - (b.altitude ?? Infinity) || a.canonical_name.localeCompare(b.canonical_name));
  $('results').replaceChildren();
  $('result-count').textContent = `${matches.length} results${matches.length > 300 ? ' · type to narrow (showing 300)' : ''}`;
  const max = matches.reduce((n, r) => Math.max(n, Math.log1p(r.edge_count)), 1);
  for (const row of matches.slice(0, 300)) {
    const item = text('li'), target = link(row.canonical_name, mapURL(row.slug, mode));
    const bar = text('span', '', 'edge-bar'); bar.style.width = `${60 * Math.log1p(row.edge_count) / max}px`;
    target.append(text('small', `Altitude ${Number.isFinite(row.altitude) ? row.altitude.toFixed(3) : 'not assigned'} · ${row.edge_count} connections${row.has_text ? '' : ' · no text yet'}`), bar);
    item.append(target); $('results').append(item);
  }
  $('places').replaceChildren();
  if (query) {
    const places = world.territories.filter(t => normalize(t.name).includes(query)).slice(0, 10);
    if (places.length) $('places').append(text('h3', 'Places'));
    for (const t of places) { const p = text('p'); p.append(link(`${t.name} · ${t.book_id}`, districtURL(t.territory_id))); $('places').append(p); }
  }
}
function bookList() {
  const query = normalize($('book-search').value.trim()); $('book-list').replaceChildren();
  for (const book of world.territories.filter(t => t.level === 'continent' && normalize(`${t.name} ${t.book_id}`).includes(query)).sort((a, b) => a.seat_order - b.seat_order)) {
    const item = text('li'), target = link('', districtURL(book.territory_id)), swatch = text('span', '', 'swatch');
    swatch.style.backgroundColor = book.colour_hex; target.append(swatch, document.createTextNode(book.name)); item.append(target); $('book-list').append(item);
  }
}
function switchMode(next) {
  if (state.slug) location.hash = mapURL(state.slug, next);
  else { geographyMode = next; showMode(next); }
}
async function start() {
  world = await data.geography();
  $('counts').textContent = `${world.territories.filter(t => t.level === 'continent').length} books · ${world.territories.filter(t => t.level === 'district').length.toLocaleString()} chapter districts`;
  map = await createMap($('map'), world, select, hover);
  try { wording = await data.wording(); } catch (error) { report(error); }
  try { rows = await data.search(); $('registry-state').textContent = `${rows.length.toLocaleString()} entities exported`; }
  catch (error) { $('registry-state').textContent = 'Medical registry not exported yet'; console.error(error); }
  // The ledger is optional until Part 9; its absence does not block geography.
  try {
    const response = await fetch('../data/ledger.json');
    if (response.ok) { const ledger = await response.json(); ledgerDate = ledger.updated_at || ledger.ledger_date || ledger.export_date || ledger.date; }
    else if (response.status !== 404) console.error(`../data/ledger.json (HTTP ${response.status})`);
  } catch (error) { console.error(error); }
  legend($('legend'), wording);
  try {
    const { createGlobe } = await import('./globe3d.js');
    globe = await createGlobe($('globe'), world, select, hover);
    const home = world.territories.find(t => t.level === 'continent' && t.book_id === 'HARRISON-22');
    if (!home || !globe.alignment(home)) throw new Error('Globe/raster alignment check failed');
    document.body.dataset.alignment = 'passed';
    globe.focus(home, true, 4.6);
  } catch (error) {
    console.error(error); globe = null; geographyMode = '2d'; $('view-3d').disabled = true;
    fallbackMessage = '3-D view is not available in this browser; showing the 2-D map.';
  }
  $('book-search').addEventListener('input', bookList);
  let timer;
  $('search').addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(() => { state.query = $('search').value; elevator(); }, 120); });
  $('search').addEventListener('keydown', e => { if (e.key === 'Enter') { clearTimeout(timer); state.query = $('search').value; elevator(); $('results').querySelector('a')?.click(); } });
  for (const tab of document.querySelectorAll('[data-group]')) tab.addEventListener('click', () => {
    state.group = tab.dataset.group;
    for (const button of document.querySelectorAll('[data-group]')) button.setAttribute('aria-pressed', String(button === tab));
    elevator();
  });
  $('view-3d').addEventListener('click', () => switchMode('3d'));
  $('view-2d').addEventListener('click', () => switchMode('2d'));
  $('zoom-in').addEventListener('click', () => mode === '3d' ? globe.zoom(0.8) : map.zoom(1.5));
  $('zoom-out').addEventListener('click', () => mode === '3d' ? globe.zoom(1.25) : map.zoom(1 / 1.5));
  $('btn-fit').addEventListener('click', () => mode === '3d' ? globe.fit() : map.fit());
  $('guides').addEventListener('change', () => globe?.guides($('guides').checked));
  $('btn-panel').addEventListener('click', () => openPanel(!$('panel').classList.contains('open')));
  for (const id of ['home', 'btn-back']) $(id).addEventListener('click', () => {
    geographyMode = globe ? '3d' : '2d';
    if (location.hash === '#/globe') route(); else location.hash = '/globe';
    const home = world.territories.find(t => t.level === 'continent' && t.book_id === 'HARRISON-22');
    if (home) globe?.home(home);
    map.fit();
  });
  $('panel').addEventListener('click', event => {
    const target = event.target.closest('a[href^="#/"]');
    if (target) { if (target.hash === location.hash) route(); openPanel(false); }
  });
  addEventListener('hashchange', () => { route(); elevator(); });
  bookList(); elevator(); await route(); document.body.dataset.state = 'ready';
}
start().catch(error => { document.body.dataset.state = 'error'; status(`Could not load the viewer: ${error.message}`); console.error(error); });
