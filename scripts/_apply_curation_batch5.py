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
    "danlvhui", "feiquanlv", "langyanhui", "shenhailv", "changshihui", "mangconglv",
    "dancuilv", "tianyuanlv", "kongquelv", "gongdianlv", "songshuanglv", "danbaishilv",
    "bohelv", "wasonglv", "heyelv", "tianluolv", "baiqucailv", "hetunhui", "enyoulv",
    "hujishenglv", "yunshanlv", "nenjulv", "aibeilv", "jialingshuilv", "yusuilv",
    "baoshilv", "haimeilv", "ganlanshilv", "luweilv", "huaihuahuanglv", "pingguolv",
    "diehuang", "ganlanhuanglv", "yingwulv", "hanbaiyu", "yudubai", "zhenzhuhui",
    "yanhui",
)

save("canglv", load("canglv")["entries"])

d = load("minglv")
save("minglv", d["entries"][2:5])

save("cuilv", load("cuilv")["entries"])
save("danlv", load("danlv")["entries"][:3])
save("conglv", [load("conglv")["entries"][2]])
save("ailv", load("ailv")["entries"][:2])

d = load("xianlv")
save("xianlv", [d["entries"][1], d["entries"][2], d["entries"][3]])

save("yaohuang", load("yaohuang")["entries"])

d = load("shuilv")
save("shuilv", [d["entries"][0], d["entries"][1], d["entries"][3]])

d = load("yalv")
save("yalv", [d["entries"][0], d["entries"][1], d["entries"][4]])

save("youlv", load("youlv")["entries"][:2])
save("xiangyabai", [load("xiangyabai")["entries"][0]])

d = load("xuebai")
save("xuebai", [d["entries"][0], d["entries"][4]])

save("zhonghui", [load("zhonghui")["entries"][2]])

d = load("yehui")
save("yehui", [d["entries"][0], d["entries"][2], d["entries"][3]])

print("batch5 done")
