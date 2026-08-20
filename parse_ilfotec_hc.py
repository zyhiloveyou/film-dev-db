#!/usr/bin/env python3
"""Parse Ilfotec HC datasheet (ILFOTEC-HC-200225.pdf text) development times table."""
import csv, os, re

TXT = '/tmp/ilfotec_hc.txt'
OUT = os.path.join(os.path.dirname(__file__), 'data', 'official_ilfotec_hc.csv')

def to_min(tok):
    tok = tok.strip()
    if not tok or tok in ('–', '-', '—'):
        return None
    m = re.match(r'^(\d+):(\d{2})$', tok)
    if m:
        return round(int(m.group(1)) + int(m.group(2)) / 60, 2)
    m = re.match(r'^(\d+(?:[.,]\d+)?)$', tok)
    if m:
        return float(m.group(1).replace(',', '.'))
    return None

def main():
    txt = open(TXT).read()
    start = txt.find('ILFORD & KENTMERE FILMS')
    end = txt.find('Stop, fix, wash', start)
    block = txt[start:end]
    lines = [l.strip() for l in block.splitlines() if l.strip()]

    merged = []
    for l in lines:
        if l == 'PROFESSIONAL' and merged and 'DELTA' in merged[-1]:
            merged[-1] += ' ' + l
        else:
            merged.append(l)
    lines = merged

    COLS = [('1+11', 24), ('1+15', 20), ('1+31', 20), ('1+47', 20)]
    rows = []      # [film, iso, contrast, [t1..t4]]
    kent = []      # [film, iso, dilution, time]
    film = None
    ei = None

    for line in lines:
        up = line.upper()
        if 'DELTA' in up and 'PROFESSIONAL' in up:
            nums = re.findall(r'\d+', up)
            film = f"Ilford Delta {nums[0]} Professional" if nums else 'Ilford Delta Professional'
            continue
        if up.startswith('PANF'):
            film = 'Ilford Pan F Plus'
        elif up.startswith('FP4'):
            film = 'Ilford FP4 Plus'
        elif up.startswith('HP5'):
            film = 'Ilford HP5 Plus'
        elif up.startswith('SFX'):
            film = 'Ilford SFX 200'
        elif up.startswith('ORTHO'):
            film = 'Ilford Ortho Plus'
        elif up.startswith('KENTMERE'):
            film = 'Kentmere'
            continue
        elif up.startswith('PAN100') and film == 'Kentmere':
            film = 'Kentmere Pan 100'
            continue
        elif up.startswith('PAN400') and film == 'Kentmere':
            film = 'Kentmere Pan 400'
            continue
        if film == 'Kentmere':
            continue

        toks = line.split()

        # contrast rows (Ortho Plus): "Normal – 4:00 6:00 –"
        if 'NORMAL' in up or 'HIGH' in up:
            cells = [to_min(c) for c in toks[1:]]
            if len(cells) == 4 and any(t is not None for t in cells):
                contrast = 'Normal' if 'NORMAL' in up else 'High'
                rows.append([film, ei, contrast, cells])
            continue

        # EI rows
        m = re.search(r'EI\s+(\d+)\s*/\s*\d+', line, re.I)
        if m:
            ei = m.group(1)
            rest = line[m.end():].split()
            cells = [to_min(c) for c in rest]
            if len(cells) == 4:
                rows.append([film, ei, None, cells])
            continue

        # Kentmere bare EI: "100/21 4:00 5:00" -> 1+31, 1+47 at 20C
        m = re.match(r'^(\d{3,4})\s*/\s*\d+\s+(.*)$', line)
        if m and film and film.startswith('Kentmere'):
            tt = [to_min(t) for t in m.group(2).split()]
            if len(tt) == 2:
                kent.append([film, m.group(1), '1+31', tt[0]])
                kent.append([film, m.group(1), '1+47', tt[1]])
            continue

    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['film', 'iso', 'dilution', 'temp_c', 'time_min', 'notes'])
        for film, iso, dil, t in kent:
            w.writerow([film, iso, dil, 20, t, None])
        for film, iso, contrast, cells in rows:
            note = f"contrast={contrast}" if contrast else None
            for (dil, temp), t in zip(COLS, cells):
                if t is not None:
                    w.writerow([film, iso, dil, temp, t, note])
    print(f"rows: {len(rows) + len(kent)}")

if __name__ == '__main__':
    main()
