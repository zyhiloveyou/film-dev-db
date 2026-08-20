#!/usr/bin/env python3
"""Parse Rollei film datasheet development time tables (extracted text)."""
import csv, glob, os, re

SRC = os.path.join(os.path.dirname(__file__), 'sources', 'rollei')
OUT = os.path.join(os.path.dirname(__file__), 'data', 'official_rollei.csv')

INLINE_RE = re.compile(r'^(.+?)\s+(\d{2,4})/(\d{1,2})°\s*(.*)$')
ISO_RE = re.compile(r'^(\d{2,4})/(\d{1,2})°\s*(.*)$')
DIL_RE = re.compile(r'^(1\s*\+\s*\d+|2\s*\+\s*\d+|Stock|B\s*\(\s*1\s*\+\s*\d+\))\s+(.+)$')
BARE_DIL_RE = re.compile(r'^(1\s*\+\s*\d+|2\s*\+\s*\d+|Stock|B\s*\(\s*1\s*\+\s*\d+\))$')
BARE_TIME_RE = re.compile(r'^(\d+:\d{2}|\d+(?:[.,]\d+)?)$')

def parse_time(tok):
    tok = tok.strip()
    m = re.match(r'^(\d+):(\d{2})$', tok)
    if m:
        return round(int(m.group(1)) + int(m.group(2)) / 60, 2)
    m = re.match(r'^(\d+(?:[.,]\d+)?)$', tok)
    if m:
        return float(m.group(1).replace(',', '.'))
    return None

def split_dil_time(tail):
    toks = tail.split()
    for i in range(len(toks) - 1, -1, -1):
        t = parse_time(toks[i])
        if t is not None:
            dil = ' '.join(toks[:i]).replace(' ', '') or None
            temp = 20
            m = re.search(r'\((\d{2})°', ' '.join(toks[i + 1:]))
            if m:
                temp = int(m.group(1))
            return dil, t, temp
    return None, None, None

def main():
    rows = []
    for fp in sorted(glob.glob(os.path.join(SRC, '*.pdf'))):
        if 'RHC' in fp or 'RPX400_Datenblatt_R190801' in fp:
            continue
        from pypdf import PdfReader
        txt = "\n".join((p.extract_text() or '') for p in PdfReader(fp).pages)
        i = txt.find('DEVELOPER ISO')
        if i < 0:
            continue
        j = txt.find('PUSH & PULL', i)
        k = txt.find('PRE-WATERING', i)
        ends = [x for x in (j, k) if x > 0]
        block = txt[i:min(ends) if ends else i + 8000]

        fname = os.path.basename(fp)
        film = ('Rollei RPX 100' if 'RPX100' in fname else
                'Rollei RPX 25' if 'RPX25' in fname else
                'Rollei RPX 400' if 'RPX400' in fname else
                'Rollei Retro 80S' if 'Retro80S' in fname else
                'Rollei Superpan 200')
        dev = None
        last_iso = None
        last_dil = None
        pending_dil = None
        for line in block.splitlines():
            line = line.strip()
            if not line or 'DEVELOPER ISO' in line or line.startswith('DEVELOPMENT'):
                continue
            m = INLINE_RE.match(line)
            if m:
                dev, iso, tail = m.group(1).strip(), int(m.group(2)), m.group(4).strip()
                last_iso = iso
                last_dil = None
                pending_dil = None
                if tail:
                    dil, t, temp = split_dil_time(tail)
                    if t is not None:
                        if dil is None:
                            dil = last_dil
                        else:
                            last_dil = dil
                        rows.append([film, dev, iso, dil, temp, t])
                continue
            m = ISO_RE.match(line)
            if m:
                iso, tail = int(m.group(1)), m.group(3).strip()
                last_iso = iso
                if tail:
                    dil, t, temp = split_dil_time(tail)
                    if t is not None:
                        if dil is None:
                            dil = last_dil
                        else:
                            last_dil = dil
                        rows.append([film, dev, iso, dil, temp, t])
                continue
            m = DIL_RE.match(line)
            if m and last_iso is not None:
                dil, t, temp = split_dil_time(m.group(2))
                if t is not None:
                    last_dil = m.group(1).replace(' ', '')
                    rows.append([film, dev, last_iso, last_dil, temp, t])
                continue
            mb = BARE_DIL_RE.match(line)
            if mb:
                pending_dil = mb.group(1).replace(' ', '')
                continue
            if BARE_TIME_RE.match(line) and last_iso is not None and pending_dil:
                rows.append([film, dev, last_iso, pending_dil, 20, float(line.replace(',', '.'))])
                continue
            if len(line) < 45 and not line[0].isdigit() and '°' not in line and '/' not in line:
                dev = line
                last_dil = None
                pending_dil = None
    # dedupe
    seen = set()
    out = []
    for r in rows:
        key = tuple(r)
        if key not in seen:
            seen.add(key)
            out.append(r)
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['film', 'developer', 'iso', 'dilution', 'temp_c', 'time_min'])
        w.writerows(sorted(out, key=lambda r: (r[0], r[1], str(r[2]), str(r[3]))))
    print(f"rows: {len(out)}")

if __name__ == '__main__':
    main()
