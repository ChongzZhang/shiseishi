/**
 * 识色快照 — 左图 / 五色盘 / 右栏题跋式诗句
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

  const PALETTE_GRAPH_H = 112;
  const PALETTE_LEGEND_H = 86;
  const PALETTE_GAP = 6;
  const PALETTE_H = PALETTE_GRAPH_H + PALETTE_LEGEND_H + PALETTE_GAP;
  const PHOTO_GAP = 12;
  const PHOTO_MAX_H = 176;

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

  function isWeChat() {
    return /MicroMessenger/i.test(navigator.userAgent || '');
  }

  async function ensureFonts() {
    if (!document.fonts) return;
    await Promise.all([
      document.fonts.load('400 32px "Noto Serif SC"'),
      document.fonts.load('400 17px "Noto Serif SC"'),
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
      return { name: 17, line: 15, pad: 16, gap: 14, lead: 9 };
    }
    return { name: 18, line: 16, pad: 18, gap: 16, lead: 10 };
  }

  function measureColorBlock(ctx, poetry, innerW, ts) {
    let h = ts.pad + ts.name + ts.lead;
    const line = poemLine(poetry);
    if (line) {
      ctx.font = `300 ${ts.line}px "Noto Serif SC", STSong, serif`;
      h += wrapText(ctx, line, innerW).length * (ts.line + 8);
    }
    return h + ts.gap;
  }

  /** 右栏：题跋式，无框，留白与细线 */
  function drawColorBlock(ctx, x, y, color, poetry, colW, ts, isFirst) {
    const innerW = colW - ts.pad * 2;
    const blockH = measureColorBlock(ctx, poetry, innerW, ts) - ts.gap;

    if (!isFirst) {
      ctx.strokeStyle = C.border;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(x + ts.pad, y);
      ctx.lineTo(x + colW - ts.pad, y);
      ctx.stroke();
    }

    const baseY = y + (isFirst ? ts.pad * 0.5 : ts.pad);
    const nameY = baseY + ts.name;

    ctx.fillStyle = color.hex;
    ctx.fillRect(x + ts.pad, baseY + 3, 3, ts.name - 6);

    ctx.textAlign = 'left';
    ctx.fillStyle = C.ink;
    ctx.font = `400 ${ts.name}px "Noto Serif SC", STSong, serif`;
    ctx.fillText(color.name, x + ts.pad + 11, nameY);

    let ty = nameY + ts.lead + ts.line;
    const line = poemLine(poetry);
    if (line) {
      ctx.fillStyle = C.inkLight;
      ctx.font = `300 ${ts.line}px "Noto Serif SC", STSong, serif`;
      wrapText(ctx, line, innerW - 4).forEach((ln) => {
        ctx.fillText(ln, x + ts.pad, ty);
        ty += ts.line + 8;
      });
    }

    return blockH + ts.gap;
  }

  /** 五色盘图形区：仅色点与五边形，不写色名 */
  function drawPaletteGraph(ctx, colors, boxX, boxY, boxW, boxH) {
    const n = Math.min(colors.length, 5);
    if (n < 1) return;

    const cx = boxX + boxW / 2;
    const cy = boxY + boxH / 2;
    const R = Math.min(boxW, boxH) * 0.34;
    const nodeR = 11;

    const verts = [];
    for (let i = 0; i < n; i++) {
      const angle = -Math.PI / 2 + (i * 2 * Math.PI) / n;
      verts.push({
        x: cx + R * Math.cos(angle),
        y: cy + R * Math.sin(angle),
        color: colors[i],
      });
    }

    if (n === 5) {
      for (let i = 0; i < 5; i++) {
        const v0 = verts[i];
        const v1 = verts[(i + 1) % 5];
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(v0.x, v0.y);
        ctx.lineTo(v1.x, v1.y);
        ctx.closePath();
        ctx.fillStyle = hexToRgba(colors[i].hex, 0.09);
        ctx.fill();
      }
    }

    ctx.beginPath();
    verts.forEach((v, i) => {
      if (i === 0) ctx.moveTo(v.x, v.y);
      else ctx.lineTo(v.x, v.y);
    });
    ctx.closePath();
    ctx.strokeStyle = 'rgba(42, 40, 36, 0.2)';
    ctx.lineWidth = 1;
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(cx, cy, 3, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(42, 40, 36, 0.15)';
    ctx.fill();

    verts.forEach((v) => {
      ctx.beginPath();
      ctx.arc(v.x, v.y, nodeR + 2, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(255,255,255,0.9)';
      ctx.fill();
      ctx.beginPath();
      ctx.arc(v.x, v.y, nodeR, 0, Math.PI * 2);
      ctx.fillStyle = v.color.hex;
      ctx.fill();
      ctx.strokeStyle = 'rgba(42, 40, 36, 0.22)';
      ctx.lineWidth = 1;
      ctx.stroke();
    });
  }

  /** 色名图例：竖排对齐，与图形分离，绝不叠字 */
  function drawPaletteLegend(ctx, colors, boxX, boxY, boxW, boxH) {
    const n = Math.min(colors.length, 5);
    if (n < 1) return;

    const rowH = boxH / n;
    const dotR = 4.5;

    for (let i = 0; i < n; i++) {
      const rowCy = boxY + rowH * i + rowH / 2;
      const dotX = boxX + 16;

      ctx.beginPath();
      ctx.arc(dotX, rowCy, dotR, 0, Math.PI * 2);
      ctx.fillStyle = colors[i].hex;
      ctx.fill();
      ctx.strokeStyle = 'rgba(42, 40, 36, 0.15)';
      ctx.stroke();

      ctx.textAlign = 'left';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = C.inkLight;
      ctx.font = '400 12px "Noto Serif SC", STSong, serif';
      ctx.fillText(colors[i].name, dotX + 12, rowCy);
    }
  }

  function drawPalettePanel(ctx, colors, boxX, boxY, boxW) {
    drawRoundedRect(ctx, boxX, boxY, boxW, PALETTE_H, 6);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.55)';
    ctx.fill();
    ctx.strokeStyle = C.border;
    ctx.lineWidth = 1;
    ctx.stroke();

    const innerX = boxX + 4;
    const innerW = boxW - 8;
    const graphY = boxY + 4;

    drawPaletteGraph(ctx, colors, innerX, graphY, innerW, PALETTE_GRAPH_H - 4);

    const divY = graphY + PALETTE_GRAPH_H - 2;
    ctx.strokeStyle = C.border;
    ctx.beginPath();
    ctx.moveTo(boxX + 12, divY);
    ctx.lineTo(boxX + boxW - 12, divY);
    ctx.stroke();

    drawPaletteLegend(
      ctx,
      colors,
      innerX,
      divY + 4,
      innerW,
      PALETTE_LEGEND_H - 6,
    );
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
    return photo.h + PHOTO_GAP + PALETTE_H + 12;
  }

  function drawLeftColumn(ctx, sourceImg, colors, bodyY) {
    const panelX = PAD;
    const panelW = LEFT_W;
    const photo = fitPhoto(sourceImg, panelW - 16, PHOTO_MAX_H);
    const photoTop = bodyY + 8;
    const paletteY = photoTop + Math.max(photo.h, 0) + PHOTO_GAP;
    const panelH = paletteY - bodyY + PALETTE_H + 8;

    drawRoundedRect(ctx, panelX, bodyY, panelW, panelH, 8);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.28)';
    ctx.fill();
    ctx.strokeStyle = C.border;
    ctx.stroke();

    if (photo.w && photo.h) {
      const px = panelX + 8;
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

    drawPalettePanel(ctx, colors, panelX + 8, paletteY, panelW - 16);
    return panelH;
  }

  function drawHeader(ctx) {
    ctx.fillStyle = C.ink;
    ctx.font = '400 32px "Noto Serif SC", STSong, serif';
    ctx.textAlign = 'center';
    ctx.fillText('色谱寻诗', W / 2, 36);
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
