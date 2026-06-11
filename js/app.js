/**
 * 色谱寻诗 — 主流程
 */
(() => {
  const uploadZone = document.getElementById('upload-zone');
  const fileInput = document.getElementById('file-input');
  const previewImg = document.getElementById('preview-img');
  const previewPlaceholder = document.getElementById('preview-placeholder');
  const colorList = document.getElementById('color-list');
  const panelHint = document.getElementById('panel-hint');
  const panelStatus = document.getElementById('panel-status');

  const poetryRawCache = new Map();
  let currentColors = [];
  let expandedPinyin = null;

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

      card.innerHTML = `
        <div class="color-header-wrap">
          <button class="color-header" type="button" aria-expanded="false">
            <span class="swatch" style="background:${c.hex}"></span>
            <span class="color-name">${escapeHtml(c.name)}</span>
            <span class="color-rgb">${rgbText}${pct ? ` · ${pct}` : ''}</span>
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

  function renderColors(colors) {
    currentColors = colors;
    if (currentColors.length === 0) {
      colorList.innerHTML = '';
      panelHint.hidden = false;
      panelHint.textContent = '待上传图片后，此处将显示图中前五主色及其中国色名';
      return;
    }
    paintColorList();
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

  async function handleFile(file) {
    if (!file || !file.type.startsWith('image/')) return;

    setStatus('设色中…', true);
    renderEmptyPanel();

    try {
      const result = await ColorExtract.extractTopColors(file);

      if (result.validPixels === 0) {
        setStatus('图中未检出显著色，请换一张色彩更丰富的图');
        previewPlaceholder.hidden = false;
        previewImg.hidden = true;
        return;
      }

      previewPlaceholder.hidden = true;
      previewImg.hidden = false;
      previewImg.src = result.previewUrl;

      const mapped = await ColorMatch.mapColors(result.colors);
      renderColors(mapped);
      setStatus('');
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

  renderEmptyPanel();
})();
