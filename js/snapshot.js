/**
 * 识色结果快照 — Canvas 竖版排版，适配手机分享
 */
const ColorSnapshot = (() => {
  const W = 720;
  const PAD = 36;
  const CONTENT_W = W - PAD * 2;

  const C = {
    paper: '#F4F0E6',
    paperMid: '#EDE8DC',
    ink: '#2A2824',
    inkLight: '#6B6560',
    inkFaint: '#A8A098',
    border: 'rgba(42, 40, 36, 0.14)',
    accent: 'rgba(42, 40, 36, 0.06)',
  };

  let overlayEl = null;
  let previewImgEl = null;
  let saveBtnEl = null;
  let closeBtnEl = null;
  let lastBlobUrl = null;
  let lastBlob = null;

  async function ensureFonts() {
    if (!document.fonts) return;
    await Promise.all([
      document.fonts.load('400 32px "Noto Serif SC"'),
      document.fonts.load('300 24px "Noto Serif SC"'),
      document.fonts.load('300 20px "Noto Serif SC"'),
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

  function measureBlock(ctx, color, poetry, gloss, compact) {
    const fs = compact ? 22 : 24;
    const lineFs = compact ? 26 : 28;
    const metaFs = 20;
    const gap = 14;
    let h = 0;

    ctx.font = `400 ${fs}px "Noto Serif SC", STSong, serif`;
    h += fs + 6;
    if (gloss) {
      ctx.font = `300 ${metaFs}px "Noto Serif SC", STSong, serif`;
      h += metaFs + 8;
    }
    h += gap;

    const entry = poetry?.entries?.[0];
    if (entry?.line) {
      ctx.font = `300 ${lineFs}px "Noto Serif SC", STSong, serif`;
      const poemLines = wrapText(ctx, entry.line, CONTENT_W - 52);
      h += poemLines.length * (lineFs + 10);
      const meta = poemMeta(entry);
      if (meta) {
        ctx.font = `300 ${metaFs}px "Noto Serif SC", STSong, serif`;
        h += metaFs + 12;
      }
    } else {
      ctx.font = `300 ${metaFs}px "Noto Serif SC", STSong, serif`;
      h += metaFs + 8;
    }

    h += 28;
    return h;
  }

  function drawRoundedRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r);
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
  }

  async function buildCanvas(sourceImg, colors) {
    await ensureFonts();

    const compact = colors.length >= 5;
    const poems = await Promise.all(
      colors.map((c) => loadPoetry(c.pinyin, c)),
    );

    const measureCtx = document.createElement('canvas').getContext('2d');
    const imgMaxH = compact ? 240 : 300;

    let photoH = 0;
    let photoW = CONTENT_W;
    if (sourceImg?.naturalWidth) {
      const scale = Math.min(CONTENT_W / sourceImg.naturalWidth, imgMaxH / sourceImg.naturalHeight, 1);
      photoW = Math.round(sourceImg.naturalWidth * scale);
      photoH = Math.round(sourceImg.naturalHeight * scale);
    }

    let totalH = PAD;
    totalH += 52;
    totalH += 28;
    totalH += 24;
    if (photoH) totalH += photoH + 32;
    else totalH += 8;
    totalH += 1;

    colors.forEach((c, i) => {
      totalH += measureBlock(
        measureCtx,
        c,
        poems[i],
        ColorGlosses?.get?.(c.pinyin),
        compact,
      );
    });

    totalH += 56;
    totalH += PAD;

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const canvas = document.createElement('canvas');
    canvas.width = W * dpr;
    canvas.height = totalH * dpr;
    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);

    ctx.fillStyle = C.paper;
    ctx.fillRect(0, 0, W, totalH);

    ctx.fillStyle = C.accent;
    ctx.fillRect(0, 0, W, 120);

    let y = PAD;

    ctx.fillStyle = C.ink;
    ctx.font = '400 34px "Noto Serif SC", STSong, serif';
    ctx.textAlign = 'center';
    ctx.fillText('色谱寻诗', W / 2, y + 34);
    y += 48;

    ctx.fillStyle = C.inkLight;
    ctx.font = '300 20px "Noto Serif SC", STSong, serif';
    ctx.fillText('观其五色 · 古人如何写这颜色', W / 2, y + 18);
    y += 36;

    const dateStr = new Date().toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
    ctx.fillStyle = C.inkFaint;
    ctx.font = '300 18px "Noto Serif SC", STSong, serif';
    ctx.fillText(dateStr, W / 2, y + 16);
    y += 32;

    if (photoH) {
      const photoX = (W - photoW) / 2;
      ctx.save();
      drawRoundedRect(ctx, photoX, y, photoW, photoH, 4);
      ctx.clip();
      ctx.drawImage(sourceImg, photoX, y, photoW, photoH);
      ctx.restore();
      ctx.strokeStyle = C.border;
      ctx.lineWidth = 1;
      drawRoundedRect(ctx, photoX, y, photoW, photoH, 4);
      ctx.stroke();
      y += photoH + 28;
    }

    ctx.strokeStyle = C.border;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(PAD, y);
    ctx.lineTo(W - PAD, y);
    ctx.stroke();
    y += 24;

    colors.forEach((c, idx) => {
      const poetry = poems[idx];
      const gloss = ColorGlosses?.get?.(c.pinyin);
      const pct = c.ratio != null ? `${Math.round(c.ratio * 100)}%` : '';
      const fs = compact ? 22 : 24;
      const lineFs = compact ? 26 : 28;
      const metaFs = 20;

      const swatch = 28;
      ctx.fillStyle = c.hex;
      drawRoundedRect(ctx, PAD, y + 2, swatch, swatch, 3);
      ctx.fill();
      ctx.strokeStyle = C.border;
      ctx.lineWidth = 1;
      ctx.stroke();

      ctx.textAlign = 'left';
      ctx.fillStyle = C.ink;
      ctx.font = `400 ${fs}px "Noto Serif SC", STSong, serif`;
      const nameX = PAD + swatch + 14;
      ctx.fillText(c.name, nameX, y + fs + 2);

      if (pct) {
        ctx.fillStyle = C.inkFaint;
        ctx.font = `300 ${metaFs}px Consolas, monospace`;
        const pctW = ctx.measureText(pct).width;
        ctx.fillText(pct, W - PAD - pctW, y + fs);
      }

      y += fs + 10;

      if (gloss) {
        ctx.fillStyle = C.inkFaint;
        ctx.font = `300 ${metaFs}px "Noto Serif SC", STSong, serif`;
        ctx.fillText(gloss, nameX, y + metaFs - 2);
        y += metaFs + 12;
      } else {
        y += 4;
      }

      const entry = poetry?.entries?.[0];
      const textX = PAD + 20;
      const textW = CONTENT_W - 36;

      if (entry?.line) {
        ctx.fillStyle = C.ink;
        ctx.font = `300 ${lineFs}px "Noto Serif SC", STSong, serif`;
        const poemLines = wrapText(ctx, `「${entry.line}」`, textW);
        poemLines.forEach((ln) => {
          ctx.fillText(ln, textX, y + lineFs);
          y += lineFs + 10;
        });

        const meta = poemMeta(entry);
        if (meta) {
          ctx.fillStyle = C.inkLight;
          ctx.font = `300 ${metaFs}px "Noto Serif SC", STSong, serif`;
          const metaLines = wrapText(ctx, meta, textW);
          metaLines.forEach((ln) => {
            ctx.fillText(ln, textX, y + metaFs);
            y += metaFs + 6;
          });
          y += 8;
        }
      } else {
        ctx.fillStyle = C.inkFaint;
        ctx.font = `300 ${metaFs}px "Noto Serif SC", STSong, serif`;
        ctx.fillText('暂无诗句', textX, y + metaFs);
        y += metaFs + 12;
      }

      y += 16;
      ctx.strokeStyle = C.border;
      ctx.beginPath();
      ctx.moveTo(PAD + 12, y);
      ctx.lineTo(W - PAD - 12, y);
      ctx.stroke();
      y += 20;
    });

    ctx.textAlign = 'center';
    ctx.fillStyle = C.inkFaint;
    ctx.font = '300 17px "Noto Serif SC", STSong, serif';
    ctx.fillText('色名参考中国色 · 每色示诗一例', W / 2, totalH - PAD + 4);

    return canvas;
  }

  function revokeLastUrl() {
    if (lastBlobUrl) {
      URL.revokeObjectURL(lastBlobUrl);
      lastBlobUrl = null;
    }
    lastBlob = null;
  }

  function bindDom() {
    overlayEl = document.getElementById('snapshot-overlay');
    previewImgEl = document.getElementById('snapshot-preview');
    saveBtnEl = document.getElementById('snapshot-save');
    closeBtnEl = document.getElementById('snapshot-close');

    closeBtnEl?.addEventListener('click', hide);
    overlayEl?.querySelector('.snapshot-backdrop')?.addEventListener('click', hide);

    saveBtnEl?.addEventListener('click', () => {
      if (!lastBlob) return;
      const a = document.createElement('a');
      const stamp = new Date().toISOString().slice(0, 10);
      a.download = `色谱寻诗-${stamp}.png`;
      a.href = lastBlobUrl;
      a.click();
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && overlayEl && !overlayEl.hidden) hide();
    });
  }

  function showPreview(blob) {
    revokeLastUrl();
    lastBlob = blob;
    lastBlobUrl = URL.createObjectURL(blob);
    previewImgEl.src = lastBlobUrl;
    previewImgEl.hidden = false;
    overlayEl.hidden = false;
    overlayEl.setAttribute('aria-hidden', 'false');
    document.body.classList.add('snapshot-open');
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
    const blob = await new Promise((resolve, reject) => {
      canvas.toBlob((b) => (b ? resolve(b) : reject(new Error('生成失败'))), 'image/png');
    });

    return blob;
  }

  async function open(sourceImgEl, colors, onProgress) {
    const blob = await capture(sourceImgEl, colors, onProgress);
    showPreview(blob);
    return blob;
  }

  return { bindDom, open, capture, hide };
})();
