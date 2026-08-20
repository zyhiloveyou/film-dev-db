#!/usr/bin/env python3
"""Build derived guides (rotary / temperature) and a merged index from all sources."""
import csv, json, os

BASE = os.path.dirname(__file__)
DATA = os.path.join(BASE, 'data')

def read_csv(name):
    return list(csv.DictReader(open(os.path.join(DATA, name), encoding='utf-8')))

# ---------- 1. Rotary (continuous agitation) guide from MDC 20C rows ----------
mdc = read_csv('mdc_all.csv')
rotary = []
for r in mdc:
    if r['temp_c'] != '20.0':
        continue
    t = r['t35mm_min'] or r['t120_min'] or r['t_sheet_min']
    if not t:
        continue
    t = float(t)
    # Ilford official rule: continuous agitation = 0.85 x intermittent
    # Rollei official rule: rotary = 10-15% shorter (0.85-0.90)
    rotary.append({
        'film': r['film'], 'developer': r['developer'], 'dilution': r['dilution'],
        'iso': r['iso'],
        'inversion_20c_min': t,
        'rotary_20c_min_0.85': round(t * 0.85, 2),
        'rotary_20c_min_0.90': round(t * 0.90, 2),
    })
seen = set()
rotary_u = []
for r in rotary:
    k = (r['film'], r['developer'], r['dilution'], r['iso'], r['inversion_20c_min'])
    if k in seen:
        continue
    seen.add(k)
    rotary_u.append(r)
with open(os.path.join(DATA, 'rotary_guide.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rotary_u[0].keys()))
    w.writeheader()
    w.writerows(rotary_u)

# ---------- 2. Temperature conversion table ----------
# Ilford/Kodak standard: +/-10% per 1C from 20C. Foma official factors:
foma_factors = {16: 1.45, 18: 1.2, 19: 1.1, 20: 1.0, 21: 0.9, 22: 0.85, 23: 0.8, 24: 0.75, 26: 0.6}
# Ilford/Kodak rule factor = 1.1^(20-T)
rows = []
for t in range(15, 31):
    if t in foma_factors:
        rows.append({'temp_c': t, 'factor_ilford_kodak': round(1.1 ** (20 - t), 3),
                     'factor_foma': foma_factors[t]})
    else:
        rows.append({'temp_c': t, 'factor_ilford_kodak': round(1.1 ** (20 - t), 3), 'factor_foma': ''})
with open(os.path.join(DATA, 'temp_conversion.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['temp_c', 'factor_ilford_kodak', 'factor_foma'])
    w.writeheader()
    w.writerows(rows)

# ---------- 3. Merged index ----------
labo = json.load(open(os.path.join(BASE, 'sources', 'films_labolosalos.json')))
summary = {
    'mdc': {'rows': len(mdc),
            'films': len({r['film'] for r in mdc}),
            'developers': len({r['developer'] for r in mdc}),
            'temps_c': sorted({float(r['temp_c']) for r in mdc if r['temp_c']})},
    'labo_los_alos': {'rows': len(labo['entries']), 'films': labo['meta']['films'],
                      'developers': labo['meta']['developers']},
    'official_ilfotec_hc': len(read_csv('official_ilfotec_hc.csv')),
    'official_foma': len(read_csv('official_foma.csv')),
    'official_kodak_trix': len(read_csv('official_kodak_trix.csv')),
    'official_rollei': len(read_csv('official_rollei.csv')),
    'rotary_guide': len(rotary_u),
}
json.dump(summary, open(os.path.join(DATA, 'summary.json'), 'w'), ensure_ascii=False, indent=2)
print(json.dumps(summary, ensure_ascii=False, indent=2))
