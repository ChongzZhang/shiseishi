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

def clear(*pinyins):
    for p in pinyins:
        save(p, [])

clear(
    "biandouhuahong","baijihong","nenlinghong","cujiangcaohong","yangcongzi",
    "haixiangzi","gutongzi","shiruihong","shaoyaogenghong","canghuahong",
    "chuhehong","mabiancaozi","dingxiangdanzi","danzihong","danqianniuzi",
    "fengxinzi","luolanzi","meiguizi","tengluozi","jiegengzi","zhilanzi",
    "lingmenghong","longxuhong","dianqishihong","yingcaozi","lusuihui",
    "yinhonghui","muyunhui","banjiuhui","dantengluozi","danqingzi",
    "qinghakezi","doukouzi","biandouzi","jiehuazi","gejinzi","qianniuzi",
    "longjingyuzi","biqizi","jinghong","bogenhong",
)

save("ganzi", [{
    "line":"一泓绀紫澄碧，中有睡蛟龙。","title":"水调歌头","author":"王质","type":"词",
    "source":"宋词/ci.song.10000.json#102","matchTier":2,"verified":True
}])

save("meiguihong", [{
    "line":"玫瑰红被径，薜荔绿走墙。","title":"刘无损欲书十扇以韦苏州乔木生夏凉流云吐华月句作韵  其五","author":"王安中","type":"诗",
    "source":"全唐诗/poet.song.80000.json#478","matchTier":1,"verified":True
}])

save("weizi", [
    {"line":"一声啼鴂画楼东，魏紫姚黄扫地空。","title":"芍药四首  其三","author":"邵雍","type":"诗","source":"全唐诗/poet.song.22000.json#454","matchTier":1,"verified":True},
    {"line":"一年春色摧残尽，更觅姚黄魏紫看。","title":"再赋简养正","author":"范成大","type":"诗","source":"全唐诗/poet.song.138000.json#664","matchTier":1,"verified":True},
    {"line":"丽黄啼晓霁，魏紫笑春深。","title":"步西湖次韵徐南卿  其一","author":"陈造","type":"诗","source":"全唐诗/poet.song.151000.json#219","matchTier":1,"verified":True},
])

save("luhui", [
    {"line":"伊谁补漏天，吾州与芦灰。","title":"欲晴又雨终夕震电","author":"薛季宣","type":"诗","source":"全唐诗/poet.song.155000.json#66","matchTier":1,"verified":True},
    {"line":"芦灰迷桂晕，梁屋掩霞朝。","title":"洛城秋雨","author":"宋庠","type":"诗","source":"全唐诗/poet.song.10000.json#569","matchTier":1,"verified":True},
    {"line":"习习芦灰上，泠泠玉管中。","title":"八风从律","author":"蒋防","type":"诗","source":"全唐诗/poet.tang.27000.json#277","matchTier":1,"verified":True},
])

save("zihui", [{
    "line":"清泉沈金彩，古烟凝紫灰。","title":"铜雀研","author":"周文璞","type":"诗",
    "source":"全唐诗/poet.song.183000.json#739","matchTier":1,"verified":True
}])

save("qinglian", [
    {"line":"云根露奇怪，上有青莲宫。","title":"游南山寺题澹轩","author":"王炎","type":"诗","source":"全唐诗/poet.song.160000.json#680","matchTier":1,"verified":True},
    {"line":"何妨试向朱门去，会有青莲一朵开。","title":"崇上人携育王书归行化因以山偈勉之","author":"虞俦","type":"诗","source":"全唐诗/poet.song.154000.json#465","matchTier":1,"verified":True},
    {"line":"兹晨幸休暇，共步青莲界。","title":"冬日予与六人者游焦山谒圜禅师访瘗鹤铭断碑及焦公丹台怆然有怀兼柬朱陈二友陈方病目而朱校易未毕","author":"周孚","type":"诗","source":"全唐诗/poet.song.155000.json#328","matchTier":1,"verified":True},
])

print("batch2 done")
