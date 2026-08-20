#!/usr/bin/env python3
"""Parse MDC markdown dumps (from r.jina.ai) into a unified CSV + JSON."""
import csv, glob, json, os, re, sys

RAW = os.path.join(os.path.dirname(__file__), 'sources', 'mdc_raw')
OUT_CSV = os.path.join(os.path.dirname(__file__), 'data', 'mdc_all.csv')
OUT_JSON = os.path.join(os.path.dirname(__file__), 'data', 'mdc_all.json')

def parse_rows(text):
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) < 8:
            continue
        if cells[0] in ('Film', '---'):
            continue
        # normalize header-ish artifacts
        if not cells[0]:
            continue
        rows.append(cells[:9] if len(cells) >= 9 else cells + [''] * (9 - len(cells)))
    return rows

def clean_num(s):
    s = s.strip().rstrip('+')
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None

def main():
    seen = set()
    out = []
    files = sorted(glob.glob(os.path.join(RAW, '*.md')))
    for fp in files:
        text = open(fp, encoding='utf-8', errors='replace').read()
        for r in parse_rows(text):
            film, dev, dil, iso, t35, t120, sheet, temp, notes = r
            key = (film, dev, dil, iso, t35, t120, sheet, temp,
                   notes.split('devrow=')[-1].rstrip(')') if 'devrow=' in notes else '')
            if key in seen:
                continue
            seen.add(key)
            rec = {
                'film': film,
                'developer': dev,
                'dilution': dil or None,
                'iso': iso or None,
                't35mm_min': clean_num(t35),
                't120_min': clean_num(t120),
                't_sheet_min': clean_num(sheet),
                'temp_c': clean_num(temp.rstrip('C')) if temp.endswith('C') else None,
                'mdc_row': notes.split('devrow=')[-1].rstrip(')') if 'devrow=' in notes else None,
                'source': 'MassiveDevChart',
            }
            out.append(rec)
    out.sort(key=lambda r: (r['film'].lower(), r['developer'].lower(), str(r['dilution']), str(r['iso'])))
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    films = sorted({r['film'] for r in out})
    devs = sorted({r['developer'] for r in out})
    print(f"rows: {len(out)}  files: {len(files)}")
    print(f"films: {len(films)}  developers: {len(devs)}")
    print(f"temps: {sorted({r['temp_c'] for r in out if r['temp_c']})}")

if __name__ == '__main__':
    main()
