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

# ---- black & white reversal (正冲/反转冲洗) kits & processes ----
# 来源：Rollei B&W Reversal Kit 说明书（2020，Agenzia Luce）、Adox Scala Kit 数据表（2021）、
#       Ilford "Reversal Processing" 技术文档（2019-06）
reversal = [
    {
        'id': 'rollei_kit',
        'kit': 'Rollei B&W Reversal Kit（黑白反转套药）',
        'temp': 24,
        'note': '加工温度 24°C（配药 24°C±2°C）。首显液 1A+1B+8 水；二显 1+9。一套可处理 30-36 卷。'
                '想更浅的幻灯片可把首显/二显各加 5%，想更深则各减 5%。',
        'steps': [
            ['首显', '见表', '开始倒置 10 次，之后每 30 秒倒置 1 次'],
            ['水洗', '2:00', '流水'],
            ['漂白', '5:00', '每 30 秒 1 次，或换水 3-5 次'],
            ['水洗', '2:00', '流水'],
            ['清洁浴', '3:00', '每 30 秒 1 次'],
            ['二次曝光', '3:00', '100-200W 灯，距离 30-50cm'],
            ['二显', '见表', '1+9'],
            ['停显', '1:00', '1+19，缓慢倒置'],
            ['定影', '7:00', '1+4，开始倒置 10 次，之后每 60 秒 1 次'],
            ['水洗', '—', '流水或换水 10-15 次'],
            ['最终浴', '1:00', '1+100，极慢持续倒置'],
        ],
        'films': [
            ['Rollei Superpan 200', '200', 9.0, 6.75],
            ['Rollei Retro 400S', '400', 9.5, 7.25],
            ['Rollei RPX 25', '25', 5.0, 3.75],
            ['Rollei Retro 80S', '80', 15.75, 11.75],
            ['Rollei RPX 100', '100', 15.75, 11.75],
            ['Rollei RPX 400', '400', 16.25, 12.25],
            ['Agfa Copex Rapid', '50', 6.5, 5.0],
            ['Ilford Delta 100', '100', 16.5, 12.5],
            ['Ilford Delta 400', '400', 16.5, 12.5],
            ['Kodak TX 400', '400', 16.0, 12.0],
        ],
    },
    {
        'id': 'adox_scala',
        'kit': 'Adox Scala Reversal Kit（SCALA 反转套药）',
        'temp': 20,
        'note': '二显直接复用首显液（用后废弃）。一套可处理 8 卷 35mm/120。'
                'Jobo 滚冲机：首显/漂白/清洁/二显时间全部缩短 15%。',
        'steps': [
            ['首显', '11:30（Scala 50 @20°C）', '连续搅拌 1 分钟，之后每 30 秒 5-10 秒'],
            ['水洗', '2:30', '流水'],
            ['漂白', '4:00', '可全程缓慢连续搅拌'],
            ['水洗', '2:30', '流水'],
            ['清洁浴', '4:00', ''],
            ['水洗', '3:00', '流水'],
            ['二次曝光', '2:00 每面', '日光/灯光下翻面各 2 分钟'],
            ['二显', '6:00', '复用首显液（1+1 稀释液）'],
            ['最终水洗', '6-10:00', '流水'],
        ],
        'films': [
            ['Adox Scala 50', '50', 11.5, 6.0],
            ['Adox Scala 160', '160', 8.0, 6.0],
        ],
    },
    {
        'id': 'ilford_pq',
        'kit': 'Ilford PQ Universal 反转流程（自行配药）',
        'temp': 20,
        'note': '适用于 Pan F Plus（强烈推荐）、FP4 Plus、Delta 100 Professional；不推荐 HP5 Plus / Delta 400（反差过低）。'
                '首显液 = PQ Universal 1+5 + 硫代硫酸钠（Pan F+ 加 8g/L；FP4+/Delta 100 加 12g/L）。'
                '漂白液 = 高锰酸钾 2g/500ml + 硫酸 10ml/490ml，用时等量混合。',
        'steps': [
            ['首显', '12:00', '每 60 秒倒置 10 秒；时间可调（更长=更浅）'],
            ['首洗', '5:00', '流水'],
            ['漂白', '5:00', '连续搅拌，直到银影完全褪去'],
            ['二洗', '1:00', '流水'],
            ['清洁浴', '2:00', '亚硫酸氢盐 25g/L，连续倒置'],
            ['三洗', '1:00', '流水'],
            ['二次曝光', '0:30-1:00 每面', '100W 钨丝灯 46cm，或荧光灯 30cm'],
            ['二显', '6:00', 'PQ Universal 1+9 新配'],
            ['四洗', '1:00', '流水'],
            ['定影', '5:00', 'Rapid Fixer 1+4 或 Hypam 1+4'],
        ],
        'films': [
            ['Ilford Pan F Plus', '50', 12.0, 6.0],
            ['Ilford FP4 Plus', '125', 12.0, 6.0],
            ['Ilford Delta 100 Professional', '100', 12.0, 6.0],
        ],
    },
]

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
    'reversal': reversal,
}

out_path = os.path.join(BASE, 'web', 'data_web.js')
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w', encoding='utf-8') as f:
    f.write('window.DEVDB = ')
    json.dump(web, f, ensure_ascii=False, separators=(',', ':'))
    f.write(';\n')
print(f"web data: {os.path.getsize(out_path)/1024:.0f} KB, entries={len(entries)}")
