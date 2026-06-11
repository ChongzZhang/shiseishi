/**
 * 用户手动编辑（localStorage，仅本机生效）
 */
const UserEdits = (() => {
  const STORAGE_KEY = 'shiseishi-user-edits';
  const TARGET = 5;

  function load() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return { hiddenColors: [], hiddenPoems: {}, addedPoems: {} };
      const data = JSON.parse(raw);
      return {
        hiddenColors: Array.isArray(data.hiddenColors) ? data.hiddenColors : [],
        hiddenPoems: data.hiddenPoems && typeof data.hiddenPoems === 'object' ? data.hiddenPoems : {},
        addedPoems: data.addedPoems && typeof data.addedPoems === 'object' ? data.addedPoems : {},
      };
    } catch {
      return { hiddenColors: [], hiddenPoems: {}, addedPoems: {} };
    }
  }

  function save(data) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  }

  function poemKey(entry) {
    if (entry.source) return entry.source;
    const line = (entry.line || '').replace(/\s/g, '');
    return `line:${line}`;
  }

  function isColorHidden(pinyin) {
    return load().hiddenColors.includes(pinyin);
  }

  function hideColor(pinyin) {
    const data = load();
    if (!data.hiddenColors.includes(pinyin)) {
      data.hiddenColors.push(pinyin);
      save(data);
    }
  }

  function hidePoem(pinyin, entryOrKey) {
    const key = typeof entryOrKey === 'string' ? entryOrKey : poemKey(entryOrKey);
    const data = load();
    if (!data.hiddenPoems[pinyin]) data.hiddenPoems[pinyin] = [];
    if (!data.hiddenPoems[pinyin].includes(key)) {
      data.hiddenPoems[pinyin].push(key);
      save(data);
    }
  }

  function addPoem(pinyin, { line, author, title }) {
    const text = (line || '').trim();
    if (!text) return null;
    const entry = {
      line: text,
      author: (author || '佚名').trim() || '佚名',
      title: (title || '自添').trim() || '自添',
      type: '诗',
      source: `user:${Date.now()}:${Math.random().toString(36).slice(2, 9)}`,
      matchTier: 0,
      verified: false,
      userAdded: true,
    };
    const data = load();
    if (!data.addedPoems[pinyin]) data.addedPoems[pinyin] = [];
    data.addedPoems[pinyin].push(entry);
    save(data);
    return entry;
  }

  function mergePoetry(data) {
    if (!data) return data;
    const store = load();
    const pinyin = data.pinyin;
    const hidden = new Set(store.hiddenPoems[pinyin] || []);
    const lib = (data.entries || []).filter((e) => !hidden.has(poemKey(e)));
    const added = (store.addedPoems[pinyin] || []).filter((e) => !hidden.has(poemKey(e)));
    const entries = [...lib, ...added];
    return {
      ...data,
      entries,
      coverage: `${entries.length}/${TARGET}`,
    };
  }

  function hasPoems(pinyin, rawData) {
    const base = rawData || { pinyin, entries: [] };
    return mergePoetry(base).entries.length > 0;
  }

  function counts() {
    const data = load();
    const hiddenPoemCount = Object.values(data.hiddenPoems).reduce((n, arr) => n + arr.length, 0);
    const addedPoemCount = Object.values(data.addedPoems).reduce((n, arr) => n + arr.length, 0);
    return { colors: data.hiddenColors.length, hiddenPoems: hiddenPoemCount, addedPoems: addedPoemCount };
  }

  function reset() {
    localStorage.removeItem(STORAGE_KEY);
  }

  return {
    isColorHidden,
    hideColor,
    hidePoem,
    addPoem,
    poemKey,
    mergePoetry,
    filterPoetry: mergePoetry,
    hasPoems,
    counts,
    reset,
  };
})();
