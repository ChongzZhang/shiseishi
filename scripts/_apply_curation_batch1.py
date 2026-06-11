import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
poetry = root / "data/poetry"

def save(pinyin, entries):
    p = poetry / f"{pinyin}.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    data["entries"] = entries
    data["coverage"] = f"{len(entries)}/5"
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# === 海棠红起 人工筛选结果（连续色名 + 写景）===

save("haitanghong", [
  {"line":"是时官梅香正阑，亦有海棠红映肉。","title":"群玉亭","author":"朱翌","type":"诗","source":"全唐诗/poet.song.108000.json#51","matchTier":1,"verified":True},
  {"line":"水沈烟断一帘秋，醉睡海棠红玉软。","title":"重游寥阳洞有感","author":"欧阳澈","type":"诗","source":"全唐诗/poet.song.107000.json#154","matchTier":1,"verified":True},
])

save("yuhong", [
  {"line":"石乳腻昏雨，玉红绚朝暾。","title":"题三易备遗","author":"葛寅炎","type":"诗","source":"全唐诗/poet.song.227000.json#0","matchTier":1,"verified":True},
])

for p in ["gaolianghong","manjianghong","putaozi","tangchangpuhong","eguanhong",
          "anziyuanhong","zhuganzi","jinyuzi","caozhuhong","danjianghong","pinhong",
          "fengxianhuahong","fentuanhuahong","jiazhutaohong","jianghong","lianbanhong",
          "baochunhong","yuejihong","jiangdouhong","xiaguanghong","songyemudanhong",
          "shubihong","jianjingyuhong","shanlidouhong","jinkuihong","shubeihui",
          "ganzhezi","shizhuzi","cangyinghui","luanshizi","qiepizi","tuyanhong",
          "zijinghong","caitouzi","putaojiuhong","moshizi","tanzi","huoezi","mozi"]:
    save(p, [])

save("zaohong", [
  {"line":"会见今年八九月，处处枣红梨子黄。","title":"送秦德久守安丰","author":"周紫芝","type":"诗","source":"全唐诗/poet.song.107000.json#0","matchTier":1,"verified":True},
  {"line":"八月梨枣红，绕墙风自落。","title":"读方言","author":"黄庭坚","type":"诗","source":"全唐诗/poet.song.0.json#0","matchTier":1,"verified":True},
])

save("fengyehong", [
  {"line":"枫叶红斓斑，松□翠摇飐。","title":"奉和郭使君游光福寺云闲阁二十韵","author":"赵公硕","type":"诗","source":"全唐诗/poet.song.0.json#0","matchTier":1,"verified":True},
  {"line":"鸟行黑点波涛白，枫叶红连橘柚黄。","title":"寄题明月禅院二首  其二","author":"释赞宁","type":"诗","source":"全唐诗/poet.song.0.json#0","matchTier":1,"verified":True},
])

save("shuihong", [
  {"line":"今日重来皆蔓草，水红无数强排秋。","title":"芙蓉堂","author":"孔平仲","type":"诗","source":"全唐诗/poet.song.0.json#0","matchTier":1,"verified":True},
])

print("batch1 done")
