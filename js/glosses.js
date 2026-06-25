/**
 * 色名释义查询（内嵌于 glosses-data.js）
 */
const ColorGlosses = (() => {
  function get(pinyin) {
    if (typeof COLOR_GLOSSES === 'undefined' || !pinyin) return null;
    const gloss = COLOR_GLOSSES[pinyin];
    return gloss && String(gloss).trim() ? gloss : null;
  }

  return { get };
})();
