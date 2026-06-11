import json
from pathlib import Path
checks = ['shilv','zhulv','caohuang','guhuang','shuilv','tuhuang','biqing','youlv','maolv','tenghuang','yuebai','yinzhu','mihuang','gancaohuang','yalv','xinghuang','ouhe','minglv','xianlv']
for c in checks:
    p = Path('data/poetry') / f'{c}.json'
    if p.exists():
        d = json.loads(p.read_text(encoding='utf-8'))
        n = len(d.get('entries',[]))
        label = d['color']
        print(f'{label:6s} {n}条')
    else:
        print(f'{c} 文件不存在')
