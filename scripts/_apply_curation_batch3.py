import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
poetry = root / "data/poetry"

def load(pinyin):
    return json.loads((poetry / f"{pinyin}.json").read_text(encoding="utf-8"))

def save(pinyin, entries):
    data = load(pinyin)
    data["entries"] = entries
    data["coverage"] = f"{len(entries)}/5"
    (poetry / f"{pinyin}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

def clear(*pinyins):
    for p in pinyins:
        save(p, [])

clear(
    "gudinghui", "wumeizi", "shenqianniuzi", "yuanshanzi", "danlanzi", "luodianzi",
    "manaohui", "yejuzi", "mantianxingzi", "yeputaozi", "longkuizi", "anlongdanzi",
    "jingshizi", "anlanzi", "jingtailan", "niluolan", "yuantianlan", "xinglan",
    "yushandoulan", "honglan", "hushuilan", "qiubolan", "jianshilan", "jiqing",
    "baoshilan", "bolinlan", "yuanweilan", "qianniuhualan", "feiyancaolan",
    "yinyubai", "ananlan", "yuweihui", "jingyuhui", "haishenhui", "shayuhui",
    "yunshuilan", "qingshanlan", "dalishihui", "haitaolan", "diechilan", "haijunlan",
    "shuiniuhui", "niujiaohui", "yanhanlan",
)

d = load("yinbai")
save("yinbai", d["entries"][:3])

d = load("jianfengzi")
save("jianfengzi", [d["entries"][0]])

d = load("huaqing")
save("huaqing", [d["entries"][1], d["entries"][2], d["entries"][4]])

d = load("biqing")
save("biqing", [d["entries"][2]])

d = load("tianlan")
save("tianlan", [d["entries"][0]])

d = load("haiqing")
save("haiqing", [d["entries"][1], d["entries"][4]])

print("batch3 done")
