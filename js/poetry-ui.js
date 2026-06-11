/**
 * 诗句面板渲染（主站 / 浏览页共用）
 */
const PoetryUI = (() => {
  function escapeHtml(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  function dynastyLabel(e) {
    const d = (e.dynasty || '').trim();
    return d ? `<span class="poetry-dynasty">${escapeHtml(d)}</span>` : '';
  }

  function renderEntry(e) {
    const dynasty = dynastyLabel(e);
    return `
      <blockquote class="poetry-item">
        <div class="poetry-item-row">
          <p class="poetry-line">${escapeHtml(e.line)}</p>
        </div>
        <footer class="poetry-meta">
          ${dynasty}
          <span class="poetry-author">${escapeHtml(e.author)}</span>
          <cite>${escapeHtml(e.title)}</cite>
        </footer>
      </blockquote>`;
  }

  function renderList(data) {
    if (!data?.entries?.length) {
      return '<p class="poetry-empty">暂无诗句</p>';
    }
    const items = data.entries.map(renderEntry).join('');
    return `${items}<p class="poetry-coverage">共 ${data.coverage} 条</p>`;
  }

  function renderPanel(data, pinyin) {
    return renderList(data);
  }

  function mountPanel(container, pinyin, getMergedData) {
    const data = getMergedData();
    container.innerHTML = renderPanel(data, pinyin);
  }

  return { renderPanel, renderList, mountPanel, escapeHtml };
})();
