/**
 * 色谱寻诗 — 主流程
 */
(() => {
  const uploadZone = document.getElementById('upload-zone');
  const fileInput = document.getElementById('file-input');
  const previewImg = document.getElementById('preview-img');
  const previewPlaceholder = document.getElementById('preview-placeholder');
  const colorList = document.getElementById('color-list');
  const rareColorSpot = document.getElementById('rare-color-spot');
  const panelHint = document.getElementById('panel-hint');
  const panelStatus = document.getElementById('panel-status');
  const snapshotBar = document.getElementById('snapshot-bar');
  const snapshotBtn = document.getElementById('snapshot-btn');

  const achProgressLabel = document.getElementById('ach-progress-label');
  const achBadge = document.getElementById('ach-badge');
  const achievementsCta = document.getElementById('achievements-cta');
  const unlockOverlay = document.getElementById('unlock-overlay');
  const unlockImg = document.getElementById('unlock-img');
  const unlockTitle = document.getElementById('unlock-title');
  const unlockSub = document.getElementById('unlock-sub');
  const unlockContinue = document.getElementById('unlock-continue');

  const poetryRawCache = new Map();
  let currentColors = [];
  let expandedPinyin = null;
  let unlockQueue = [];
  let manifestReady = false;

  function setStatus(text, loading = false) {
    panelStatus.textContent = text;
    panelStatus.classList.toggle('loading', loading);
    panelStatus.hidden = !text;
  }

  function renderEmptyPanel() {
    colorList.innerHTML = '';
    currentColors = [];
    panelHint.hidden = false;
    panelHint.textContent = '待上传图片后，此处将显示图中前五主色及其中国色名';
    if (snapshotBar) snapshotBar.hidden = true;
    if (rareColorSpot) rareColorSpot.hidden = true;
    setStatus('');
  }

  function escapeHtml(s) {
    return PoetryUI.escapeHtml(s);
  }

  function getMergedPoetry(pinyin) {
    const raw = poetryRawCache.get(pinyin);
    return raw || { pinyin, entries: [], coverage: '0/5' };
  }

  function refreshPoetryPanel(card, pinyin) {
    const inner = card.querySelector('.poetry-inner');
    PoetryUI.mountPanel(inner, pinyin, () => getMergedPoetry(pinyin));
  }

  function paintColorList() {
    panelHint.hidden = true;
    colorList.innerHTML = '';

    currentColors.forEach((c) => {
      const card = document.createElement('article');
      card.className = 'color-card';
      card.dataset.pinyin = c.pinyin;

      const rgbText = `RGB(${c.rgb[0]}, ${c.rgb[1]}, ${c.rgb[2]})`;
      const pct = c.ratio != null ? `${Math.round(c.ratio * 100)}%` : '';
      const gloss = ColorGlosses.get(c.pinyin);
      const glossHtml = gloss
        ? `<span class="color-gloss">${escapeHtml(gloss)}</span>`
        : '';

      card.innerHTML = `
        <div class="color-header-wrap">
          <button class="color-header" type="button" aria-expanded="false">
            <span class="swatch" style="background:${c.hex}"></span>
            <span class="color-ident">
              <span class="color-ident-top">
                <span class="color-name">${escapeHtml(c.name)}</span>
                <span class="color-rgb">${rgbText}${pct ? ` · ${pct}` : ''}</span>
              </span>
              ${glossHtml}
            </span>
            <span class="chevron" aria-hidden="true"></span>
          </button>
        </div>
        <div class="poetry-panel">
          <div class="poetry-inner"></div>
        </div>
      `;

      card.querySelector('.color-header').addEventListener('click', () => togglePoetry(c, card));
      colorList.appendChild(card);
    });
  }

  function paintRareColorSpot(rare) {
    if (!rareColorSpot) return;
    if (!rare) {
      rareColorSpot.hidden = true;
      rareColorSpot.innerHTML = '';
      return;
    }
    rareColorSpot.hidden = false;
    rareColorSpot.innerHTML = `
      <p class="rare-color-label">稀有色</p>
      <div class="rare-color-body">
        <span class="rare-color-swatch" style="background:${rare.hex}"></span>
        <span class="rare-color-meta">
          <span class="rare-color-name">${escapeHtml(rare.name)}</span>
          <span class="rare-color-score">稀有度 ${rare.rarityScore}</span>
        </span>
      </div>
    `;
  }

  function renderColors(colors) {
    currentColors = colors;
    if (currentColors.length === 0) {
      colorList.innerHTML = '';
      panelHint.hidden = false;
      panelHint.textContent = '待上传图片后，此处将显示图中前五主色及其中国色名';
      if (snapshotBar) snapshotBar.hidden = true;
      if (rareColorSpot) rareColorSpot.hidden = true;
      return;
    }
    paintColorList();
    paintRareColorSpot(ColorRarity.pickRarest(colors));
    if (snapshotBar) snapshotBar.hidden = false;
  }

  async function togglePoetry(color, card) {
    const header = card.querySelector('.color-header');
    const isOpen = card.classList.contains('open');

    document.querySelectorAll('.color-card.open').forEach((el) => {
      if (el !== card) {
        el.classList.remove('open');
        el.querySelector('.color-header').setAttribute('aria-expanded', 'false');
      }
    });

    if (isOpen) {
      card.classList.remove('open');
      header.setAttribute('aria-expanded', 'false');
      expandedPinyin = null;
      return;
    }

    card.classList.add('open');
    header.setAttribute('aria-expanded', 'true');
    expandedPinyin = color.pinyin;

    const inner = card.querySelector('.poetry-inner');
    inner.innerHTML = '<p class="poetry-loading">载句中…</p>';

    try {
      await loadPoetryRaw(color.pinyin, color);
      refreshPoetryPanel(card, color.pinyin);
    } catch {
      inner.innerHTML = '<p class="poetry-empty">诗句加载失败</p>';
    }
  }

  async function loadPoetryRaw(pinyin, colorMeta) {
    if (poetryRawCache.has(pinyin)) return poetryRawCache.get(pinyin);

    let data;
    if (typeof POETRY_LIBRARY !== 'undefined' && POETRY_LIBRARY[pinyin]) {
      data = POETRY_LIBRARY[pinyin];
    } else {
      try {
        const res = await fetch(`data/poetry/${pinyin}.json`);
        if (res.ok) data = await res.json();
      } catch { /* fall through */ }
    }

    if (!data) {
      data = {
        color: colorMeta?.name || '',
        pinyin,
        hex: colorMeta?.hex || '',
        entries: [],
        coverage: '0/5',
      };
    }

    poetryRawCache.set(pinyin, data);
    return data;
  }

  function updateAchievementsUI(flashBadge = false) {
    const { unlocked, total } = Achievements.getProgress();
    if (achProgressLabel) achProgressLabel.textContent = `${unlocked} / ${total}`;

    if (flashBadge && achBadge) {
      achBadge.hidden = false;
      achBadge.textContent = '+';
      achievementsCta?.classList.add('ach-cta-flash');
      setTimeout(() => {
        achievementsCta?.classList.remove('ach-cta-flash');
        achBadge.hidden = true;
      }, 2400);
    }
  }

  function showUnlockOverlay(bookmark) {
    unlockImg.src = Achievements.assetUrl(bookmark.file);
    unlockImg.alt = `${bookmark.name} 书签`;
    unlockImg.hidden = false;
    unlockTitle.textContent = `识得【${bookmark.name}】`;
    unlockSub.textContent = '书签已入藏';

    unlockOverlay.hidden = false;
    unlockOverlay.setAttribute('aria-hidden', 'false');
    document.body.classList.add('unlock-open');
    requestAnimationFrame(() => unlockOverlay.classList.add('unlock-visible'));
  }

  function hideUnlockOverlay() {
    unlockOverlay.classList.remove('unlock-visible');
    document.body.classList.remove('unlock-open');
    setTimeout(() => {
      unlockOverlay.hidden = true;
      unlockOverlay.setAttribute('aria-hidden', 'true');
      unlockImg.hidden = true;
      unlockImg.src = '';
      processUnlockQueue();
    }, 320);
  }

  function processUnlockQueue() {
    if (unlockQueue.length === 0) return;
    const next = unlockQueue.shift();
    showUnlockOverlay(next);
  }

  function enqueueUnlocks(newly) {
    if (!newly.length) return;
    unlockQueue.push(...newly);
    if (!document.body.classList.contains('unlock-open')) {
      processUnlockQueue();
    }
    updateAchievementsUI(true);
  }

  async function handleFile(file) {
    if (!file || !file.type.startsWith('image/')) return;

    setStatus('设色中…', true);
    renderEmptyPanel();

    try {
      const result = await ColorExtract.extractPixels(file);

      if (result.validPixels === 0) {
        setStatus('图中未检出有效像素，请换一张图片');
        previewPlaceholder.hidden = false;
        previewImg.hidden = true;
        return;
      }

      previewPlaceholder.hidden = true;
      previewImg.hidden = false;
      previewImg.src = result.previewUrl;

      const mapped = ColorMatch.mapFromPixels(result.data, result.width, result.height);
      renderColors(mapped);
      setStatus('');

      if (manifestReady) {
        const newly = Achievements.checkUnlocks(mapped);
        enqueueUnlocks(newly);
      }
    } catch (err) {
      const msg = location.protocol === 'file:'
        ? '请通过 serve.bat 启动本地服务器，不要直接双击 HTML'
        : `分析失败：${err.message || '请重试'}`;
      setStatus(msg);
      console.error(err);
    }
  }

  uploadZone.addEventListener('click', () => fileInput.click());
  uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('drag-over');
  });
  uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('drag-over'));
  uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
    handleFile(e.dataTransfer.files[0]);
  });
  fileInput.addEventListener('change', () => {
    handleFile(fileInput.files[0]);
    fileInput.value = '';
  });

  unlockContinue?.addEventListener('click', hideUnlockOverlay);

  snapshotBtn?.addEventListener('click', async () => {
    if (!currentColors.length || previewImg.hidden) return;
    snapshotBtn.disabled = true;
    const prevLabel = snapshotBtn.querySelector('.snapshot-btn-text')?.textContent;
    const labelEl = snapshotBtn.querySelector('.snapshot-btn-text');
    try {
      await ColorSnapshot.open(previewImg, currentColors, (msg) => {
        if (labelEl) labelEl.textContent = msg.replace(/…$/, '');
      });
    } catch (err) {
      setStatus(err.message || '快照生成失败');
    } finally {
      snapshotBtn.disabled = false;
      if (labelEl && prevLabel) labelEl.textContent = prevLabel;
    }
  });

  ColorSnapshot.bindDom();

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !unlockOverlay.hidden) hideUnlockOverlay();
  });

  renderEmptyPanel();

  Achievements.loadManifest()
    .then(() => {
      manifestReady = true;
      updateAchievementsUI();
    })
    .catch(() => {
      if (achProgressLabel) achProgressLabel.textContent = '—';
    });

  const dailyStatusLabel = document.getElementById('daily-status-label');
  const headerDailyStatus = document.getElementById('header-daily-status');

  function updateDailyUI() {
    const label = DailyChallenge.getStatusLabel();
    if (dailyStatusLabel) dailyStatusLabel.textContent = label;
    if (headerDailyStatus) headerDailyStatus.textContent = label;
  }

  DailyChallenge.loadData()
    .then(updateDailyUI)
    .catch(() => {
      if (dailyStatusLabel) dailyStatusLabel.textContent = '—';
      if (headerDailyStatus) headerDailyStatus.textContent = '—';
    });
})();
