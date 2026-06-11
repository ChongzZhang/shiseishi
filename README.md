# 识色赋诗

上传图片，分析前五主色，映射 [中国色](https://zhongguose.com/) 色名，点击可展开经语料验证的古诗词句。

## 运行游戏

双击 [`serve.bat`](serve.bat)，浏览器打开 http://127.0.0.1:8766/index.html

图片仅在本地浏览器分析，不上传服务器。

## 构建诗句库（首次或更新语料后）

构建脚本较慢但只需运行一次。在 PowerShell 或 CMD 中：

```bat
cd 识色赋诗\scripts
build.bat
```

或手动：

```powershell
cd "C:\Users\zhangcz\Desktop\游戏\识色赋诗\scripts"
python -m pip install -r requirements.txt
python build_poetry.py
```

**说明：**

1. 首次运行会自动 `git clone` [chinese-poetry](https://github.com/chinese-poetry/chinese-poetry) 到 `vendor/chinese-poetry`（约 3–8 分钟）
2. 随后扫描语料并为 ~294 种颜色各写入最多 3 条诗句（约 5–15 分钟）
3. 产物：`data/poetry/*.json`、`data/poetry-index.json`、`scripts/build_report.txt`

若构建中断，重新运行 `python build_poetry.py` 即可（已有语料则跳过克隆）。

仅重建索引（不重新扫描）：

```powershell
python build_poetry.py --index-only
```

## 数据来源

| 数据 | 来源 |
|------|------|
| 中国传统色名/RGB | [zhongguose.com/colors.json](https://zhongguose.com/colors.json) |
| 古诗词曲赋语料 | [chinese-poetry/chinese-poetry](https://github.com/chinese-poetry/chinese-poetry) |

诗句匹配规则（构建脚本内实现）：

- P1：句中含完整色名
- P2：含核心色字 + 色相关意象词
- P3：仅含核心色字
- P4：仅 `scripts/color_imagery.yaml` 中人工定义的色意向导（凑不满 3 条时启用）

**搜不到不编造**；零覆盖色名见 `scripts/build_report.txt`。

## 项目结构

```
识色赋诗/
  index.html          主页面
  css/style.css       宋代水墨风样式
  js/extract.js       Canvas 取色
  js/match.js         RGB → 中国色名
  js/app.js           交互与诗句 lazy-load
  data/colors.json    中国色数据
  data/poetry/        构建产物（按 pinyin 分文件）
  scripts/build_poetry.py
  serve.bat / serve.ps1
```

## 许可说明

中国色数据来自 zhongguose.com，仅供个人学习参考；古诗词数据来自开源 chinese-poetry 项目。
