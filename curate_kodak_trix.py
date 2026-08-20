#!/usr/bin/env python3
"""Curate Kodak Tri-X 400 (400TX) official development times from Kodak datasheet
F-4017 (verified against layout-mode extraction of Kodak_Tri-X.pdf).
Small tank = inversion agitation every 30s; Large tank = manual agitation every 60s.
Temps: 65F/18C, 68F/20C, 70F/21C, 72F/22C, 75F/24C.
"""
import csv, os

OUT = os.path.join(os.path.dirname(__file__), 'data', 'official_kodak_trix.csv')

TEMPS = [18, 20, 21, 22, 24]
# developer: (small_tank[5], large_tank[5])  None = NR
TABLE = {
    'T-MAX':        ([6.75, 6, 5.5, 4.75, None], [None, None, None, None, None]),
    'T-MAX RS':     ([4.75, 4.5, 4.25, 4, 3.5], [5.5, 5, 4.75, 4.5, 4]),
    'HC-110 (Dil B)': ([4.5, 3.75, 3.5, 3, 2.5], [5, 4.5, 4, 3.5, 3]),
    'D-76':         ([8, 6.75, 6.25, 5.5, 4.75], [9.25, 7.75, 7, 6.5, 5.5]),
    'D-76 (1:1)':   ([10.75, 9.75, 9, 8.5, 7.75], [12.25, 11, 10.5, 9.75, 8.75]),
    'XTOL':         ([8, 7, 6.25, 5.75, 4.75], [9.25, 8, 7.25, 6.5, 5.5]),
    'XTOL (1:1)':   ([10, 9, 8.5, 8, 7.25], [11.5, 10.5, 9.75, 9.25, 8.25]),
    'MICRODOL-X':   ([10.25, 9.25, 8.75, 8.25, 7.5], [11.75, 10.75, 10, 9.5, 8.5]),
    'MICRODOL-X (1:3)': ([18.75, 17, 16, 15, 13.5], [None, 19.5, 18.25, 17.25, 15.5]),
    'DK-50 (1:1)':  ([7, 6, 5.5, 5, 4.5], [7.5, 6.5, 6, 5.5, 5]),
}

with open(OUT, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['film', 'developer', 'iso', 'temp_c', 'agitation', 'time_min'])
    for dev, (small, large) in TABLE.items():
        for temp, t in zip(TEMPS, small):
            if t is not None:
                w.writerow(['Kodak Tri-X 400', dev, 400, temp, 'inversion 30s', t])
        for temp, t in zip(TEMPS, large):
            if t is not None:
                w.writerow(['Kodak Tri-X 400', dev, 400, temp, 'large-tank 60s', t])
print("rows written")
