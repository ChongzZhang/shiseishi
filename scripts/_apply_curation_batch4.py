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
    "yunfengbai", "jingtianlan", "yunshanlan", "oulan", "yueyingbai", "danlanhui",
    "zhanjianhui", "waguanhui", "qinghui", "gelan", "anlan", "haitianlan",
    "qingshuilan", "pubulan", "kongquelan", "zhuhuanglv", "meidielv", "koushaolv",
    "danfanlan", "bingshanlan", "wanbolan", "qingtinglan", "yuqinlan", "xiayunhui",
    "huanghunhui", "huilan", "shenhuilan", "yuzanlv", "qingfanlv", "caoyuanyuanlv",
    "wuzhilv", "langhualv", "haiwanglv", "minghui",
)

save("xinghui", load("xinghui")["entries"][:3])

d = load("yuebai")
save("yuebai", [d["entries"][0], d["entries"][2], d["entries"][3], d["entries"][4]])

save("shilv", [load("shilv")["entries"][0], load("shilv")["entries"][1], load("shilv")["entries"][3]])

save("fenlv", [load("fenlv")["entries"][0], load("fenlv")["entries"][4]])

save("maolv", [load("maolv")["entries"][1], load("maolv")["entries"][2]])

save("maimiaolv", load("maimiaolv")["entries"][:2])

save("tonglv", [load("tonglv")["entries"][0], load("tonglv")["entries"][2], load("tonglv")["entries"][3]])

save("zhulv", load("zhulv")["entries"][:2])

save("lanlv", [load("lanlv")["entries"][1], load("lanlv")["entries"][2]])

save("cuilan", load("cuilan")["entries"][:2])

save("xiakeqing", [load("xiakeqing")["entries"][0]])

print("batch4 done")
