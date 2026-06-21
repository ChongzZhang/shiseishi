/**
 * 成就书签页 — 网格展示、放大预览与下载
 */
(() => {
  const grid = document.getElementById('ach-grid');
  const progressFill = document.getElementById('ach-progress-fill');
  const progressText = document.getElementById('ach-progress-text');
  const previewOverlay = document.getElementById('ach-preview-overlay');
  const previewImg = document.getElementById('ach-preview-img');
  const previewTitle = document.getElementById('ach-preview-title');
  const previewMeta = document.getElementById('ach-preview-meta');
  const previewDownload = document.getElementById('ach-preview-download');

  function escapeHtml(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  function showPreview(bookmark, unlockedAt) {
    const imgSrc = Achievements.assetUrl(bookmark.file);
    previewImg.src = imgSrc;
    previewImg.alt = `${bookmark.name} 书签`;
    previewTitle.textContent = bookmark.name;
    previewMeta.textContent = unlockedAt
      ? `${Achievements.formatDate(unlockedAt)} · ${bookmark.hex}`
      : bookmark.hex;
    previewDownload.href = imgSrc;
    previewDownload.download = bookmark.file;

    previewOverlay.hidden = false;
    previewOverlay.setAttribute('aria-hidden', 'false');
    document.body.classList.add('ach-preview-open');
    requestAnimationFrame(() => previewOverlay.classList.add('ach-preview-visible'));
  }

  function hidePreview() {
    previewOverlay.classList.remove('ach-preview-visible');
    document.body.classList.remove('ach-preview-open');
    setTimeout(() => {
      previewOverlay.hidden = true;
      previewOverlay.setAttribute('aria-hidden', 'true');
      previewImg.src = '';
    }, 280);
  }

  function renderCard(bookmark, unlocked, unlockedAt) {
    const card = document.createElement('article');
    card.className = `ach-card${unlocked ? ' ach-card-unlocked' : ' ach-card-locked'}`;

    const imgSrc = Achievements.assetUrl(bookmark.file);
    const dateStr = unlockedAt ? Achievements.formatDate(unlockedAt) : '';

    if (unlocked) {
      card.innerHTML = `
        <button type="button" class="ach-card-img-wrap ach-card-preview-btn" aria-label="放大预览 ${escapeHtml(bookmark.name)} 书签">
          <img class="ach-card-img" src="${escapeHtml(imgSrc)}" alt="${escapeHtml(bookmark.name)} 书签" loading="lazy">
        </button>
        <div class="ach-card-info">
          <span class="ach-swatch" style="background:${escapeHtml(bookmark.hex)}"></span>
          <span class="ach-card-name">${escapeHtml(bookmark.name)}</span>
          <span class="ach-card-date">${escapeHtml(dateStr)}</span>
        </div>
        <a class="ach-download-btn" href="${escapeHtml(imgSrc)}" download="${escapeHtml(bookmark.file)}" aria-label="下载 ${escapeHtml(bookmark.name)} 书签">下载书签</a>
      `;
      card.querySelector('.ach-card-preview-btn').addEventListener('click', () => {
        showPreview(bookmark, unlockedAt);
      });
    } else {
      card.innerHTML = `
        <div class="ach-card-img-wrap ach-card-placeholder">
          <span class="ach-lock-icon" aria-hidden="true">?</span>
          <span class="ach-swatch ach-swatch-muted" style="background:${escapeHtml(bookmark.hex)}"></span>
        </div>
        <div class="ach-card-info">
          <span class="ach-card-name">${escapeHtml(bookmark.name)}</span>
          <span class="ach-card-hint">上传含此色的图片以解锁</span>
        </div>
      `;
      card.title = '上传含此色的图片以解锁';
    }

    return card;
  }

  previewOverlay?.querySelectorAll('[data-close-preview]').forEach((el) => {
    el.addEventListener('click', hidePreview);
  });
  previewDownload?.addEventListener('click', (e) => e.stopPropagation());

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && previewOverlay && !previewOverlay.hidden) hidePreview();
  });

  async function init() {
    try {
      await Achievements.loadManifest();
    } catch {
      grid.innerHTML = '<p class="ach-error">书签清单加载失败，请刷新重试</p>';
      return;
    }

    const manifest = Achievements.getManifest();
    const store = JSON.parse(localStorage.getItem('shiseishi-achievements-v1') || '{}');
    const unlockedMap = store.unlocked || {};

    const { unlocked, total } = Achievements.getProgress();
    const pct = total ? Math.round((unlocked / total) * 100) : 0;

    if (progressFill) progressFill.style.width = `${pct}%`;
    if (progressText) progressText.textContent = `已集 ${unlocked} / ${total} 枚`;

    grid.innerHTML = '';
    for (const b of manifest) {
      const ts = unlockedMap[b.pinyin];
      grid.appendChild(renderCard(b, Boolean(ts), ts));
    }
  }

  init();
})();
