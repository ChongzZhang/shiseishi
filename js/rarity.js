/**
 * 稀有色稀有度 — 查表与 Top5 最稀有选取
 */
const ColorRarity = (() => {
  function table() {
    return typeof COLOR_RARITY !== 'undefined' ? COLOR_RARITY : null;
  }

  function getEntry(pinyin) {
    const t = table();
    if (!t || !pinyin) return null;
    return t[pinyin] || null;
  }

  function getScore(pinyin) {
    const entry = getEntry(pinyin);
    return entry ? entry.score : null;
  }

  function getVolume(pinyin) {
    const entry = getEntry(pinyin);
    return entry ? entry.volume : null;
  }

  /** 从识色 Top5 取稀有度最高者；并列取 volume 更小 */
  function pickRarest(colors) {
    if (!colors?.length) return null;
    const t = table();
    if (!t) return null;

    let best = null;
    let bestScore = -Infinity;
    let bestVolume = Infinity;

    for (const c of colors) {
      const entry = t[c.pinyin];
      if (!entry) continue;
      const { score, volume } = entry;
      if (
        score > bestScore
        || (score === bestScore && volume < bestVolume)
      ) {
        bestScore = score;
        bestVolume = volume;
        best = {
          ...c,
          rarityScore: score,
          rarityVolume: volume,
        };
      }
    }
    return best;
  }

  return { getScore, getVolume, getEntry, pickRarest };
})();
