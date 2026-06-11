import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
cs = json.loads((ROOT / 'data/colors.json').read_text(encoding='utf-8'))
targets = ['jinglan','yalv','canglan','jinzi','putaojiuhong','meihong','meiguizi',
           'jiazhutaohong','walv','yanlan','danzhe','fupenzihong','nenhui','chanlv','yuanweilan','shuilv']
for c in cs:
    if c['pinyin'] in targets:
        print(f"{c['name']:10s} {c['pinyin']:20s} hex={c['hex']}")
