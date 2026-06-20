/**
 * 每日一色挑战页
 */
(() => {
  const dateEl = document.getElementById('daily-date');
  const statusBadge = document.getElementById('daily-status-badge');
  const hintLine = document.getElementById('daily-hint-line');
  const hintSource = document.getElementById('daily-hint-source');
  const imageryEl = document.getElementById('daily-imagery');
  const donePanel = document.getElementById('daily-done-panel');
  const doneColor = document.getElementById('daily-done-color');
  const doneImg = document.getElementById('daily-done-img');
  const doneNote = document.getElementById('daily-done-note');
  const uploadSection = document.getElementById('daily-upload-section');
  const uploadZone = document.getElementById('daily-upload-zone');
  const fileInput = document.getElementById('daily-file-input');
  const previewImg = document.getElementById('daily-preview-img');
  const previewPlaceholder = document.getElementById('daily-preview-placeholder');
  const statusEl = document.getElementById('daily-status');
  const failColors = document.getElementById('daily-fail-colors');
  const successOverlay = document.getElementById('daily-success-overlay');
  const successImg = document.getElementById('daily-success-img');
  const successTitle = document.getElementById('daily-success-title');
  const successSub = document.getElementById('daily-success-sub');
  const successClose = document.getElementById('daily-success-close');

  let todayChallenge = null;

  function escapeHtml(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  function setStatus(text, loading = false) {
    statusEl.textContent = text;
    statusEl.classList.toggle('loading', loading);
    statusEl.hidden = !text;
  }

  function renderHint(challenge) {
    hintLine.textContent = challenge.hintLine ? `「${challenge.hintLine}」` : '今日意象待寻';
    hintSource.textContent = challenge.hintSource ? `— ${challenge.hintSource}` : '';
    imageryEl.textContent = challenge.imagery ? `画面意象：${challenge.imagery}` : '';
    dateEl.textContent = `${DailyChallenge.formatDisplayDate(challenge.dateKey)} · 第 ${challenge.dayIndex} 日`;
  }

  function showCompletedState(challenge, completion) {
    statusBadge.hidden = false;
    statusBadge.textContent = '已打卡';
    donePanel.hidden = false;
    uploadSection.hidden = true;

    doneColor.textContent = `今日之色 · ${challenge.name}`;
    doneImg.src = Achievements.assetUrl(challenge.file);
    doneImg.alt = `${challenge.name} 书签`;

    if (completion?.alreadyOwned) {
      doneNote.textContent = '此书签已在成就集藏中';
    } else {
      doneNote.textContent = '书签已入成就集藏';
    }
  }

  function showPendingState() {
    statusBadge.hidden = true;
    donePanel.hidden = true;
    uploadSection.hidden = false;
    failColors.hidden = true;
  }

  function renderFailColors(mapped) {
    if (!mapped?.length) {
      failColors.hidden = true;
      return;
    }
    const items = mapped.map((c) => {
      const pct = c.ratio != null ? `${Math.round(c.ratio * 100)}%` : '';
      return `<span class="daily-fail-chip"><span class="swatch" style="background:${escapeHtml(c.hex)}"></span>${escapeHtml(c.name)}${pct ? ` ${pct}` : ''}</span>`;
    }).join('');
    failColors.innerHTML = `<p class="daily-fail-label">图中前五主色：</p><div class="daily-fail-list">${items}</div>`;
    failColors.hidden = false;
  }

  function showSuccessOverlay(challenge, result) {
    successImg.src = Achievements.assetUrl(challenge.file);
    successImg.alt = `${challenge.name} 书签`;
    successImg.hidden = false;
    successTitle.textContent = `今日之色 · ${challenge.name}`;

    if (result.alreadyCompleted) {
      successSub.textContent = '今日已打卡';
    } else if (result.alreadyOwned) {
      successSub.textContent = '打卡成功 · 此书签已在成就集藏中';
    } else if (result.newlyUnlocked) {
      successSub.textContent = '打卡成功 · 书签已入成就集藏';
    } else {
      successSub.textContent = '打卡成功';
    }

    successOverlay.hidden = false;
    successOverlay.setAttribute('aria-hidden', 'false');
    document.body.classList.add('unlock-open');
    requestAnimationFrame(() => successOverlay.classList.add('unlock-visible'));
  }

  function hideSuccessOverlay() {
    successOverlay.classList.remove('unlock-visible');
    document.body.classList.remove('unlock-open');
    setTimeout(() => {
      successOverlay.hidden = true;
      successOverlay.setAttribute('aria-hidden', 'true');
      successImg.hidden = true;
    }, 320);
  }

  async function handleFile(file) {
    if (!file || !file.type.startsWith('image/')) return;

    setStatus('设色中…', true);
    failColors.hidden = true;

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
      const submit = await DailyChallenge.submitPhoto(mapped);

      if (submit.success) {
        setStatus('');
        showCompletedState(submit.challenge, DailyChallenge.getCompletion(submit.challenge.dateKey));
        if (!submit.alreadyCompleted) {
          showSuccessOverlay(submit.challenge, submit);
        }
      } else {
        setStatus('图中主色未识得今日之色，再寻一寻？');
        renderFailColors(submit.mapped);
      }
    } catch (err) {
      const msg = location.protocol === 'file:'
        ? '请通过本地服务器访问，不要直接双击 HTML'
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
  successClose?.addEventListener('click', hideSuccessOverlay);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !successOverlay.hidden) hideSuccessOverlay();
  });

  async function init() {
    try {
      await Promise.all([DailyChallenge.loadData(), Achievements.loadManifest()]);
    } catch {
      hintLine.textContent = '挑战数据加载失败，请刷新重试';
      return;
    }

    todayChallenge = DailyChallenge.getTodayChallenge();
    renderHint(todayChallenge);

    const completion = DailyChallenge.getCompletion(todayChallenge.dateKey);
    if (completion) {
      showCompletedState(todayChallenge, completion);
    } else {
      showPendingState();
    }
  }

  init();
})();
