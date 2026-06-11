"""
从原始诗词文本中提取含颜色词的诗句 —— 按联（上下两句）输出
来源：唐诗三百首、宋词三百首、陶渊明集、谢灵运集、红楼梦
"""
import re, os

ROOT = r"C:\Users\zhangcz\Desktop\游戏\识色赋诗"
RAW = os.path.join(ROOT, "data", "raw")

COLORS = [
    "红", "朱", "赤", "丹", "绛", "绯", "殷", "彤", "赭", "茜", "胭脂",
    "绿", "碧", "翠", "青", "苍", "葱", "缥", "黛",
    "蓝", "靛", "绀",
    "黄", "缃", "橙",
    "白", "素", "皓", "皎", "皑", "皙", "银", "霜色",
    "黑", "乌", "墨", "皂", "缁",
    "紫",
    "灰", "褐", "棕", "粉", "缟",
]
PAT = re.compile("|".join(COLORS))

BLACKLIST = re.compile(
    "玄宗|玄武|玄都|金陵|金门|金谷|金吾|金石|金舆"
    "|黄金|金樽|金屋|金风|金波|金炉|金盘|金徽"
    "|金貂|金茎|金殿|金钥|金甲"
    "|明珠|明月|明星|天明|清明|光明|月明|灯明|明镜|明时|明朝|明年|明日|明妃|明君"
    "|青楼|司马青衫|青鸟|踏青|青阳"
    "|白玉|白帝|白衣|白首|白屋|白水"
    "|赤壁|赤帝|赤城|赤松"
    "|黄泉|黄昏|黄花|黄莺|黄鹤|黄龙"
    "|紫微|紫宸|紫陌|紫府|紫烟"
    "|丹墀|丹陛|丹心|丹青"
    "|碧落|碧空|碧霄|碧海"
    "|绿珠|绿绮"
    "|红楼|红尘|红颜"
    "|乌云|乌衣"
    "|黑水|黑头"
    "|彩云|彩虹|彩笔|五彩"
    "|素手|素衣|素书|尺素|素心"
    "|银烛|银汉|银屏|银灯|银台|银床"
)


def extract_couplets(poem_text):
    """从一首诗的全文提取含颜色词的联（上下两句含逗号的部分）"""
    # Remove押韵 annotations
    poem_text = re.sub(r'\(押\w+韻\)', '', poem_text)
    poem_text = poem_text.replace('○', ' ')

    # Split by period to get full sentences
    sentences = re.split(r'[。！？]', poem_text)
    
    couplets = []
    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue
        
        # A couplet has comma (逗号) separating upper/lower halves
        if '，' not in sent and ',' not in sent:
            # Single clause - check if it contains color and is long enough
            if len(sent) >= 7 and PAT.search(sent) and not BLACKLIST.search(sent):
                couplets.append(sent)
            continue
        
        # Split by comma to get halves
        halves = re.split(r'[，,]', sent)
        halves = [h.strip() for h in halves if h.strip()]
        
        if len(halves) < 2:
            continue
        
        # Check consecutive pairs for color words
        for i in range(len(halves) - 1):
            pair = halves[i] + "，" + halves[i + 1]
            if PAT.search(pair) and not BLACKLIST.search(pair):
                # Only add if at least one half is reasonable length
                if len(halves[i]) >= 3 and len(halves[i+1]) >= 3:
                    couplets.append(pair)
    
    return couplets


def extract_tang300():
    path = os.path.join(RAW, "tang300.txt")
    if not os.path.exists(path): return []
    text = open(path, encoding='utf-8').read()
    results = []
    blocks = re.split(r'\n(?=詩名:)', text)
    for block in blocks:
        title = author = poem = ""
        for line in block.split('\n'):
            line = line.strip()
            if line.startswith('詩名:'): title = line[3:].strip()
            elif line.startswith('作者:'): author = line[3:].strip()
            elif line.startswith('詩文:'): poem = line[3:].strip()
        if poem:
            for cp in extract_couplets(poem):
                results.append((cp, title, author, "唐三百"))
    return results


def extract_song300():
    path = os.path.join(RAW, "song300.txt")
    if not os.path.exists(path): return []
    text = open(path, encoding='utf-8').read()
    results = []
    blocks = re.split(r'\n(?=詞牌:)', text)
    for block in blocks:
        title = author = poem = ""
        for line in block.split('\n'):
            line = line.strip()
            if line.startswith('詞牌:'): title = line[3:].strip()
            elif line.startswith('作者:'): author = line[3:].strip()
            elif line.startswith('詞文:'): poem = line[3:].strip()
        if poem:
            for cp in extract_couplets(poem):
                results.append((cp, title, author, "宋三百"))
    return results


def extract_hongloumeng():
    path = os.path.join(RAW, "hongloumeng.txt")
    if not os.path.exists(path): return []
    text = open(path, encoding='utf-8').read()
    results = []
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    title = ""
    for line in lines:
        if line.startswith('#') or 'http' in line or '简书' in line:
            continue
        if not re.search(r'[，。！？]', line) and len(line) <= 20:
            title = line.strip('#').strip()
            continue
        for cp in extract_couplets(line):
            results.append((cp, title, "曹雪芹", "红楼梦"))
    return results


def extract_generic(fname, src, author):
    path = os.path.join(RAW, fname)
    if not os.path.exists(path): return []
    text = open(path, encoding='utf-8').read()
    results = []
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    title = ""
    for line in lines:
        if any(kw in line for kw in ['http', 'github', 'dooshu', '古诗库', '陶渊明集', '谢灵运全集']):
            continue
        if len(line) <= 25 and not re.search(r'[，。！？]', line):
            title = line
            continue
        for cp in extract_couplets(line):
            results.append((cp, title, author, src))
    return results


all_results = []
for fn, label in [("唐诗三百首", extract_tang300), ("宋词三百首", extract_song300),
                    ("红楼梦", extract_hongloumeng), ("陶渊明集", lambda: extract_generic("taoyuanming.txt", "陶渊明集", "陶渊明")),
                    ("谢灵运集", lambda: extract_generic("xielingyun.txt", "谢灵运集", "谢灵运"))]:
    print(f"{fn}...", end=" ")
    r = label()
    print(f"{len(r)} 联")
    all_results.extend(r)

# 去重
seen = set()
unique = []
for line, title, author, source in all_results:
    if line not in seen:
        seen.add(line)
        unique.append((line, title, author, source))

print(f"\n去重后合计: {len(unique)} 联")

# 输出
out = os.path.join(ROOT, "data", "color_poems.txt")
with open(out, 'w', encoding='utf-8') as f:
    f.write("色谱寻诗 - 含颜色词诗句提取（按联）\n")
    f.write("来源: 唐诗三百首 · 宋词三百首 · 陶渊明集 · 谢灵运集 · 红楼梦\n")
    f.write("=" * 60 + "\n\n")

    by_src = {}
    for line, title, author, source in sorted(unique, key=lambda x: (x[3],)):
        by_src.setdefault(source, []).append((line, title, author))

    for src in ["唐三百", "宋三百", "陶渊明集", "谢灵运集", "红楼梦"]:
        items = by_src.get(src, [])
        if not items: continue
        f.write(f"━━━ {src} ({len(items)}联) ━━━\n\n")
        for line, title, author in items:
            f.write(f"  {line}\n")
            f.write(f"    ——《{title}》 {author}\n\n")

    f.write("\n" + "=" * 60 + "\n")
    f.write(f"总计: {len(unique)} 联\n")

print(f"已保存: {out}")
