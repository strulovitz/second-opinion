import { COLOUR, RELATION_COLOUR } from './geo.js';

export const groups = ['symptoms-and-signs', 'diseases-and-conditions', 'treatments-and-drugs'];
export function text(tag, value = '', className) {
  const node = document.createElement(tag); node.textContent = value;
  if (className) node.className = className;
  return node;
}
export function link(label, href, className) {
  const node = text('a', label, className); node.href = href; return node;
}
export const mapURL = (slug, mode = '2d') => `#/map/${encodeURIComponent(slug)}${mode === '3d' ? '/3d' : ''}`;
export const districtURL = id => `#/district/${encodeURIComponent(id)}`;
export function sectionKey(edge) {
  return [edge.relation, edge.relation === 'MISTAKEN_FOR' ? 'both' : edge.direction, edge.subtype].filter(Boolean).join(':');
}
export function sectionTitle(edge, wording) { return wording.sections?.[sectionKey(edge)] || [edge.relation, edge.direction, edge.subtype].filter(Boolean).join(' / '); }
export const fLabel = (f, wording) => wording.f_labels?.[f] || `F${f}`;
export function ranges(pages = []) {
  const values = [...new Set(pages)].sort((a, b) => a - b), out = [];
  for (let i = 0; i < values.length; i++) {
    const first = values[i]; let last = first;
    while (i + 1 < values.length && values[i + 1] === last + 1) last = values[++i];
    out.push(first === last ? `${first}` : `${first}–${last}`);
  }
  return out.join(', ');
}
export function intro(panel, world, rows, wording, date) {
  panel.replaceChildren(text('h2', 'The globe'), text('p', wording.globe_intro || 'Every continent is one textbook. Every chapter is a district. Click a place to explore.'));
  const bands = text('ul', '', 'bands');
  for (const value of ['0.30–1.00 · Diseases and conditions (deep = multisystem)', '1.00–1.50 · Symptoms and signs (low = nonspecific)', '1.50–3.00 · Treatments (lifestyle through surgery)']) bands.append(text('li', value));
  panel.append(bands);
  for (const group of groups) panel.append(text('p', `${wording.group_labels?.[group] || group}: ${rows.filter(r => r.group === group).length.toLocaleString()}`));
  if (!rows.length) panel.append(text('p', 'The textbook geography is available. The medical registry and relationship data have not been exported yet.', 'notice'));
  if (date) panel.append(text('p', `Ledger: ${date}`, 'muted'));
}
export function entityCard(panel, entity, spots, mode, wording, highlight) {
  const aliases = (entity.aliases || []).filter(a => a !== entity.canonical_name);
  panel.replaceChildren(text('p', wording.group_labels?.[entity.group] || entity.group, 'group-label'), text('h2', entity.canonical_name));
  if (aliases.length) panel.append(text('p', `Also called: ${aliases.slice(0, 6).join('; ')}${aliases.length > 6 ? `; and ${aliases.length - 6} more` : ''}`, 'muted'));
  const values = { r: Number.isFinite(entity.altitude) ? entity.altitude.toFixed(3) : 'not assigned', n: entity.ordering_value ?? 'not counted', N: entity.books_total ?? 'not counted',
    heaviness_group_label: wording.heaviness_labels?.[entity.heaviness_group] || entity.heaviness_group || 'not assigned', class_canonical: entity.class_canonical || 'not assigned' };
  panel.append(text('p', (wording.altitude_templates?.[entity.group] || 'Altitude {r}.').replace(/\{(\w+)\}/g, (_, k) => values[k] ?? k)));
  const colours = Object.fromEntries(['blue', 'yellow', 'grey'].map(c => [c, spots.filter(s => s.colour === c).length]));
  const books = new Set([...(entity.lit_spots || []).map(s => s.book_id), ...(entity.edges || []).flatMap(e => (e.statements || []).map(s => s.book_id))]);
  panel.append(text('p', `Showing ${spots.length} lights in ${new Set(spots.map(s => s.district_id)).size} districts from ${books.size} books; ${colours.blue} blue, ${colours.yellow} yellow, ${colours.grey} grey.`));
  const links = text('p', '', 'card-links');
  links.append(link('Read the page', `../pages/${encodeURIComponent(entity.slug)}.html`), link(mode === '3d' ? 'Open in 2-D' : 'Open in 3-D', mapURL(entity.slug, mode === '3d' ? '2d' : '3d')), link('Back to globe', '#/globe'));
  panel.append(links);
  if (!(entity.edges || []).length) panel.append(text('p', `No relation from the books has been read for this entity yet; it appears in the index of ${new Set((entity.lit_spots || []).map(s => s.district_id)).size} chapters (white dots).`, 'notice'));
  const sections = new Map();
  for (const edge of entity.edges || []) {
    const key = sectionKey(edge);
    if (!sections.has(key)) {
      const section = text('section', '', `relations ${RELATION_COLOUR[edge.relation] || 'grey'}`), list = text('ul');
      section.append(text('h3', sectionTitle(edge, wording)), list); panel.append(section); sections.set(key, list);
    }
    const item = text('li'), target = link(edge.other_name, mapURL(edge.other_slug, mode));
    target.addEventListener('pointerenter', () => highlight(edge.other_slug));
    target.addEventListener('pointerleave', () => highlight(null));
    target.addEventListener('focus', () => highlight(edge.other_slug)); target.addEventListener('blur', () => highlight(null));
    item.append(target, text('span', fLabel(edge.f_scale, wording), `fbadge f${edge.f_scale}`));
    if (edge.severity) item.append(text('span', wording.severity || 'serious', 'severe'));
    item.append(text('small', `${edge.statements?.length || 0} sentences`)); sections.get(key).append(item);
  }
}
export function districtCard(panel, territory, world, detail, wording, mode, entity) {
  const chain = [];
  for (let t = territory; t; t = world.byId.get(t.parent)) chain.unshift(t.name);
  panel.replaceChildren(text('p', chain.join(' › '), 'breadcrumb'), text('h2', territory.name), text('p', territory.territory_id, 'territory-id'), text('p', `Book: ${territory.book_id}`));
  if (territory.toc_number != null) panel.append(text('p', `Chapter number: ${territory.toc_number}`));
  if (territory.tile_sides) panel.append(text('p', `Chapter tile: ${territory.tile_sides === 6 ? 'hexagon' : 'pentagon'}`));
  if (territory.page_start != null) panel.append(text('p', `Stored page range: ${territory.page_start}–${territory.page_end}`));
  if (entity) {
    const mention = entity.lit_spots?.find(s => s.district_id === territory.territory_id);
    if (mention) panel.append(text('p', `${entity.canonical_name}: printed pages ${ranges(mention.pages)}`));
    panel.append(link('Back to entity card', mapURL(entity.slug, mode)));
  }
  if (detail) {
    panel.append(text('p', `${detail.entities.length} entities discussed here`));
    for (const group of groups) {
      const rows = detail.entities.filter(e => e.group === group); if (!rows.length) continue;
      panel.append(text('h3', wording.group_labels?.[group] || group));
      const list = text('ul');
      for (const row of rows.slice(0, 60)) {
        const item = text('li'); item.append(link(row.canonical_name, mapURL(row.slug, mode)), text('small', `${row.edges_here} connections, ${row.mentions} mentions`)); list.append(item);
      }
      panel.append(list);
      if (rows.length > 60) panel.append(link(`and ${rows.length - 60} more in the data file`, `../data/districts/${encodeURIComponent(territory.territory_id)}.json`));
    }
  } else if (territory.level === 'district') panel.append(text('p', 'The medical data for this district have not been exported yet.', 'muted'));
  else panel.append(text('p', 'Choose a chapter district to see its medical data.', 'muted'));
  panel.append(link('Show on globe', districtURL(territory.territory_id)));
}
export function tooltipContent(node, value, world, wording, entity) {
  node.replaceChildren();
  if (value.other_slug) {
    node.append(text('strong', value.other_name), text('small', wording.group_labels?.[value.other_group] || value.other_group), text('div', sectionTitle(value, wording)), text('div', fLabel(value.f, wording)));
    const s = value.statement;
    if (s.numeric_pct != null) node.append(text('span', `${s.numeric_pct}%`));
    if (value.severity) node.append(text('span', wording.severity || 'serious', 'severe'));
    if (s.frequency_phrase) node.append(text('div', `“${s.frequency_phrase}”`));
    node.append(text('div', `${s.book_id}, ${s.district_name || world.byId.get(value.district_id)?.name}, p.${s.page_number}`));
    if (value.count > 1) node.append(text('div', `and ${value.count - 1} more sentences`));
  } else if (value.lit) node.append(text('strong', entity?.canonical_name || ''), text('div', `Discussed in ${world.byId.get(value.district_id)?.name} (${value.book_id}), pages ${ranges(value.pages)}`));
  else node.append(text('strong', value.name), text('div', `${value.book_id} · Stored page range: ${value.page_start}–${value.page_end}`));
}
export function legend(node, wording) {
  node.replaceChildren();
  const summary = text('summary', 'Legend'); node.append(summary);
  const content = text('div', '', 'legend-content'); node.append(content);
  for (const colour of ['blue', 'yellow', 'grey', 'lit']) {
    const item = text('span', '', 'legend-item'), dot = text('i', '', colour === 'lit' ? 'dot hollow' : 'dot');
    dot.style.setProperty('--spot', COLOUR[colour]); item.append(dot, document.createTextNode(wording.legend?.[colour] || colour)); content.append(item);
  }
  for (let f = 1; f <= 5; f++) {
    const item = text('span', '', 'legend-item'), dot = text('i', '', 'dot');
    dot.style.width = dot.style.height = `${6 + f * 2}px`; item.append(dot, document.createTextNode(`F${f} ${fLabel(f, wording)}`)); content.append(item);
  }
  for (const [kind, label] of [['dashed', fLabel(0, wording)], ['serious', wording.severity || 'serious']]) {
    const item = text('span', '', 'legend-item'); item.append(text('i', '', `dot ${kind}`), document.createTextNode(label)); content.append(item);
  }
}
