/**
 * 识色快照 — 左图 / 五色横条 / 右栏题跋式诗句
 */
const ColorSnapshot = (() => {
  const W = 720;
  const PAD = 26;
  const COL_GAP = 20;
  const LEFT_W = 272;
  const RIGHT_X = PAD + LEFT_W + COL_GAP;
  const RIGHT_W = W - PAD - RIGHT_X;
  const HEADER_H = 54;
  const BODY_PAD_BOTTOM = 22;

  const RIBBON_H = 58;
  const RIBBON_GAP = 10;
  const PHOTO_GAP = 12;
  const PHOTO_MAX_H = 196;

  const C = {
    paper: '#F4F0E6',
    ink: '#2A2824',
    inkLight: '#5A544E',
    inkFaint: '#9E968E',
    border: 'rgba(42, 40, 36, 0.1)',
  };

  let overlayEl = null;
  let previewImgEl = null;
  let hintEl = null;
  let saveBtnEl = null;
  let closeBtnEl = null;
  let lastBlobUrl = null;
  let lastDataUrl = null;
  let lastBlob = null;

  function hexToRgba(hex, alpha) {
    const h = (hex || '#888').replace('#', '');
    const full = h.length === 3 ? h.split('').map((c) => c + c).join('') : h;
    const n = parseInt(full, 16);
    return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${alpha})`;
  }

  function hexLuminance(hex) {
    const h = (hex || '#888').replace('#', '');
    const full = h.length === 3 ? h.split('').map((c) => c + c).join('') : h;
    const r = parseInt(full.slice(0, 2), 16) / 255;
    const g = parseInt(full.slice(2, 4), 16) / 255;
    const b = parseInt(full.slice(4, 6), 16) / 255;
    const lin = (v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4);
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
  }

  function contrastOnColor(hex) {
    return hexLuminance(hex) > 0.42 ? C.ink : '#F7F4EE';
  }

  function isWeChat() {
    return /MicroMessenger/i.test(navigator.userAgent || '');
  }

  async function ensureFonts() {
    if (!document.fonts) return;
    await Promise.all([
      document.fonts.load('400 34px "Noto Serif SC"'),
      document.fonts.load('400 21px "Noto Serif SC"'),
      document.fonts.load('300 14px "Noto Serif SC"'),
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
    return { color: colorMeta?.name || '', pinyin, entries: [], coverage: '0/5' };
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

  function poemLine(poetry) {
    return poetry?.entries?.[0]?.line || '';
  }

  function typeScale(count) {
    if (count >= 5) {
      return { name: 20, line: 14, pad: 18, gap: 20, lead: 16, lineLead: 10, seal: 26 };
    }
    return { name: 21, line: 15, pad: 20, gap: 22, lead: 18, lineLead: 11, seal: 28 };
  }

  function measureColorBlock(ctx, poetry, innerW, ts) {
    let h = ts.pad + ts.seal + ts.lead;
    const line = poemLine(poetry);
    if (line) {
      ctx.font = `300 ${ts.line}px "Noto Serif SC", STSong, serif`;
      h += wrapText(ctx, line, innerW - ts.seal - 14).length * (ts.line + ts.lineLead);
    }
    return h + ts.gap;
  }

  /** 右栏：题跋式 — 色印 + 色名 + 诗句，层次分明 */
  function drawColorBlock(ctx, x, y, color, poetry, colW, ts, isFirst) {
    const innerW = colW - ts.pad * 2;
    const blockH = measureColorBlock(ctx, poetry, innerW, ts) - ts.gap;

    if (!isFirst) {
      ctx.strokeStyle = C.border;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(x + ts.pad, y + 6);
      ctx.lineTo(x + colW - ts.pad, y + 6);
      ctx.stroke();
    }

    const baseY = y + (isFirst ? ts.pad * 0.4 : ts.pad + 6);
    const sealX = x + ts.pad;
    const sealY = baseY;
    const textX = sealX + ts.seal + 12;

    drawRoundedRect(ctx, sealX, sealY, ts.seal, ts.seal, 3);
    ctx.fillStyle = color.hex;
    ctx.fill();
    ctx.strokeStyle = 'rgba(42, 40, 36, 0.18)';
    ctx.lineWidth = 1;
    ctx.stroke();

    const nameY = sealY + ts.seal * 0.72;
    ctx.textAlign = 'left';
    ctx.textBaseline = 'alphabetic';
    ctx.fillStyle = C.ink;
    ctx.font = `400 ${ts.name}px "Noto Serif SC", STSong, serif`;
    ctx.fillText(color.name, textX, nameY);

    let ty = nameY + ts.lead + ts.line;
    const line = poemLine(poetry);
    if (line) {
      ctx.fillStyle = C.inkFaint;
      ctx.font = `300 ${ts.line}px "Noto Serif SC", STSong, serif`;
      wrapText(ctx, line, innerW - ts.seal - 14).forEach((ln) => {
        ctx.fillText(ln, textX, ty);
        ty += ts.line + ts.lineLead;
      });
    }

    return blockH + ts.gap;
  }

  /** 照片下五色横条 — 大色面题签，无图表感 */
  function drawColorRibbon(ctx, colors, boxX, boxY, boxW, boxH) {
    const n = Math.min(colors.length, 5);
    if (n < 1) return;

    const segW = boxW / n;
    const r = 4;

    ctx.save();
    drawRoundedRect(ctx, boxX, boxY, boxW, boxH, r);
    ctx.clip();

    for (let i = 0; i < n; i++) {
      const sx = boxX + segW * i;
      ctx.fillStyle = colors[i].hex;
      ctx.fillRect(sx, boxY, segW + (i === n - 1 ? 1 : 0), boxH);

      if (i > 0) {
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.35)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(sx + 0.5, boxY + 6);
        ctx.lineTo(sx + 0.5, boxY + boxH - 6);
        ctx.stroke();
      }

      const label = colors[i].name;
      const cx = sx + segW / 2;
      const cy = boxY + boxH / 2;
      const fg = contrastOnColor(colors[i].hex);

      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = fg;
      ctx.font = '400 13px "Noto Serif SC", STSong, serif';

      if (label.length <= 2) {
        ctx.fillText(label, cx, cy);
      } else {
        const chars = [...label];
        const step = Math.min(15, (boxH - 10) / chars.length);
        const totalH = step * (chars.length - 1);
        let ly = cy - totalH / 2;
        chars.forEach((ch) => {
          ctx.fillText(ch, cx, ly);
          ly += step;
        });
      }
    }

    ctx.restore();

    drawRoundedRect(ctx, boxX, boxY, boxW, boxH, r);
    ctx.strokeStyle = 'rgba(42, 40, 36, 0.14)';
    ctx.lineWidth = 1;
    ctx.stroke();
  }

  function fitPhoto(sourceImg, boxW, boxH) {
    if (!sourceImg?.naturalWidth) return { w: 0, h: 0 };
    const scale = Math.min(boxW / sourceImg.naturalWidth, boxH / sourceImg.naturalHeight);
    return {
      w: Math.round(sourceImg.naturalWidth * scale),
      h: Math.round(sourceImg.naturalHeight * scale),
    };
  }

  function measureLeftColumn(sourceImg) {
    const photo = fitPhoto(sourceImg, LEFT_W - 16, PHOTO_MAX_H);
    return photo.h + PHOTO_GAP + RIBBON_H + RIBBON_GAP + 12;
  }

  function drawLeftColumn(ctx, sourceImg, colors, bodyY) {
    const panelX = PAD;
    const panelW = LEFT_W;
    const innerX = panelX + 8;
    const innerW = panelW - 16;
    const photo = fitPhoto(sourceImg, innerW, PHOTO_MAX_H);
    const photoTop = bodyY + 8;
    const ribbonY = photoTop + Math.max(photo.h, 0) + PHOTO_GAP;
    const panelH = ribbonY - bodyY + RIBBON_H + RIBBON_GAP + 4;

    drawRoundedRect(ctx, panelX, bodyY, panelW, panelH, 8);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.28)';
    ctx.fill();
    ctx.strokeStyle = C.border;
    ctx.stroke();

    if (photo.w && photo.h) {
      const px = innerX;
      const py = photoTop;
      ctx.save();
      drawRoundedRect(ctx, px, py, photo.w, photo.h, 3);
      ctx.clip();
      ctx.drawImage(sourceImg, px, py, photo.w, photo.h);
      ctx.restore();
      ctx.strokeStyle = 'rgba(42, 40, 36, 0.12)';
      drawRoundedRect(ctx, px, py, photo.w, photo.h, 3);
      ctx.stroke();
    }

    drawColorRibbon(ctx, colors, innerX, ribbonY, innerW, RIBBON_H);
    return panelH;
  }

  function drawHeader(ctx) {
    ctx.fillStyle = C.ink;
    ctx.font = '400 34px "Noto Serif SC", STSong, serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'alphabetic';
    ctx.fillText('色谱寻诗', W / 2, 38);
    ctx.strokeStyle = C.border;
    ctx.beginPath();
    ctx.moveTo(W * 0.22, HEADER_H - 2);
    ctx.lineTo(W * 0.78, HEADER_H - 2);
    ctx.stroke();
  }

  function drawColumnDivider(ctx, bodyY, bodyH) {
    const x = RIGHT_X - COL_GAP / 2;
    ctx.strokeStyle = 'rgba(42, 40, 36, 0.06)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(x, bodyY + 4);
    ctx.lineTo(x, bodyY + bodyH - 4);
    ctx.stroke();
  }

  async function buildCanvas(sourceImg, colors) {
    await ensureFonts();

    const poems = await Promise.all(colors.map((c) => loadPoetry(c.pinyin, c)));
    const ts = typeScale(colors.length);
    const measureCtx = document.createElement('canvas').getContext('2d');
    const innerW = RIGHT_W - ts.pad * 2;

    let rightH = 0;
    colors.forEach((_, i) => {
      rightH += measureColorBlock(measureCtx, poems[i], innerW, ts);
    });

    const bodyH = Math.max(rightH, measureLeftColumn(sourceImg));
    const totalH = HEADER_H + bodyH + BODY_PAD_BOTTOM;

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const canvas = document.createElement('canvas');
    canvas.width = W * dpr;
    canvas.height = totalH * dpr;
    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);

    ctx.fillStyle = C.paper;
    ctx.fillRect(0, 0, W, totalH);
    drawHeader(ctx);

    const bodyY = HEADER_H + 8;
    drawLeftColumn(ctx, sourceImg, colors, bodyY);
    drawColumnDivider(ctx, bodyY, bodyH);

    let cy = bodyY;
    colors.forEach((c, i) => {
      cy += drawColorBlock(ctx, RIGHT_X, cy, c, poems[i], RIGHT_W, ts, i === 0);
    });

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
    if (hintEl) hintEl.textContent = wechat ? '长按图片保存' : '长按图片可保存';
    if (saveBtnEl) saveBtnEl.textContent = wechat ? '保存提示' : '保存图片';
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
        hintEl?.classList.add('snapshot-hint-flash');
        setTimeout(() => hintEl?.classList.remove('snapshot-hint-flash'), 1600);
        return;
      }
      if (!lastBlob && !lastDataUrl) return;
      const a = document.createElement('a');
      a.download = `色谱寻诗-${new Date().toISOString().slice(0, 10)}.png`;
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
    if (isWeChat() && dataUrl) {
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
