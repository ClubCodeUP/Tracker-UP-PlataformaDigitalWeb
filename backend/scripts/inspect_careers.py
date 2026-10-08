import glob
import json

files = sorted(glob.glob('backend/data/curricula/*.json'))
for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        d = json.load(fp)
        c = d['carrera']
        print(f"{c.get('id')}: {c.get('codigo')} - {c.get('nombre')} ({c.get('facultad')})")

