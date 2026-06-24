/**
 * 每日一色挑战 — 选题、打卡、与成就联动
 */
const DailyChallenge = (() => {
  const STORAGE_KEY = 'shiseishi-daily-v1';
  const DATA_URL = 'assets/color-bookmarks/daily-challenges.json';

  let data = null;
  let colors = null;

  function loadStorage() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return { completions: {} };
      const parsed = JSON.parse(raw);
      return { completions: parsed.completions || {} };
    } catch {
      return { completions: {} };
    }
  }

  function saveStorage(store) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
  }

  async function loadData() {
    if (data) return data;
    const res = await fetch(DATA_URL, { cache: 'no-store' });
    if (!res.ok) throw new Error('每日挑战数据加载失败');
    data = await res.json();
    colors = data.colors || [];
    return data;
  }

  /** 北京时间日期键 YYYY-MM-DD */
  function getDateKey(date = new Date()) {
    return new Intl.DateTimeFormat('en-CA', {
      timeZone: data?.timezone || 'Asia/Shanghai',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    }).format(date);
  }

  function formatDisplayDate(dateKey) {
    const [y, m, d] = dateKey.split('-').map(Number);
    return `${y}年${m}月${d}日`;
  }

  function daysSinceEpoch(dateKey) {
    const epoch = data?.epoch || '2026-01-01';
    const a = new Date(`${dateKey}T12:00:00+08:00`);
    const b = new Date(`${epoch}T12:00:00+08:00`);
    return Math.floor((a - b) / 86400000);
  }

  function getTodayChallenge() {
    if (!colors?.length) return null;
    const dateKey = getDateKey();
    const dayIndex = daysSinceEpoch(dateKey);
    const idx = ((dayIndex % colors.length) + colors.length) % colors.length;
    return { ...colors[idx], dateKey, dayIndex: dayIndex + 1 };
  }

  function getCompletion(dateKey) {
    const { completions } = loadStorage();
    return completions[dateKey] || null;
  }

  function isTodayCompleted() {
    const today = getTodayChallenge();
    if (!today) return false;
    return Boolean(getCompletion(today.dateKey));
  }

  function markComplete(challenge, alreadyOwned) {
    const store = loadStorage();
    store.completions[challenge.dateKey] = {
      pinyin: challenge.pinyin,
      ts: Date.now(),
      alreadyOwned,
    };
    saveStorage(store);
  }

  /**
   * 判定上传结果是否命中今日色（前五主色含目标 pinyin）
   * @returns {{ success, alreadyCompleted, newlyUnlocked, alreadyOwned, mapped }}
   */
  async function submitPhoto(mappedColors) {
    const challenge = getTodayChallenge();
    if (!challenge) throw new Error('今日挑战未就绪');

    const existing = getCompletion(challenge.dateKey);
    if (existing) {
      return {
        success: true,
        alreadyCompleted: true,
        challenge,
        mapped: mappedColors,
        alreadyOwned: existing.alreadyOwned,
        newlyUnlocked: false,
      };
    }

    const hit = mappedColors.some((c) => c.pinyin === challenge.pinyin);
    if (!hit) {
      return { success: false, challenge, mapped: mappedColors };
    }

    const wasOwned = Achievements.isUnlocked(challenge.pinyin);
    const unlocked = Achievements.unlock(challenge.pinyin);
    markComplete(challenge, wasOwned);

    return {
      success: true,
      alreadyCompleted: false,
      challenge,
      mapped: mappedColors,
      alreadyOwned: wasOwned,
      newlyUnlocked: Boolean(unlocked),
    };
  }

  function getStatusLabel() {
    if (isTodayCompleted()) return '今日已打卡';
    return '今日待寻色';
  }

  return {
    loadData,
    getDateKey,
    formatDisplayDate,
    getTodayChallenge,
    getCompletion,
    isTodayCompleted,
    submitPhoto,
    getStatusLabel,
  };
})();
