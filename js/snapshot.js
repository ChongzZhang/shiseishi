/**
 * 识色快照 — 左图 + 五色盘 / 右栏色名与诗句（极简排版）
 */
const ColorSnapshot = (() => {
  const W = 720;
  const PAD = 24;
  const COL_GAP = 18;
  const LEFT_W = 268;
  const RIGHT_X = PAD + LEFT_W + COL_GAP;
  const RIGHT_W = W - PAD - RIGHT_X;
  const HEADER_H = 58;
  const BODY_PAD_BOTTOM = 20;

  const C = {
    paper: '#F4F0E6',
    ink: '#2A2824',
    inkLight: '#5C5650',
    inkFaint: '#A8A098',
    border: 'rgba(42, 40, 36, 0.12)',
  };

  const PALETTE_H = 200;
  const PHOTO_GAP = 10;
  const PHOTO_MAX_H = 188;

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
      document.fonts.load('400 34px "Noto Serif SC"'),
      document.fonts.load('400 19px "Noto Serif SC"'),
      document.fonts.load('300 17px "Noto Serif SC"'),
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

  function typeScale(count) {
    if (count >= 5) {
      return { name: 18, line: 16, swatch: 20, pad: 12, gap: 10 };
    }
    return { name: 20, line: 17, swatch: 22, pad: 14, gap: 12 };
  }

  function poemLine(poetry) {
    return poetry?.entries?.[0]?.line || '';
  }

  function measureColorBlock(ctx, poetry, innerW, ts) {
    let h = ts.pad * 2 + ts.name;
    const line = poemLine(poetry);
    if (line) {
      ctx.font = `300 ${ts.line}px "Noto Serif SC", STSong, serif`;
      h += wrapText(ctx, line, innerW).length * (ts.line + 7) + 4;
    } else {
      h += ts.line + 4;
    }
    return h + ts.gap;
  }

  function drawColorBlock(ctx, x, y, color, poetry, cardW, ts) {
    const innerW = cardW - ts.pad * 2 - ts.swatch - 12;
    const blockH = measureColorBlock(ctx, poetry, innerW, ts) - ts.gap;

    drawRoundedRect(ctx, x, y, cardW, blockH, 6);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.62)';
    ctx.fill();
    ctx.strokeStyle = 'rgba(42, 40, 36, 0.1)';
    ctx.lineWidth = 1;
    ctx.stroke();

    ctx.fillStyle = color.hex;
    drawRoundedRect(ctx, x + 1, y + 10, 4, blockH - 20, 2);
    ctx.fill();

    const ix = x + ts.pad + 2;
    const rowY = y + ts.pad;
    const swatchCy = rowY + ts.swatch / 2 + 2;

    ctx.beginPath();
    ctx.arc(ix + ts.swatch / 2, swatchCy, ts.swatch / 2, 0, Math.PI * 2);
    ctx.fillStyle = color.hex;
    ctx.fill();
    ctx.strokeStyle = 'rgba(42, 40, 36, 0.18)';
    ctx.lineWidth = 1;
    ctx.stroke();

    const tx = ix + ts.swatch + 10;
    ctx.textAlign = 'left';
    ctx.fillStyle = C.ink;
    ctx.font = `400 ${ts.name}px "Noto Serif SC", STSong, serif`;
    ctx.fillText(color.name, tx, rowY + ts.name);

    let ty = rowY + ts.name + 12;
    const line = poemLine(poetry);
    if (line) {
      ctx.fillStyle = C.inkLight;
      ctx.font = `300 ${ts.line}px "Noto Serif SC", STSong, serif`;
      wrapText(ctx, line, innerW).forEach((ln) => {
        ctx.fillText(ln, tx, ty);
        ty += ts.line + 7;
      });
    }

    return blockH + ts.gap;
  }

  function vertexLabelStyle(angle) {
    const c = Math.cos(angle);
    const s = Math.sin(angle);
    if (s < -0.4) return { align: 'center', baseline: 'bottom', pad: 7 };
    if (s > 0.4) return { align: 'center', baseline: 'top', pad: 7 };
    if (c < 0) return { align: 'right', baseline: 'middle', pad: 5 };
    return { align: 'left', baseline: 'middle', pad: 5 };
  }

  function labelFontSize(name) {
    const n = [...(name || '')].length;
    if (n <= 2) return 13;
    if (n === 3) return 12;
    return 11;
  }

  /** 五色盘 — 无标题字，图形为主 */
  function drawFiveColorPalette(ctx, colors, boxX, boxY, boxW, boxH) {
    const n = Math.min(colors.length, 5);
    if (n < 1) return;

    const cx = boxX + boxW / 2;
    const cy = boxY + boxH / 2 + 2;
    const R = Math.min(boxW, boxH) * 0.38;
    const nodeR = 16;

    ctx.save();

    drawRoundedRect(ctx, boxX, boxY, boxW, boxH, 8);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
    ctx.fill();
    ctx.strokeStyle = 'rgba(42, 40, 36, 0.16)';
    ctx.lineWidth = 1.2;
    ctx.stroke();

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

    if (n === 5) {
      for (let i = 0; i < 5; i++) {
        const v0 = verts[i];
        const v1 = verts[(i + 1) % 5];
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(v0.x, v0.y);
        ctx.lineTo(v1.x, v1.y);
        ctx.closePath();
        ctx.fillStyle = hexToRgba(colors[i].hex, 0.14);
        ctx.fill();
      }
    }

    ctx.beginPath();
    verts.forEach((v, i) => {
      if (i === 0) ctx.moveTo(v.x, v.y);
      else ctx.lineTo(v.x, v.y);
    });
    ctx.closePath();
    ctx.strokeStyle = 'rgba(42, 40, 36, 0.28)';
    ctx.lineWidth = 1.2;
    ctx.stroke();

    verts.forEach((v) => {
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(v.x, v.y);
      ctx.strokeStyle = 'rgba(42, 40, 36, 0.12)';
      ctx.lineWidth = 1;
      ctx.stroke();
    });

    ctx.beginPath();
    ctx.arc(cx, cy, 6, 0, Math.PI * 2);
    ctx.fillStyle = C.paper;
    ctx.fill();
    ctx.strokeStyle = 'rgba(42, 40, 36, 0.22)';
    ctx.stroke();

    verts.forEach((v) => {
      const { color, x, y, angle } = v;
      const name = color.name || '';

      ctx.beginPath();
      ctx.arc(x, y, nodeR + 3, 0, Math.PI * 2);
      ctx.fillStyle = '#fff';
      ctx.fill();

      ctx.beginPath();
      ctx.arc(x, y, nodeR, 0, Math.PI * 2);
      ctx.fillStyle = color.hex;
      ctx.fill();
      ctx.strokeStyle = 'rgba(42, 40, 36, 0.35)';
      ctx.lineWidth = 1.2;
      ctx.stroke();

      const fs = labelFontSize(name);
      const labelR = R + nodeR + 12;
      let lx = cx + labelR * Math.cos(angle);
      let ly = cy + labelR * Math.sin(angle);
      const st = vertexLabelStyle(angle);

      ctx.font = `400 ${fs}px "Noto Serif SC", STSong, serif`;
      ctx.fillStyle = C.ink;
      ctx.textAlign = st.align;
      ctx.textBaseline = st.baseline;
      if (st.align === 'center' && st.baseline === 'bottom') ly -= st.pad;
      if (st.align === 'center' && st.baseline === 'top') ly += st.pad;
      if (st.align === 'right') lx -= st.pad;
      if (st.align === 'left') lx += st.pad;
      ctx.fillText(name, lx, ly);
    });

    ctx.restore();
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
    const photo = fitPhoto(sourceImg, LEFT_W - 8, PHOTO_MAX_H);
    return photo.h + PHOTO_GAP + PALETTE_H + 8;
  }

  function drawLeftColumn(ctx, sourceImg, colors, bodyY) {
    const panelX = PAD;
    const panelW = LEFT_W;
    const photo = fitPhoto(sourceImg, panelW - 12, PHOTO_MAX_H);
    const photoTop = bodyY + 6;
    const paletteY = photoTop + Math.max(photo.h, 0) + PHOTO_GAP;
    const panelH = paletteY - bodyY + PALETTE_H + 6;

    drawRoundedRect(ctx, panelX, bodyY, panelW, panelH, 8);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.35)';
    ctx.fill();
    ctx.strokeStyle = C.border;
    ctx.lineWidth = 1;
    ctx.stroke();

    if (photo.w && photo.h) {
      const px = panelX + 6;
      const py = photoTop;
      ctx.save();
      drawRoundedRect(ctx, px, py, photo.w, photo.h, 4);
      ctx.clip();
      ctx.drawImage(sourceImg, px, py, photo.w, photo.h);
      ctx.restore();
      ctx.strokeStyle = 'rgba(42, 40, 36, 0.14)';
      drawRoundedRect(ctx, px, py, photo.w, photo.h, 4);
      ctx.stroke();
    }

    drawFiveColorPalette(
      ctx,
      colors,
      panelX + 6,
      paletteY,
      panelW - 12,
      PALETTE_H,
    );

    return panelH;
  }

  function drawHeader(ctx) {
    ctx.fillStyle = C.ink;
    ctx.font = '400 34px "Noto Serif SC", STSong, serif';
    ctx.textAlign = 'center';
    ctx.fillText('色谱寻诗', W / 2, 40);

    ctx.strokeStyle = C.border;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(PAD * 1.5, HEADER_H - 4);
    ctx.lineTo(W - PAD * 1.5, HEADER_H - 4);
    ctx.stroke();
  }

  function drawColumnDivider(ctx, bodyY, bodyH) {
    const x = RIGHT_X - COL_GAP / 2;
    ctx.strokeStyle = 'rgba(42, 40, 36, 0.08)';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(x, bodyY);
    ctx.lineTo(x, bodyY + bodyH);
    ctx.stroke();
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(x + 1, bodyY);
    ctx.lineTo(x + 1, bodyY + bodyH);
    ctx.stroke();
  }

  async function buildCanvas(sourceImg, colors) {
    await ensureFonts();

    const poems = await Promise.all(colors.map((c) => loadPoetry(c.pinyin, c)));
    const ts = typeScale(colors.length);
    const measureCtx = document.createElement('canvas').getContext('2d');
    const innerW = RIGHT_W - ts.pad * 2 - ts.swatch - 12;

    let rightH = 0;
    colors.forEach((_, i) => {
      rightH += measureColorBlock(measureCtx, poems[i], innerW, ts);
    });

    const leftH = measureLeftColumn(sourceImg);
    const bodyH = Math.max(rightH, leftH);
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

    const bodyY = HEADER_H + 6;
    drawLeftColumn(ctx, sourceImg, colors, bodyY);
    drawColumnDivider(ctx, bodyY, bodyH);

    let cy = bodyY;
    colors.forEach((c, i) => {
      cy += drawColorBlock(ctx, RIGHT_X, cy, c, poems[i], RIGHT_W, ts);
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
    if (hintEl) {
      hintEl.textContent = wechat
        ? '长按图片保存'
        : '长按图片可保存';
    }
    if (saveBtnEl) {
      saveBtnEl.textContent = wechat ? '保存提示' : '保存图片';
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
