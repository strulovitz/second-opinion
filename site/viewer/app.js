import { geography } from './data.js';
import { createMap } from './map2d.js';

const $ = id => document.getElementById(id);
const status = $('status');
function text(tag, value, className) {
  const element = document.createElement(tag);
  element.textContent = value;
  if (className) element.className = className;
  return element;
}

async function start() {
  const world = await geography();
  const continents = world.territories.filter(t => t.level === 'continent').sort((a, b) => a.seat_order - b.seat_order);
  const home = continents.find(t => t.book_id === 'HARRISON-22') || continents[0];
  const districts = world.territories.filter(t => t.level === 'district');
  $('counts').textContent = `${continents.length} books · ${districts.length.toLocaleString()} chapter districts`;
  let globe = null, mode = '3d';
  function choose(territory) { location.hash = `/district/${encodeURIComponent(territory.territory_id)}`; }
  function hover(territory, event) {
    const tooltip = $('tooltip');
    tooltip.hidden = !territory;
    if (!territory || !event) return;
    const continent = continents.find(c => c.book_id === territory.book_id);
    tooltip.textContent = `${continent?.name || territory.book_id} · ${territory.name}`;
    const box = $('stage').getBoundingClientRect();
    tooltip.style.left = `${Math.max(4, Math.min(box.width - 305, event.clientX - box.left + 14))}px`;
    tooltip.style.top = `${Math.max(4, Math.min(box.height - 65, event.clientY - box.top + 14))}px`;
  }
  const map = await createMap($('map'), world, choose, hover);
  function showMode(next) {
    mode = next === '3d' && globe ? '3d' : '2d';
    $('globe').hidden = mode !== '3d'; $('map').hidden = mode !== '2d';
    $('view-3d').setAttribute('aria-pressed', String(mode === '3d'));
    $('view-2d').setAttribute('aria-pressed', String(mode === '2d'));
    $('zoom-in').disabled = $('zoom-out').disabled = $('guides').disabled = mode !== '3d';
    document.body.dataset.mode = mode;
    requestAnimationFrame(() => mode === '3d' ? globe.resize() : map.resize());
  }
  function panel(territory) {
    $('info').replaceChildren();
    if (!territory) {
      $('info').append(text('h2', 'Explore the globe'), text('p', 'Every continent is one textbook. The smaller regions are its Parts, Sections and chapters. Click a region, or choose a specialty below.'));
      return;
    }
    const chain = [];
    for (let t = territory; t; t = world.byId.get(t.parent)) chain.unshift(t.name);
    $('info').append(text('p', chain.join(' › '), 'breadcrumb'), text('h2', territory.name),
      text('p', territory.territory_id, 'territory-id'), text('p', `Book: ${territory.book_id}`));
    if (territory.toc_number != null) $('info').append(text('p', `Chapter number: ${territory.toc_number}`));
    if (territory.page_start != null) $('info').append(text('p', `Stored page range: ${territory.page_start}–${territory.page_end}`));
    document.body.dataset.selected = territory.territory_id;
  }
  function route() {
    const match = location.hash.match(/^#\/district\/([^/]+)$/);
    const territory = match ? world.byId.get(decodeURIComponent(match[1])) : null;
    if (!territory && location.hash !== '#/globe') history.replaceState(null, '', '#/globe');
    panel(territory);
    if (territory && globe) { globe.focus(territory); globe.mark(territory); }
  }
  function bookList() {
    const query = $('book-search').value.trim().toLocaleLowerCase();
    $('book-list').replaceChildren();
    for (const book of continents.filter(t => `${t.name} ${t.book_id}`.toLocaleLowerCase().includes(query))) {
      const item = document.createElement('li'), link = document.createElement('a'), swatch = document.createElement('span');
      swatch.className = 'swatch'; swatch.style.backgroundColor = book.colour_hex;
      link.href = `#/district/${encodeURIComponent(book.territory_id)}`;
      link.append(swatch, document.createTextNode(book.name)); item.append(link); $('book-list').append(item);
    }
  }
  $('book-search').addEventListener('input', bookList);
  $('view-3d').addEventListener('click', () => showMode('3d'));
  $('view-2d').addEventListener('click', () => showMode('2d'));
  $('zoom-in').addEventListener('click', () => globe?.zoom(0.8));
  $('zoom-out').addEventListener('click', () => globe?.zoom(1.25));
  $('guides').addEventListener('change', () => globe?.guides($('guides').checked));
  $('home').addEventListener('click', () => { location.hash = '/globe'; panel(null); globe?.focus(home); });
  bookList();
  try {
    const { createGlobe } = await import('./globe3d.js');
    globe = await createGlobe($('globe'), world, choose, hover);
    if (!globe.alignment(home)) throw new Error('Globe/raster alignment check failed');
    document.body.dataset.alignment = 'passed';
    globe.focus(home, true);
    status.hidden = true;
  } catch (error) {
    console.error(error);
    $('view-3d').disabled = true;
    status.textContent = `3D could not start: ${error.message}. The 2D map is available.`;
  }
  showMode(globe ? '3d' : '2d');
  route();
  addEventListener('hashchange', route);
  document.body.dataset.state = 'ready';
}

start().catch(error => {
  document.body.dataset.state = 'error';
  status.textContent = `Could not load the geography: ${error.message}`;
  console.error(error);
});
