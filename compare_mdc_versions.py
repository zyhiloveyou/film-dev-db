#!/usr/bin/env python3
"""对比两次抓取的数据（v1 旧库 vs v2 新抓），输出更新报告。"""
import csv, json, os, collections, sys

BASE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(BASE, 'data', 'mdc_all.csv')
V2 = os.path.join(BASE, 'data', 'mdc_all_v2.csv')
OUT = os.path.join(BASE, 'data', 'update_report.md')

def load_v1(path):
    d = {}
    for r in csv.DictReader(open(path, encoding='utf-8')):
        if not r['film']:
            continue
        k = (r['film'], r['developer'], r['dilution'] or '', r['iso'] or '', r['temp_c'] or '')
        d[k] = (r['t35mm_min'] or '', r['t120_min'] or '', r['t_sheet_min'] or '', r['mdc_row'] or '')
    return d

def load_v2(path):
    d = {}
    for r in csv.DictReader(open(path, encoding='utf-8')):
        if not r['film']:
            continue
        k = (r['film'], r['developer'], r['dilution'] or '', r['iso'] or '', r['temp_c'] or '')
        d[k] = (r['t35mm_min'] or '', r['t120_min'] or '', r['t_sheet_min'] or '',
                r['t35mm_raw'] or '', r['t120mm_raw'] or '', r['t_sheet_raw'] or '', r['mdc_row'] or '')
    return d

def main():
    v1, v2 = load_v1(V1), load_v2(V2)
    added = {k: v for k, v in v2.items() if k not in v1}
    removed = {k: v for k, v in v1.items() if k not in v2}
    filled = {}   # v1 时间为空、v2 有值（解析修复或源更新）
    changed = {}  # 值不同
    for k, nv in v2.items():
        ov = v1.get(k)
        if not ov:
            continue
        o_min = ov[:3]
        n_min = nv[:3]
        if all(x == '' for x in o_min) and any(x != '' for x in n_min):
            filled[k] = (ov, nv)
        elif o_min != n_min:
            changed[k] = (ov, nv)
    L = ['# 数据库更新检查报告\n\n',
         f'- 旧库（抓取于 2026-07-14 版）: {len(v1)} 行\n',
         f'- 新抓（2026-09-08 版）: {len(v2)} 行\n',
         f'- **新增组合**: {len(added)} 行\n',
         f'- **删除组合**: {len(removed)} 行\n',
         f'- **时间值补全**（旧库为空/新库有值）: {len(filled)} 行\n',
         f'- **时间值变化**: {len(changed)} 行\n\n']
    for title, data, cols in [('新增组合', added, 7), ('删除组合', removed, 4),
                              ('时间值补全', filled, 7), ('时间值变化', changed, 7)]:
        L.append(f'## {title}（{len(data)}）\n\n')
        if data:
            L.append('| 胶片 | 显影液 | 稀释 | ISO | 温度 | 旧值(35/120/页) | 新值(35/120/页) |\n|---|---|---|---|---|---|---|\n')
            for k, v in list(data.items())[:300]:
                film, dev, dil, iso, temp = k
                if cols == 4:  # removed (v1 格式)
                    old = ' / '.join(x or '—' for x in v[:3])
                    new = '（已删除）'
                elif title == '新增组合':
                    old = '（无）'
                    new = ' / '.join(v[3:6] if len(v) > 6 else [x or '—' for x in v[:3]])
                else:
                    ov, nv = v
                    old = ' / '.join(x or '—' for x in ov[:3])
                    new = ' / '.join(x or '—' for x in nv[3:6])
                L.append(f'| {film} | {dev} | {dil} | {iso} | {temp} | {old} | {new} |\n')
        L.append('\n')
    open(OUT, 'w', encoding='utf-8').write(''.join(L))
    print(f'新增 {len(added)} | 删除 {len(removed)} | 补全 {len(filled)} | 变化 {len(changed)}')
    print('报告 →', OUT)
    json.dump({'added': [list(k) for k in added], 'removed': [list(k) for k in removed],
               'filled': [list(k) for k in filled], 'changed': [list(k) for k in changed]},
              open(os.path.join(BASE, 'data', 'update_diff.json'), 'w'), ensure_ascii=False)

if __name__ == '__main__':
    main()
