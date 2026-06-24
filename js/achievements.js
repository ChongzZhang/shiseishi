/**
 * 成就书签 — 解锁检测与 localStorage 持久化
 */
const Achievements = (() => {
  const STORAGE_KEY = 'shiseishi-achievements-v1';
  const MANIFEST_URL = 'assets/color-bookmarks/new/manifest.json';
  const ASSET_BASE = 'assets/color-bookmarks/new/';

  let manifest = null;
  let manifestByPinyin = null;

  function loadStorage() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return { unlocked: {} };
      const data = JSON.parse(raw);
      return { unlocked: data.unlocked || {} };
    } catch {
      return { unlocked: {} };
    }
  }

  function saveStorage(data) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  }

  async function loadManifest() {
    if (manifest) return manifest;
    const res = await fetch(MANIFEST_URL, { cache: 'no-store' });
    if (!res.ok) throw new Error('书签清单加载失败');
    manifest = await res.json();
    manifestByPinyin = new Map(manifest.map((b) => [b.pinyin, b]));
    return manifest;
  }

  function getManifest() {
    return manifest || [];
  }

  function getBookmark(pinyin) {
    return manifestByPinyin?.get(pinyin) || null;
  }

  function assetUrl(file) {
    return ASSET_BASE + file;
  }

  function getUnlocked() {
    const { unlocked } = loadStorage();
    return Object.entries(unlocked)
      .map(([pinyin, ts]) => {
        const bookmark = getBookmark(pinyin);
        if (!bookmark) return null;
        return { ...bookmark, unlockedAt: ts };
      })
      .filter(Boolean)
      .sort((a, b) => b.unlockedAt - a.unlockedAt);
  }

  function isUnlocked(pinyin) {
    const { unlocked } = loadStorage();
    return Boolean(unlocked[pinyin]);
  }

  function unlock(pinyin) {
    const bookmark = getBookmark(pinyin);
    if (!bookmark) return null;

    const store = loadStorage();
    if (store.unlocked[pinyin]) return null;

    const ts = Date.now();
    store.unlocked[pinyin] = ts;
    saveStorage(store);
    return { ...bookmark, unlockedAt: ts };
  }

  function checkUnlocks(mappedColors) {
    if (!manifestByPinyin) return [];
    const newly = [];
    for (const c of mappedColors) {
      if (!manifestByPinyin.has(c.pinyin)) continue;
      const item = unlock(c.pinyin);
      if (item) newly.push(item);
    }
    return newly;
  }

  function getProgress() {
    const total = manifest?.length || 0;
    const { unlocked } = loadStorage();
    const count = manifest
      ? manifest.filter((b) => unlocked[b.pinyin]).length
      : Object.keys(unlocked).length;
    return { unlocked: count, total };
  }

  function formatDate(ts) {
    const d = new Date(ts);
    return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`;
  }

  return {
    loadManifest,
    getManifest,
    getBookmark,
    assetUrl,
    getUnlocked,
    isUnlocked,
    unlock,
    checkUnlocks,
    getProgress,
    formatDate,
  };
})();
