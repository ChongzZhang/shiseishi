import json
from pathlib import Path
colors = json.loads(open('data/colors.json', encoding='utf-8').read())
poetry = Path('data/poetry')
zero = []
for c in colors:
    p = poetry / (c['pinyin'] + '.json')
    n = 0
    if p.exists():
        n = len(json.loads(p.read_text(encoding='utf-8')).get('entries', []))
    if n == 0:
        zero.append(c)
print(f'无诗句色名: {len(zero)}')
for z in zero:
    print(f"  {z['name']:10s} {z['pinyin']:25s} hex={z['hex']} RGB={z['RGB']}")
