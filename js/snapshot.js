/**
 * 识色结果快照 — 左图右色并排排版，适配手机 / 微信分享
 */
const ColorSnapshot = (() => {
  const W = 720;
  const PAD = 28;
  const COL_GAP = 14;
  const LEFT_W = 258;
  const RIGHT_X = PAD + LEFT_W + COL_GAP;
  const RIGHT_W = W - PAD - RIGHT_X;
  const HEADER_H = 96;
  const FOOTER_H = 40;

  const C = {
    paper: '#F4F0E6',
    paperMid: '#EDE8DC',
    ink: '#2A2824',
    inkLight: '#6B6560',
    inkFaint: '#A8A098',
    border: 'rgba(42, 40, 36, 0.14)',
    accent: 'rgba(42, 40, 36, 0.06)',
  };

  const PALETTE_ZONE_H = 192;
  const PHOTO_PALETTE_GAP = 12;
  const PHOTO_MAX_H = 210;

  function hexToRgba(hex, alpha) {
    const h = (hex || '#888').replace('#', '');
    const full = h.length === 3 ? h.split('').map((c) => c + c).join('') : h;
    const n = parseInt(full, 16);
    const r = (n >> 16) & 255;
    const g = (n >> 8) & 255;
    const b = n & 255;
    return `rgba(${r},${g},${b},${alpha})`;
  }

  function nameFontSize(name) {
    const len = [...(name || '')].length;
    if (len <= 2) return 12;
    if (len === 3) return 11;
    return 10;
  }

  function vertexLabelStyle(angle) {
    const c = Math.cos(angle);
    const s = Math.sin(angle);
    if (s < -0.42) return { align: 'center', baseline: 'bottom', pad: 8 };
    if (s > 0.42) return { align: 'center', baseline: 'top', pad: 8 };
    if (c < 0) return { align: 'right', baseline: 'middle', pad: 6 };
    return { align: 'left', baseline: 'middle', pad: 6 };
  }

  /** 左下「五色盘」— 五顶点围合，水墨意 */
  function drawFiveColorPalette(ctx, colors, boxX, boxY, boxW, boxH) {
    const n = Math.min(colors.length, 5);
    if (n === 0) return;

    const cx = boxX + boxW / 2;
    const cy = boxY + boxH / 2 + 4;
    const R = Math.min(boxW, boxH) * 0.36;
    const nodeR = n >= 5 ? 14 : 16;

    ctx.save();

    drawRoundedRect(ctx, boxX + 2, boxY + 2, boxW - 4, boxH - 4, 6);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.52)';
    ctx.fill();
    ctx.strokeStyle = 'rgba(42, 40, 36, 0.2)';
    ctx.lineWidth = 1;
    ctx.stroke();

    ctx.fillStyle = C.inkFaint;
    ctx.font = '300 11px "Noto Serif SC", STSong, serif';
    ctx.textAlign = 'center';
    ctx.fillText('五 色 盘', cx, boxY + 16);

    const verts = [];
    for (let i = 0; i < n; i++) {
      const angle = -Math.PI / 2 + (i * 2 * Math.PI) / n;
      verts.push({
        x: cx + R * Math.cos(angle),
        y: cy + R * Math.sin(angle),
        angle,
        color: colors[i],
      });
    }

    ctx.setLineDash([2, 4]);
    ctx.beginPath();
    ctx.arc(cx, cy, R * 0.52, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(42, 40, 36, 0.08)';
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.setLineDash([]);

    if (n === 5) {
      for (let i = 0; i < 5; i++) {
        const v0 = verts[i];
        const v1 = verts[(i + 1) % 5];
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(v0.x, v0.y);
        ctx.lineTo(v1.x, v1.y);
        ctx.closePath();
        ctx.fillStyle = hexToRgba(colors[i].hex, 0.1);
        ctx.fill();
      }
    }

    ctx.beginPath();
    verts.forEach((v, i) => {
      if (i === 0) ctx.moveTo(v.x, v.y);
      else ctx.lineTo(v.x, v.y);
    });
    ctx.closePath();
    ctx.strokeStyle = 'rgba(42, 40, 36, 0.22)';
    ctx.lineWidth = 1;
    ctx.stroke();

    verts.forEach((v) => {
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(v.x, v.y);
      ctx.strokeStyle = 'rgba(42, 40, 36, 0.1)';
      ctx.lineWidth = 1;
      ctx.stroke();
    });

    ctx.beginPath();
    ctx.arc(cx, cy, 5, 0, Math.PI * 2);
    ctx.fillStyle = C.paper;
    ctx.fill();
    ctx.strokeStyle = 'rgba(42, 40, 36, 0.25)';
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(cx, cy, 1.8, 0, Math.PI * 2);
    ctx.fillStyle = C.inkFaint;
    ctx.fill();

    verts.forEach((v) => {
      const { color, x, y, angle } = v;
      const name = color.name || '';

      ctx.beginPath();
      ctx.arc(x + 0.6, y + 1.2, nodeR, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(42, 40, 36, 0.07)';
      ctx.fill();

      ctx.beginPath();
      ctx.arc(x, y, nodeR + 2.5, 0, Math.PI * 2);
      ctx.fillStyle = C.paper;
      ctx.fill();

      ctx.beginPath();
      ctx.arc(x, y, nodeR, 0, Math.PI * 2);
      ctx.fillStyle = color.hex;
      ctx.fill();
      ctx.strokeStyle = 'rgba(42, 40, 36, 0.28)';
      ctx.lineWidth = 1;
      ctx.stroke();

      const fs = nameFontSize(name);
      const labelR = R + nodeR + 10;
      let lx = cx + labelR * Math.cos(angle);
      let ly = cy + labelR * Math.sin(angle);
      const style = vertexLabelStyle(angle);

      ctx.font = `400 ${fs}px "Noto Serif SC", STSong, serif`;
      ctx.fillStyle = C.ink;
      ctx.textAlign = style.align;
      ctx.textBaseline = style.baseline;

      if (style.align === 'center' && style.baseline === 'bottom') ly -= style.pad;
      if (style.align === 'center' && style.baseline === 'top') ly += style.pad;
      if (style.align === 'right') lx -= style.pad;
      if (style.align === 'left') lx += style.pad;

      const chars = [...name];
      const tracking = fs >= 12 ? 2 : 1;
      if (chars.length <= 2) {
        chars.forEach((ch, ci) => {
          ctx.fillText(ch, lx + (ci - (chars.length - 1) / 2) * (fs + tracking), ly);
        });
      } else {
        ctx.fillText(name, lx, ly);
      }
    });

    ctx.restore();
  }

  function measureLeftColumn(sourceImg) {
    const photo = fitPhoto(sourceImg, LEFT_W, PHOTO_MAX_H);
    return photo.h + PHOTO_PALETTE_GAP + PALETTE_ZONE_H;
  }

  function drawLeftColumn(ctx, sourceImg, colors, bodyY) {
    const photo = fitPhoto(sourceImg, LEFT_W, PHOTO_MAX_H);
    const px = PAD;
    const py = bodyY;

    if (photo.w && photo.h) {
      ctx.save();
      drawRoundedRect(ctx, px, py, photo.w, photo.h, 4);
      ctx.clip();
      ctx.drawImage(sourceImg, px, py, photo.w, photo.h);
      ctx.restore();
      ctx.strokeStyle = C.border;
      ctx.lineWidth = 1;
      drawRoundedRect(ctx, px, py, photo.w, photo.h, 4);
      ctx.stroke();
    }

    const paletteY = py + photo.h + PHOTO_PALETTE_GAP;
    drawFiveColorPalette(ctx, colors, PAD, paletteY, LEFT_W, PALETTE_ZONE_H);
  }

  let overlayEl = null;
  let previewImgEl = null;
  let hintEl = null;
  let saveBtnEl = null;
  let closeBtnEl = null;
  let lastBlobUrl = null;
  let lastDataUrl = null;
  let lastBlob = null;

  function isWeChat() {
    return /MicroMessenger/i.test(navigator.userAgent || '');
  }

  async function ensureFonts() {
    if (!document.fonts) return;
    await Promise.all([
      document.fonts.load('400 30px "Noto Serif SC"'),
      document.fonts.load('400 18px "Noto Serif SC"'),
      document.fonts.load('300 16px "Noto Serif SC"'),
    ]).catch(() => {});
  }

  async function loadPoetry(pinyin, colorMeta) {
    if (typeof POETRY_LIBRARY !== 'undefined' && POETRY_LIBRARY[pinyin]) {
      return POETRY_LIBRARY[pinyin];
    }
    try {
      const res = await fetch(`data/poetry/${pinyin}.json`);
      if (res.ok) return res.json();
    } catch { /* fall through */ }
    return {
      color: colorMeta?.name || '',
      pinyin,
      entries: [],
      coverage: '0/5',
    };
  }

  function wrapText(ctx, text, maxWidth) {
    const chars = [...String(text || '')];
    const lines = [];
    let line = '';
    for (const ch of chars) {
      const next = line + ch;
      if (ctx.measureText(next).width > maxWidth && line) {
        lines.push(line);
        line = ch;
      } else {
        line = next;
      }
    }
    if (line) lines.push(line);
    return lines.length ? lines : [''];
  }

  function loadImage(src) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => resolve(img);
      img.onerror = reject;
      img.src = src;
    });
  }

  function poemMeta(entry) {
    const parts = [];
    if (entry.dynasty) parts.push(entry.dynasty);
    if (entry.author) parts.push(entry.author);
    if (entry.title) parts.push(`《${entry.title}》`);
    return parts.join(' · ') || '';
  }

  function typeScale(count) {
    if (count >= 5) {
      return { name: 17, gloss: 14, line: 15, meta: 13, swatch: 16, gap: 10, div: 12 };
    }
    return { name: 19, gloss: 15, line: 16, meta: 14, swatch: 18, gap: 12, div: 14 };
  }

  function measureColorBlock(ctx, poetry, gloss, textW, ts) {
    let h = ts.gap;
    ctx.font = `400 ${ts.name}px "Noto Serif SC", STSong, serif`;
    h += ts.name + 4;
    if (gloss) {
      ctx.font = `300 ${ts.gloss}px "Noto Serif SC", STSong, serif`;
      const glossLines = wrapText(ctx, gloss, textW);
      h += glossLines.length * (ts.gloss + 4);
    }
    h += 6;
    const entry = poetry?.entries?.[0];
    if (entry?.line) {
      ctx.font = `300 ${ts.line}px "Noto Serif SC", STSong, serif`;
      const poemLines = wrapText(ctx, entry.line, textW);
      h += poemLines.length * (ts.line + 5);
      const meta = poemMeta(entry);
      if (meta) {
        ctx.font = `300 ${ts.meta}px "Noto Serif SC", STSong, serif`;
        const metaLines = wrapText(ctx, meta, textW);
        h += metaLines.length * (ts.meta + 3) + 4;
      }
    } else {
      ctx.font = `300 ${ts.meta}px "Noto Serif SC", STSong, serif`;
      h += ts.meta + 6;
    }
    h += ts.div;
    return h;
  }

  function drawColorBlock(ctx, x, y, color, poetry, gloss, textW, ts) {
    const pct = color.ratio != null ? `${Math.round(color.ratio * 100)}%` : '';
    const startY = y;

    ctx.fillStyle = color.hex;
    ctx.fillRect(x, y + 2, ts.swatch, ts.swatch);
    ctx.strokeStyle = C.border;
    ctx.lineWidth = 1;
    ctx.strokeRect(x, y + 2, ts.swatch, ts.swatch);

    const tx = x + ts.swatch + 8;
    const innerW = textW - ts.swatch - 8;

    ctx.textAlign = 'left';
    ctx.fillStyle = C.ink;
    ctx.font = `400 ${ts.name}px "Noto Serif SC", STSong, serif`;
    ctx.fillText(color.name, tx, y + ts.name + 2);
    if (pct) {
      ctx.fillStyle = C.inkFaint;
      ctx.font = `300 ${ts.meta}px Consolas, monospace`;
      const pw = ctx.measureText(pct).width;
      ctx.fillText(pct, x + textW - pw, y + ts.name + 1);
    }
    y += ts.name + 6;

    if (gloss) {
      ctx.fillStyle = C.inkFaint;
      ctx.font = `300 ${ts.gloss}px "Noto Serif SC", STSong, serif`;
      wrapText(ctx, gloss, innerW).forEach((ln) => {
        ctx.fillText(ln, tx, y + ts.gloss);
        y += ts.gloss + 4;
      });
      y += 4;
    }

    const entry = poetry?.entries?.[0];
    if (entry?.line) {
      ctx.fillStyle = C.ink;
      ctx.font = `300 ${ts.line}px "Noto Serif SC", STSong, serif`;
      wrapText(ctx, entry.line, innerW).forEach((ln) => {
        ctx.fillText(ln, tx, y + ts.line);
        y += ts.line + 5;
      });
      const meta = poemMeta(entry);
      if (meta) {
        ctx.fillStyle = C.inkLight;
        ctx.font = `300 ${ts.meta}px "Noto Serif SC", STSong, serif`;
        wrapText(ctx, meta, innerW).forEach((ln) => {
          ctx.fillText(ln, tx, y + ts.meta);
          y += ts.meta + 3;
        });
      }
    } else {
      ctx.fillStyle = C.inkFaint;
      ctx.font = `300 ${ts.meta}px "Noto Serif SC", STSong, serif`;
      ctx.fillText('暂无诗句', tx, y + ts.meta);
      y += ts.meta + 6;
    }

    y += ts.div * 0.4;
    ctx.strokeStyle = C.border;
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x + textW, y);
    ctx.stroke();
    y += ts.div * 0.6;

    return y - startY;
  }

  function drawRoundedRect(ctx, x, y, w, h, r) {
    const rr = Math.min(r, w / 2, h / 2);
    ctx.beginPath();
    ctx.moveTo(x + rr, y);
    ctx.lineTo(x + w - rr, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + rr);
    ctx.lineTo(x + w, y + h - rr);
    ctx.quadraticCurveTo(x + w, y + h, x + w - rr, y + h);
    ctx.lineTo(x + rr, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - rr);
    ctx.lineTo(x, y + rr);
    ctx.quadraticCurveTo(x, y, x + rr, y);
    ctx.closePath();
  }

  function drawHeader(ctx) {
    ctx.fillStyle = C.accent;
    ctx.fillRect(0, 0, W, HEADER_H);

    ctx.fillStyle = C.ink;
    ctx.font = '400 30px "Noto Serif SC", STSong, serif';
    ctx.textAlign = 'center';
    ctx.fillText('色谱寻诗', W / 2, 38);

    ctx.fillStyle = C.inkLight;
    ctx.font = '300 17px "Noto Serif SC", STSong, serif';
    ctx.fillText('左图右色 · 五方成色', W / 2, 64);

    const dateStr = new Date().toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
    ctx.fillStyle = C.inkFaint;
    ctx.font = '300 15px "Noto Serif SC", STSong, serif';
    ctx.fillText(dateStr, W / 2, 84);
  }

  function fitPhoto(sourceImg, boxW, boxH) {
    if (!sourceImg?.naturalWidth) return { w: 0, h: 0 };
    const scale = Math.min(boxW / sourceImg.naturalWidth, boxH / sourceImg.naturalHeight);
    return {
      w: Math.round(sourceImg.naturalWidth * scale),
      h: Math.round(sourceImg.naturalHeight * scale),
    };
  }

  async function buildCanvas(sourceImg, colors) {
    await ensureFonts();

    const poems = await Promise.all(colors.map((c) => loadPoetry(c.pinyin, c)));
    const ts = typeScale(colors.length);
    const textW = RIGHT_W;
    const measureCtx = document.createElement('canvas').getContext('2d');

    let rightH = ts.gap;
    colors.forEach((c, i) => {
      rightH += measureColorBlock(
        measureCtx,
        poems[i],
        ColorGlosses?.get?.(c.pinyin),
        textW,
        ts,
      );
    });

    const leftH = measureLeftColumn(sourceImg);
    const bodyH = Math.max(rightH, leftH);
    const totalH = HEADER_H + bodyH + FOOTER_H + PAD;

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const canvas = document.createElement('canvas');
    canvas.width = W * dpr;
    canvas.height = totalH * dpr;
    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);

    ctx.fillStyle = C.paper;
    ctx.fillRect(0, 0, W, totalH);
    drawHeader(ctx);

    const bodyY = HEADER_H + PAD * 0.35;

    drawLeftColumn(ctx, sourceImg, colors, bodyY);

    ctx.strokeStyle = C.border;
    ctx.beginPath();
    ctx.moveTo(RIGHT_X - COL_GAP / 2, bodyY);
    ctx.lineTo(RIGHT_X - COL_GAP / 2, bodyY + bodyH);
    ctx.stroke();

    let cy = bodyY;
    colors.forEach((c, i) => {
      drawColorBlock(
        ctx,
        RIGHT_X,
        cy,
        c,
        poems[i],
        ColorGlosses?.get?.(c.pinyin),
        textW,
        ts,
      );
      cy += measureColorBlock(
        ctx,
        poems[i],
        ColorGlosses?.get?.(c.pinyin),
        textW,
        ts,
      );
    });

    ctx.textAlign = 'center';
    ctx.fillStyle = C.inkFaint;
    ctx.font = '300 15px "Noto Serif SC", STSong, serif';
    ctx.fillText('色名参考中国色 · 每色示诗一例', W / 2, totalH - 16);

    return canvas;
  }

  function revokeLastUrl() {
    if (lastBlobUrl) {
      URL.revokeObjectURL(lastBlobUrl);
      lastBlobUrl = null;
    }
    lastDataUrl = null;
    lastBlob = null;
  }

  function updateSaveUi() {
    const wechat = isWeChat();
    overlayEl?.classList.toggle('snapshot-overlay--wechat', wechat);
    if (hintEl) {
      hintEl.textContent = wechat
        ? '微信内请长按下方图片，选择「保存图片」'
        : '手机上可长按图片保存到相册';
    }
    if (saveBtnEl) {
      saveBtnEl.textContent = wechat ? '查看保存提示' : '保存图片';
    }
  }

  function bindDom() {
    overlayEl = document.getElementById('snapshot-overlay');
    previewImgEl = document.getElementById('snapshot-preview');
    hintEl = document.getElementById('snapshot-hint');
    saveBtnEl = document.getElementById('snapshot-save');
    closeBtnEl = document.getElementById('snapshot-close');

    closeBtnEl?.addEventListener('click', hide);
    overlayEl?.querySelector('.snapshot-backdrop')?.addEventListener('click', hide);

    saveBtnEl?.addEventListener('click', () => {
      if (isWeChat()) {
        previewImgEl?.scrollIntoView({ behavior: 'smooth', block: 'center' });
        if (hintEl) {
          hintEl.classList.add('snapshot-hint-flash');
          setTimeout(() => hintEl.classList.remove('snapshot-hint-flash'), 1600);
        }
        return;
      }
      if (!lastBlob && !lastDataUrl) return;
      const a = document.createElement('a');
      const stamp = new Date().toISOString().slice(0, 10);
      a.download = `色谱寻诗-${stamp}.png`;
      a.href = lastDataUrl || lastBlobUrl;
      document.body.appendChild(a);
      a.click();
      a.remove();
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && overlayEl && !overlayEl.hidden) hide();
    });

    updateSaveUi();
  }

  function showPreview(blob, dataUrl) {
    revokeLastUrl();
    lastBlob = blob;
    lastDataUrl = dataUrl;

    const wechat = isWeChat();
    if (wechat && dataUrl) {
      previewImgEl.src = dataUrl;
    } else {
      lastBlobUrl = URL.createObjectURL(blob);
      previewImgEl.src = lastBlobUrl;
    }

    previewImgEl.hidden = false;
    overlayEl.hidden = false;
    overlayEl.setAttribute('aria-hidden', 'false');
    document.body.classList.add('snapshot-open');
    updateSaveUi();
    requestAnimationFrame(() => overlayEl.classList.add('snapshot-visible'));
  }

  function hide() {
    overlayEl?.classList.remove('snapshot-visible');
    document.body.classList.remove('snapshot-open');
    setTimeout(() => {
      if (overlayEl) {
        overlayEl.hidden = true;
        overlayEl.setAttribute('aria-hidden', 'true');
      }
      if (previewImgEl) {
        previewImgEl.hidden = true;
        previewImgEl.removeAttribute('src');
      }
    }, 280);
  }

  async function capture(sourceImgEl, colors, onProgress) {
    if (!sourceImgEl?.src || !colors?.length) {
      throw new Error('请先上传图片并完成识色');
    }

    onProgress?.('备句中…');
    const img = await loadImage(sourceImgEl.src);

    onProgress?.('排版快照…');
    const canvas = await buildCanvas(img, colors);

    onProgress?.('生成图片…');
    const dataUrl = canvas.toDataURL('image/png');
    const blob = await new Promise((resolve, reject) => {
      canvas.toBlob((b) => (b ? resolve(b) : reject(new Error('生成失败'))), 'image/png');
    });

    return { blob, dataUrl };
  }

  async function open(sourceImgEl, colors, onProgress) {
    const { blob, dataUrl } = await capture(sourceImgEl, colors, onProgress);
    showPreview(blob, dataUrl);
    return blob;
  }

  return { bindDom, open, capture, hide, isWeChat };
})();
