#!/usr/bin/env python3
"""Curate Foma official development times (from Foma Products Catalogue, FOMA BOHEMIA,
pages 7-8, verified against the layout-mode extraction of Foma_BW_dev_info.pdf).
Times are for spiral-tank processing at 20C: 30s continuous agitation + 10s at each minute.
"""
import csv, os

OUT = os.path.join(os.path.dirname(__file__), 'data', 'official_foma.csv')

# (developer, dilution, film, t_min, t_max, note)
rows = []
def add(dev, dil, f100, f200, f400, retro, note=''):
    for film, v in [('Fomapan 100 Classic', f100), ('Fomapan 200 Creative', f200),
                    ('Fomapan 400 Action', f400), ('Retropan 320 Soft', retro)]:
        if v is None:
            continue
        if isinstance(v, tuple):
            rows.append((dev, dil, film, v[0], v[1], note))
        else:
            rows.append((dev, dil, film, v, v, note))

# Foma developers (from official table)
add('Fomadon LQN', '1+10', (7,8), (5,6), (9,10), None)
add('Fomadon LQN', '1+14', (9,10), (7,8), (12,13), None)
add('Fomadon LQR', '1+10', (5,6), (5,6), (7,8), (9,10))
add('Fomadon LQR', '1+14', (7,8), (7,8), (9,10), (12,13))
add('Fomadon R09', '1+25', (4,4), (5,5), (6,6), (7,8), 'medium contrast g=0.65')
add('Fomadon R09', '1+50', (9,9), (10,10), (12,12), (14,16), 'medium contrast g=0.65')
add('Fomadon R09', '1+100', (20,22), (24,26), (32,34), None)
add('Fomadon P', 'Stock', (7,8), (5,6), (10,11), None)
add('Fomadon Excel', 'Stock', (5,6), (6,7), (7,7), None)
add('Foma Universal', '1+3', (5,5), (3.5,3.5), (7.5,7.5), None)
add('Retro Special Developer', 'Stock', (3,4), (3,4), (3,4), (4,5))

# Foreign developers
add('Kodak XTOL', 'Stock', (5,6), (6,7), (7,7), None)
add('Kodak T-MAX Developer', '1+4', (5,6), (5,6), (7,8), None)
add('Kodak HC-110', '1+31 (Dil.B)', None, None, (6.5,6.5), None)
add('Ilford ID-11 / Kodak D-76', 'Stock', (6,7), (5,6), (7,8), None)
add('Ilford ID-11', '1+1', (8,10), (8,9), (12,13), None)
add('Ilford ID-11', '1+3', (15,16), (12,13), (22,23), None)
add('Ilford Microphen', 'Stock', (5,7), (5,6), (8,9), None)
add('Ilford Microphen', '1+1', (8,9), None, (12,13), None)
add('Ilford Microphen', '1+3', (13,14), (12,13), (24,25), None)
add('Ilford Perceptol', 'Stock', (8,8), (6,6), (9,10), None)
add('Ilford Perceptol', '1+1', (10,11), (7.5,7.5), None, None)
add('Ilford Perceptol', '1+3', (14,15), (12,13), None, None)
add('Ilford Ilfosol S', '1+9', (6,7), (3.5,3.5), (6,6), None)
add('Ilford Ilfosol S', '1+14', (7,8), (5,6), (11,12), None)
add('Tetenal Emofin', 'Liquid', (4,5), (4,5), (6,7), None)
add('Tetenal Emofin', 'Powder', (4,6), (6,8), (6,8), None)
add('Tetenal Ultrafin Plus', '1+4', (5,5), (5,5), (7,8), None)
add('Tetenal Ultrafin Plus', '1+6', (7.5,7.5), (7,8), (11,12), None)
add('Tetenal Ultrafin T-Plus', '1+4', (4.5,5), (6,6.5), (7.5,8), None)
add('Tetenal Ultrafin Liquid', '1+20', (7.5,7.5), (7.5,7.5), (15,15), None)

with open(OUT, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['developer', 'dilution', 'film', 'temp_c', 't_min_minutes', 't_max_minutes', 'notes'])
    for r in sorted(rows, key=lambda r: (r[2], r[0])):
        w.writerow([r[0], r[1], r[2], 20, r[3], r[4], r[5]])
print(f"rows: {len(rows)}")
