/**

 * 数据浏览 — RGB 索引与诗词库（内嵌数据，无需 fetch）

 */

(() => {

  const searchInput = document.getElementById('search-input');

  const searchMode = document.getElementById('search-mode');

  const browseStats = document.getElementById('browse-stats');

  const colorsTbody = document.getElementById('colors-tbody');

  const poetryList = document.getElementById('poetry-list');

  const noPoetryTbody = document.getElementById('no-poetry-tbody');

  const colorCountEl = document.getElementById('color-count');

  const gameColorCountEl = document.getElementById('game-color-count');

  const poetryCountEl = document.getElementById('poetry-count');

  const noPoetryCountEl = document.getElementById('no-poetry-count');



  let colors = [];

  let rgbIndex = [];

  let poetryColors = [];

  let noPoetryColors = [];

  let activeTab = 'poetry';



  const PLACEHOLDERS = {

    name: '搜索色名或拼音…',

    rgb: '如 255,128,64 或 128',

    hex: '如 #ff8040 或 ff8040',

  };



  const escapeHtml = PoetryUI.escapeHtml;



  function updatePlaceholder() {

    if (!searchInput) return;

    const mode = searchMode?.value || 'name';

    searchInput.placeholder = PLACEHOLDERS[mode] || PLACEHOLDERS.name;

  }



  function matchNameQuery(item, q) {

    if (!q) return true;

    const ql = q.toLowerCase();

    const hay = `${item.name || ''}${item.namePinyin || ''}`.toLowerCase();

    return hay.includes(ql);

  }



  function matchRgbQuery(item, q) {

    if (!q) return true;

    const raw = q.trim();

    const tokens = raw.split(/[\s,，]+/).filter(Boolean).map((t) => parseInt(t, 10));

    const [r, g, b] = item.RGB || [0, 0, 0];



    if (tokens.length > 0 && !tokens.some((n) => Number.isNaN(n))) {

      if (tokens.length === 1) {

        const n = tokens[0];

        return r === n || g === n || b === n;

      }

      if (tokens.length === 2) {

        return r === tokens[0] && g === tokens[1];

      }

      return r === tokens[0] && g === tokens[1] && b === tokens[2];

    }



    const hay = `${r},${g},${b} ${r} ${g} ${b}`;

    return hay.includes(raw);

  }



  function matchHexQuery(item, q) {

    if (!q) return true;

    const norm = q.trim().replace(/^#/, '').toLowerCase();

    const hex = (item.hex || '').replace(/^#/, '').toLowerCase();

    return hex.includes(norm);

  }



  function getSearchMode() {

    return searchMode?.value || 'name';

  }



  function matchByMode(item, q) {

    const mode = getSearchMode();

    if (mode === 'rgb') return matchRgbQuery(item, q);

    if (mode === 'hex') return matchHexQuery(item, q);

    return matchNameQuery(item, q);

  }



  function getPoetry(pinyin, colorMeta) {

    if (typeof POETRY_LIBRARY !== 'undefined' && POETRY_LIBRARY[pinyin]) {

      return POETRY_LIBRARY[pinyin];

    }

    return {

      color: colorMeta?.name || pinyin,

      pinyin,

      hex: colorMeta?.hex || '#888888',

      entries: [],

      coverage: '0/5',

    };

  }



  function hasPoetry(pinyin) {

    if (typeof POETRY_LIBRARY !== 'undefined' && POETRY_LIBRARY[pinyin]) {

      return !!(POETRY_LIBRARY[pinyin].entries?.length);

    }

    return false;

  }



  function buildPoetryColors() {

    const colorByPinyin = new Map();

    for (const c of colors) {

      if (!colorByPinyin.has(c.pinyin)) colorByPinyin.set(c.pinyin, c);

    }



    const allUnique = [...colorByPinyin.values()];



    poetryColors = allUnique

      .filter((c) => hasPoetry(c.pinyin))

      .map((c) => {

        const data = getPoetry(c.pinyin, c);

        return {

          name: data.color || c.name,

          namePinyin: c.namePinyin || '',

          pinyin: c.pinyin,

          hex: data.hex || c.hex,

          RGB: c.RGB,

          coverage: data.coverage || `${data.entries.length}条`,

          entries: data.entries,

        };

      })

      .sort((a, b) => a.name.localeCompare(b.name, 'zh-CN'));



    noPoetryColors = allUnique

      .filter((c) => !hasPoetry(c.pinyin))

      .sort((a, b) => a.name.localeCompare(b.name, 'zh-CN'));

  }



  function renderColorsTable(filter = '') {

    const q = filter.trim();

    const rows = rgbIndex.filter((c) => matchByMode(c, q));

    browseStats.textContent = `显示 ${rows.length} / ${rgbIndex.length} 条`;



    colorsTbody.innerHTML = rows.map((c) => {

      const [r, g, b] = c.RGB;

      const py = c.namePinyin || '';

      const poem = c.gameId ? getPoetry(c.gameId, c) : null;

      const snippet = poem?.entries?.[0]?.line

        ? escapeHtml(poem.entries[0].line)

        : '<span class="muted">—</span>';

      return `<tr>

        <td><span class="swatch-sm" style="background:${c.hex}"></span></td>

        <td>${escapeHtml(c.name)}</td>

        <td>${escapeHtml(py)}</td>

        <td><code>${r}</code></td>

        <td><code>${g}</code></td>

        <td><code>${b}</code></td>

        <td><code>${c.hex}</code></td>

        <td class="poem-snippet">${snippet}</td>

      </tr>`;

    }).join('');

  }



  function renderNoPoetryList(filter = '') {

    const q = filter.trim();

    const rows = noPoetryColors.filter((c) => matchByMode(c, q));

    browseStats.textContent = `显示 ${rows.length} / ${noPoetryColors.length} 种无诗句颜色`;



    noPoetryTbody.innerHTML = rows.length

      ? rows.map((c) => {

        const [r, g, b] = c.RGB;

        return `<tr>

          <td><span class="swatch-sm" style="background:${c.hex}"></span></td>

          <td>${escapeHtml(c.name)}</td>

          <td><code>${r}, ${g}, ${b}</code></td>

          <td><code>${c.hex}</code></td>

        </tr>`;

      }).join('')

      : `<tr><td colspan="4" class="poetry-empty-cell">${q ? `未找到「${escapeHtml(q)}」` : '暂无数据'}</td></tr>`;

  }



  function renderPoetryList(filter = '') {

    const q = filter.trim();

    const rows = poetryColors.filter((c) => matchByMode(c, q));

    browseStats.textContent = `显示 ${rows.length} / ${poetryColors.length} 种有诗句的颜色`;



    if (rows.length === 0) {

      poetryList.innerHTML = q

        ? `<p class="poetry-empty">未找到「${escapeHtml(q)}」相关颜色</p>`

        : '<p class="poetry-empty">暂无诗句数据</p>';

      return;

    }



    poetryList.innerHTML = rows.map((c) => `

      <article class="poetry-browse-card" data-pinyin="${c.pinyin}">

        <div class="poetry-browse-header-wrap">

          <button class="poetry-browse-header" type="button">

            <span class="swatch-sm" style="background:${c.hex}"></span>

            <span class="poetry-browse-name">${escapeHtml(c.name)}</span>

            <span class="poetry-browse-meta">${escapeHtml(c.coverage || '')}</span>

            <span class="chevron" aria-hidden="true"></span>

          </button>

        </div>

        <div class="poetry-browse-body"><p class="poetry-loading">点击展开查看诗句</p></div>

      </article>

    `).join('');



    poetryList.querySelectorAll('.poetry-browse-header').forEach((btn) => {

      btn.addEventListener('click', () => togglePoetryCard(btn.closest('.poetry-browse-card')));

    });

  }



  function togglePoetryCard(card) {

    const pinyin = card.dataset.pinyin;

    const body = card.querySelector('.poetry-browse-body');

    const isOpen = card.classList.contains('open');

    const colorMeta = poetryColors.find((c) => c.pinyin === pinyin) || { pinyin, name: pinyin };



    document.querySelectorAll('.poetry-browse-card.open').forEach((el) => {

      if (el !== card) el.classList.remove('open');

    });



    if (isOpen) {

      card.classList.remove('open');

      return;

    }



    card.classList.add('open');

    const data = getPoetry(pinyin, colorMeta);

    body.innerHTML = PoetryUI.renderList(data);

  }



  function updateNoPoetryTab() {

    const tab = document.querySelector('.browse-tab[data-tab="no-poetry"]');

    const panel = document.getElementById('tab-no-poetry');

    const show = noPoetryColors.length > 0;

    if (tab) {

      tab.hidden = !show;

      tab.classList.toggle('browse-tab-hidden', !show);

    }

    if (panel && !show && activeTab === 'no-poetry') {

      switchTab('poetry');

    }

  }



  function rebuildAndRender() {

    buildPoetryColors();

    if (colorCountEl) colorCountEl.textContent = rgbIndex.length;

    if (gameColorCountEl) gameColorCountEl.textContent = colors.length;

    poetryCountEl.textContent = poetryColors.length;

    if (noPoetryCountEl) noPoetryCountEl.textContent = noPoetryColors.length;

    updateNoPoetryTab();

    applyFilter();

  }



  function switchTab(tab) {

    activeTab = tab;

    document.querySelectorAll('.browse-tab').forEach((btn) => {

      const on = btn.dataset.tab === tab;

      btn.classList.toggle('active', on);

      btn.setAttribute('aria-selected', on);

    });

    document.querySelectorAll('.browse-panel').forEach((panel) => {

      const on = panel.id === `tab-${tab}`;

      panel.classList.toggle('active', on);

      panel.hidden = !on;

    });

    applyFilter();

  }



  function applyFilter() {

    const q = searchInput.value;

    if (activeTab === 'colors') renderColorsTable(q);

    else if (activeTab === 'poetry') renderPoetryList(q);

    else renderNoPoetryList(q);

  }



  function init() {

    if (typeof COLORS_DATA === 'undefined') {

      browseStats.textContent = '色板数据未加载，请确认已引入 js/colors-data.js';

      return;

    }

    colors = COLORS_DATA;

    rgbIndex = typeof RGB_INDEX_DATA !== 'undefined' ? RGB_INDEX_DATA : [];

    updatePlaceholder();

    rebuildAndRender();

  }



  document.querySelectorAll('.browse-tab').forEach((btn) => {

    btn.addEventListener('click', () => switchTab(btn.dataset.tab));

  });



  searchInput.addEventListener('input', applyFilter);

  if (searchMode) {

    searchMode.addEventListener('change', () => {

      updatePlaceholder();

      applyFilter();

    });

  }



  init();

})();


