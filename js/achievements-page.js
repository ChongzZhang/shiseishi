/**
 * 成就书签页 — 网格展示与下载
 */
(() => {
  const grid = document.getElementById('ach-grid');
  const progressFill = document.getElementById('ach-progress-fill');
  const progressText = document.getElementById('ach-progress-text');

  function escapeHtml(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  function renderCard(bookmark, unlocked, unlockedAt) {
    const card = document.createElement('article');
    card.className = `ach-card${unlocked ? ' ach-card-unlocked' : ' ach-card-locked'}`;

    const imgSrc = Achievements.assetUrl(bookmark.file);
    const dateStr = unlockedAt ? Achievements.formatDate(unlockedAt) : '';

    if (unlocked) {
      card.innerHTML = `
        <div class="ach-card-img-wrap">
          <img class="ach-card-img" src="${escapeHtml(imgSrc)}" alt="${escapeHtml(bookmark.name)} 书签" loading="lazy">
        </div>
        <div class="ach-card-info">
          <span class="ach-swatch" style="background:${escapeHtml(bookmark.hex)}"></span>
          <span class="ach-card-name">${escapeHtml(bookmark.name)}</span>
          <span class="ach-card-date">${escapeHtml(dateStr)}</span>
        </div>
        <a class="ach-download-btn" href="${escapeHtml(imgSrc)}" download="${escapeHtml(bookmark.file)}" aria-label="下载 ${escapeHtml(bookmark.name)} 书签">下载书签</a>
      `;
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
