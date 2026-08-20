#!/usr/bin/env python3
"""Build compressed web data (data_web.js) from the film-dev-db CSVs."""
import csv, json, os

BASE = os.path.dirname(__file__)
DATA = os.path.join(BASE, 'data')

def read_csv(name):
    return list(csv.DictReader(open(os.path.join(DATA, name), encoding='utf-8')))

mdc = read_csv('mdc_all.csv')

# ---- dictionaries ----
films = sorted({r['film'] for r in mdc})
devs = sorted({r['developer'] for r in mdc})
dils = sorted({r['dilution'] for r in mdc if r['dilution']})
isos = sorted({r['iso'] for r in mdc if r['iso']}, key=lambda s: (len(s), s))
f_idx = {f: i for i, f in enumerate(films)}
d_idx = {d: i for i, d in enumerate(devs)}
di_idx = {d: i for i, d in enumerate(dils)}
i_idx = {s: i for i, s in enumerate(isos)}

# ---- entries: [filmIdx, devIdx, dilIdx, isoIdx, t35, t120, sheet, temp, row] ----
def num(v):
    try:
        return float(v) if v not in (None, '') else None
    except ValueError:
        return None

entries = []
for r in mdc:
    entries.append([
        f_idx[r['film']],
        d_idx[r['developer']],
        di_idx[r['dilution']] if r['dilution'] else -1,
        i_idx[r['iso']] if r['iso'] else -1,
        num(r['t35mm_min']),
        num(r['t120_min']),
        num(r['t_sheet_min']),
        num(r['temp_c']) or 20.0,
        int(r['mdc_row']) if r['mdc_row'] else 0,
    ])

# ---- official tables ----
def norm_official(rows, dev_field='developer', dil_field='dilution', film_field='film',
                  time_field='time_min', temp_field='temp_c', iso_field='iso', extra=None,
                  default_dev=None):
    out = []
    for r in rows:
        row = {
            'f': r[film_field],
            'd': r.get(dev_field) if dev_field else default_dev,
            'i': r.get(iso_field, ''),
            't': float(r[time_field]),
            'T': float(r[temp_field]) if r.get(temp_field) else 20,
        }
        if r.get(dil_field):
            row['dl'] = r[dil_field]
        if extra:
            for k, v in extra(r).items():
                if v:
                    row[k] = v
        out.append(row)
    return out

official = {
    'ilfotec_hc': norm_official(read_csv('official_ilfotec_hc.csv'), dev_field=None, default_dev='Ilfotec HC', extra=lambda r: {'n': r['notes']}),
    'foma': norm_official(read_csv('official_foma.csv'), time_field='t_min_minutes',
                          extra=lambda r: {'mx': float(r['t_max_minutes']), 'n': r['notes']}),
    'kodak_trix': norm_official(read_csv('official_kodak_trix.csv'), extra=lambda r: {'a': r['agitation']}),
    'rollei': norm_official(read_csv('official_rollei.csv')),
}

web = {
    'meta': {
        'mdc_updated': '2026-07-14',
        'mdc_rows': len(entries),
        'films': len(films),
        'devs': len(devs),
    },
    'films': films,
    'devs': devs,
    'dils': dils,
    'isos': isos,
    'entries': entries,
    'official': official,
}

out_path = os.path.join(BASE, 'web', 'data_web.js')
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w', encoding='utf-8') as f:
    f.write('window.DEVDB = ')
    json.dump(web, f, ensure_ascii=False, separators=(',', ':'))
    f.write(';\n')
print(f"web data: {os.path.getsize(out_path)/1024:.0f} KB, entries={len(entries)}")
