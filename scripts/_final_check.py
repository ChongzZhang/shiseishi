import json
from pathlib import Path
cs = json.loads(open('data/colors.json','r',encoding='utf-8').read())
print(f'Total colors: {len(cs)}')
pp = Path('data/poetry')
total = 0
for c in cs:
    p = pp / (c['pinyin'] + '.json')
    n = len(json.loads(p.read_text(encoding='utf-8')).get('entries',[])) if p.exists() else 0
    total += n
    marker = "" if n > 0 else " <-- ZERO!"
    print(f'{c["name"]:12s} {n:3d} poems{marker}')
print(f'\nTotal poems: {total}')
print(f'All colors have poems: {total >= len(cs)}')
