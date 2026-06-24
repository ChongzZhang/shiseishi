# 色谱寻诗 — 服务器部署说明

上传图片，识别图中主色并匹配中国传统色名，展开对应古典诗词。**纯静态站点**，无需数据库与后端 API。

---

## 一、包内内容

本压缩包为**可直接上线**的静态文件，已包含：

| 路径 | 说明 |
|------|------|
| `index.html` | 游戏主页（识色赋诗） |
| `achievements.html` | 成就书签（识色集签、下载） |
| `daily.html` | 每日一色挑战（意象诗句提示、拍照打卡） |
| `browse.html` | 诗词库 / RGB 索引浏览 |
| `css/` | 样式 |
| `js/` | 前端逻辑与内嵌诗词数据（`poetry-bundle.js` 等） |
| `assets/color-bookmarks/new/` | 成就书签图片（25 种） |
| `assets/color-bookmarks/daily-challenges.json` | 每日挑战意象诗句数据 |
| `data/poetry-preview.txt` | 诗句预览文本 |
| `404.html` | 404 页 |
| `_headers` | Cloudflare Pages 安全头（其他服务器可忽略） |

**不包含**开发脚本、语料源码、筛诗工具等内部文件。

---

## 二、部署要求

- 任意支持静态文件的 Web 服务器（Nginx、Apache、Caddy、IIS、对象存储静态托管等）
- **不需要** PHP / Node / Python 常驻进程（仅本地测试可用 Python 临时起一个静态服务）
- 建议启用 **HTTPS**
- 用户上传的图片**仅在浏览器本地分析**，不会传到服务器

---

## 三、部署步骤（通用）

1. 解压本压缩包
2. 将解压后的**全部文件**上传到网站根目录（或子目录）
3. 确保 `index.html` 可通过 URL 访问
4. 访问 `https://你的域名/` 或 `https://你的域名/index.html`

若部署在子目录（例如 `/shiseishi/`），需保证服务器能正确返回该目录下的静态资源；部分环境可能需要配置 `base` 路径（当前版本按根路径 `/` 编写）。

---

## 四、Nginx 示例

```nginx
server {
    listen 80;
    server_name example.com;
    root /var/www/shiseishi;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?)$ {
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
}
```

将 `root` 改为实际上传目录，重载 Nginx 后生效。

---

## 五、Apache 示例

在站点根目录放置 `.htaccess`（若允许）：

```apache
DirectoryIndex index.html
ErrorDocument 404 /404.html

<IfModule mod_headers.c>
  Header set X-Content-Type-Options "nosniff"
  Header set X-Frame-Options "DENY"
</IfModule>
```

---

## 六、本地快速验证

解压后在目录内执行：

**Python 3：**

```bash
python -m http.server 8080
```

浏览器打开：http://127.0.0.1:8080/index.html

**Node（若已安装 npx）：**

```bash
npx serve -l 8080
```

---

## 七、Cloudflare Pages / 对象存储

- **Cloudflare Pages**：上传整个文件夹，构建命令留空，输出目录即根目录；`_headers` 会自动生效
- **阿里云 OSS / 腾讯云 COS**：开启静态网站托管，默认首页设为 `index.html`，404 页设为 `404.html`

---

## 八、功能说明

| 页面 | 地址 | 功能 |
|------|------|------|
| 识色赋诗 | `/index.html` | 上传图片 → 前五主色 → 中国色名 → 诗词 |
| 成就书签 | `/achievements.html` | 识色解锁书签、浏览与下载 |
| 每日一色 | `/daily.html` | 每日意象诗句 → 拍照寻色 → 打卡 |
| 数据浏览 | `/browse.html` | 诗词库、RGB 索引（支持色名/RGB/HEX 检索） |

主页说明：古诗中的颜色常寓意境与象征，所配之色取意相近，而非精确色值。

---

## 九、数据与版权

- 中国传统色名参考 [中国色](https://zhongguose.com/)
- 古诗词来自开源 [chinese-poetry](https://github.com/chinese-poetry/chinese-poetry) 等公开语料
- 仅供学习、展示与个人项目使用；商用请自行确认数据来源授权

---

## 十、常见问题

**Q：打开页面空白或诗词不显示？**  
A：请用 HTTP(S) 访问，不要直接双击 HTML（`file://` 可能导致脚本受限）。必须通过 Web 服务器访问。

**Q：需要改色库或诗词？**  
A：本包为发布快照。内容更新需联系项目维护者重新打包；开发版在完整源码仓库中通过 `scripts/regen_frontend.py` 生成。

**Q：服务器会被用户上传图片吗？**  
A：不会。取色与匹配均在访客浏览器完成，服务器只提供静态 HTML/JS/CSS。

---

## 联系

如有部署问题，请联系项目维护者。
