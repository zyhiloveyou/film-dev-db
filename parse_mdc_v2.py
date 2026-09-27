#!/usr/bin/env python3
"""MDC 解析器 v2：保留非纯数字时间格式（3+3 两浴、8-10 范围、34* 标记等）。
新增 raw 列（原始显示值）+ 数值列（用于换算：范围取中值、两浴取总和）。
"""
import csv, glob, json, os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, 'sources', 'mdc_raw_v2')
OUT_CSV = os.path.join(BASE, 'data', 'mdc_all_v2.csv')
OUT_JSON = os.path.join(BASE, 'data', 'mdc_all_v2.json')

def parse_rows(text):
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) < 8:
            continue
        if cells[0] in ('Film', '---') or not cells[0]:
            continue
        rows.append(cells[:9] if len(cells) >= 9 else cells + [''] * (9 - len(cells)))
    return rows

def to_value(raw):
    """把 MDC 时间原文转成数值（供换算）：3+3→6，8-10→9，34*→34"""
    if not raw:
        return None
    s = raw.strip().replace('*', '').replace('+', ' ').replace('–', '-')
    # 两浴：3+3 → 求和
    parts = [p for p in re.split(r'[\s]+', s) if p]
    total = 0.0
    found = False
    for p in parts:
        m = re.match(r'^(\d+(?:\.\d+)?)(?:\s*-\s*(\d+(?:\.\d+)?))?$', p)
        if m:
            lo = float(m.group(1))
            hi = float(m.group(2)) if m.group(2) else lo
            total += (lo + hi) / 2
            found = True
    return round(total, 2) if found else None

def main():
    seen = set()
    out = []
    for fp in sorted(glob.glob(os.path.join(RAW, '*.md'))):
        text = open(fp, encoding='utf-8', errors='replace').read()
        for r in parse_rows(text):
            film, dev, dil, iso, t35, t120, sheet, temp, notes = r
            row = notes.split('devrow=')[-1].rstrip(')') if 'devrow=' in notes else ''
            key = (film, dev, dil, iso, t35, t120, sheet, temp, row)
            if key in seen:
                continue
            seen.add(key)
            out.append({
                'film': film,
                'developer': dev,
                'dilution': dil or None,
                'iso': iso or None,
                't35mm_raw': t35 or None,
                't120mm_raw': t120 or None,
                't_sheet_raw': sheet or None,
                't35mm_min': to_value(t35),
                't120_min': to_value(t120),
                't_sheet_min': to_value(sheet),
                'temp_c': to_value(temp.rstrip('C')) if temp.endswith('C') else None,
                'mdc_row': row or None,
                'source': 'MassiveDevChart',
            })
    out.sort(key=lambda r: (r['film'].lower(), r['developer'].lower(), str(r['dilution']), str(r['iso'])))
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    if out:
        with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
            w.writeheader()
            w.writerows(out)
        json.dump(out, open(OUT_JSON, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'行数: {len(out)}')
    films = {r['film'] for r in out}
    devs = {r['developer'] for r in out}
    print(f'胶片: {len(films)}  显影液: {len(devs)}')
    # 统计保留的原始格式
    special = [r for r in out if r['t35mm_raw'] and not re.match(r'^\d+(\.\d+)?$', r['t35mm_raw'])]
    print(f'35mm 非纯数字格式行: {len(special)}（例：{sorted({r["t35mm_raw"] for r in special})[:12]}）')
    empty = [r for r in out if not r['t35mm_raw'] and not r['t120mm_raw'] and not r['t_sheet_raw']]
    print(f'时间全空行: {len(empty)}')

if __name__ == '__main__':
    main()
