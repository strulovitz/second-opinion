#!/usr/bin/env python3
"""Write the DEMO placeholder data (Opus 5.5, 24 Oct 2026, at Nir's request).

Purpose: show, before any book has been read, exactly how the future layers
will look: disease shells inside the planet, symptom beads in the atmosphere,
treatment shells on the five orbits, blue/yellow/grey lights, F sizes, the
dashed "not stated" circle, the red severity ring and the cascade.

EVERYTHING HERE IS INVENTED and labelled so: every slug starts with "demo-",
every name starts with "DEMO", every book_id is "DEMO", every quote says it is
not from a book, page numbers are 0. The places (district IDs) are real tiles,
chosen by a fixed rule, only so the lights land on the map.

This script never connects to Neo4j and writes only site/data/demo/demo.json.
The viewer shows these entities only while its "Demo of the future" switch is
on, under a yellow DEMO banner. Never copy this file into data/export/ or any
real export, and never load it into the database (Laws 1, 2 and 11).
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/data/demo/demo.json'

ENTITIES = [
    ('demo-symptom-a', 'DEMO symptom A (a common, nonspecific example)', 'symptoms-and-signs', 1.12, None),
    ('demo-symptom-b', 'DEMO symptom B (a rare, very specific example)', 'symptoms-and-signs', 1.44, None),
    ('demo-disease-c', 'DEMO disease C (a deep, multisystem example)', 'diseases-and-conditions', 0.42, None),
    ('demo-disease-d', 'DEMO disease D (a local example near the crust)', 'diseases-and-conditions', 0.93, None),
    ('demo-treatment-e', 'DEMO treatment E (a lifestyle example, lowest orbit)', 'treatments-and-drugs', 1.65, 'lifestyle'),
    ('demo-treatment-f', 'DEMO treatment F (a prescription example)', 'treatments-and-drugs', 2.25, 'prescription'),
    ('demo-treatment-g', 'DEMO treatment G (a surgery example, outer orbit)', 'treatments-and-drugs', 2.85, 'surgery-transplant'),
]
# (start, relation, end, F, severity, subtype, how many districts, seed)
EDGES = [
    ('demo-disease-c', 'PRESENTS_WITH', 'demo-symptom-a', 5, False, None, 14, 1),
    ('demo-disease-d', 'PRESENTS_WITH', 'demo-symptom-a', 3, False, None, 6, 2),
    ('demo-disease-c', 'PRESENTS_WITH', 'demo-symptom-b', 2, False, None, 4, 3),
    ('demo-disease-c', 'TREATED_BY', 'demo-treatment-f', 4, False, None, 9, 4),
    ('demo-disease-d', 'TREATED_BY', 'demo-treatment-g', 3, False, None, 5, 5),
    ('demo-symptom-a', 'TREATED_BY', 'demo-treatment-e', 4, False, None, 7, 6),
    ('demo-treatment-f', 'HARMS', 'demo-disease-d', 1, True, None, 3, 7),
    ('demo-treatment-f', 'HARMS', 'demo-disease-c', 0, True, 'CONTRAINDICATED_IN', 2, 8),
    ('demo-disease-c', 'LEADS_TO', 'demo-disease-d', 0, False, None, 5, 9),
    ('demo-disease-c', 'MISTAKEN_FOR', 'demo-disease-d', 3, False, None, 4, 10),
]


def places(districts, count, seed):
    """A fixed spread of real district tiles (golden-ratio stride), for placement only."""
    step = int(len(districts) * 0.6180339887) | 1
    return [districts[(seed * 7919 + k * step) % len(districts)] for k in range(count)]


def statement(district, f, severity):
    return {'district_id': district['territory_id'], 'district_name': district['name'], 'book_id': 'DEMO',
            'page_number': 0, 'image_file': 'demo-placeholder', 'f_scale': f, 'severity': severity,
            'frequency_phrase': 'DEMO frequency phrase', 'numeric_pct': None,
            'quote': 'DEMO placeholder sentence. This is not from any book.'}


def main():
    rows = json.loads((ROOT / 'site/data/geography/geography.json').read_text())
    districts = [r for r in rows if r['level'] == 'district']
    meta = {slug: (name, group, altitude, heavy) for slug, name, group, altitude, heavy in ENTITIES}
    entities = {}
    for slug, (name, group, altitude, heavy) in meta.items():
        entities[slug] = {'slug': slug, 'canonical_name': name, 'aliases': [f'{name.split(" (")[0]} alias'], 'group': group,
                          'altitude': altitude, 'altitude_status': 'demo', 'heaviness_group': heavy, 'rank': None,
                          'ordering_value': 'DEMO', 'books_total': 'DEMO', 'class_canonical': 'DEMO class' if heavy else None,
                          'text_status': 'none', 'text_quote_count': 0, 'demo': True, 'lit_spots': [], 'edges': []}
    for start, relation, end, f, severity, subtype, count, seed in EDGES:
        chosen = places(districts, count, seed)
        statements = [statement(d, f if k else f, severity and k == 0) for k, d in enumerate(chosen)]
        for me, other, direction in ((start, end, 'out'), (end, start, 'in')):
            entities[me]['edges'].append({
                'relation': relation, 'direction': 'both' if relation == 'MISTAKEN_FOR' else direction, 'subtype': subtype,
                'other_slug': other, 'other_name': meta[other][0], 'other_group': meta[other][1],
                'f_scale': f, 'severity': severity, 'numeric_pct': None, 'statements': statements})
    for k, (slug, entity) in enumerate(entities.items()):
        used = {s['district_id'] for e in entity['edges'] for s in e['statements']}
        for d in places(districts, 6, 100 + k):
            if d['territory_id'] not in used:
                entity['lit_spots'].append({'district_id': d['territory_id'], 'book_id': 'DEMO', 'pages': [0], 'sources': ['demo'], 'mentions': []})
    search = [{'slug': e['slug'], 'canonical_name': e['canonical_name'], 'aliases': e['aliases'], 'group': e['group'],
               'altitude': e['altitude'], 'rank': None, 'edge_count': len(e['edges']), 'has_text': False, 'demo': True}
              for e in entities.values()]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({'notice': 'DEMO placeholders invented by kitchen/make_demo.py. Not from any book. Never load into Neo4j.',
                               'search': search, 'entities': entities}, indent=1, ensure_ascii=False) + '\n')
    print(f'Wrote {OUT} with {len(entities)} invented DEMO entities')


if __name__ == '__main__':
    main()
