/**
 * RGB → 中国传统色名（CIELAB ΔE76 最近邻）
 * 相近色名合并，输出差异明显的 5 色
 */
const ColorMatch = (() => {
  let palette = null;
  const MERGE_DELTA = 20;
  const MIN_SEPARATION = 25;
  const TARGET_COUNT = 5;

  function rgbToLab(r, g, b) {
    const lin = (c) => {
      c /= 255;
      return c > 0.04045 ? ((c + 0.055) / 1.055) ** 2.4 : c / 12.92;
    };
    const rr = lin(r), gg = lin(g), bb = lin(b);
    const x = (rr * 0.4124 + gg * 0.3576 + bb * 0.1805) * 100;
    const y = (rr * 0.2126 + gg * 0.7152 + bb * 0.0722) * 100;
    const z = (rr * 0.0193 + gg * 0.1192 + bb * 0.9505) * 100;
    const f = (t) => (t > 0.008856 ? Math.cbrt(t) : (7.787 * t) + 16 / 116);
    const fx = f(x / 95.047), fy = f(y / 100), fz = f(z / 108.883);
    return [(116 * fy) - 16, 500 * (fx - fy), 200 * (fy - fz)];
  }

  function deltaE(l1, l2) {
    return Math.sqrt(
      (l1[0] - l2[0]) ** 2 + (l1[1] - l2[1]) ** 2 + (l1[2] - l2[2]) ** 2
    );
  }

  function loadPalette() {
    if (palette) return palette;
    if (typeof COLOR_PALETTE !== 'undefined' && COLOR_PALETTE.length) {
      palette = COLOR_PALETTE;
      return palette;
    }
    throw new Error('色板未加载，请确认已引入 js/palette.js');
  }

  function findNearest(rgb, pal) {
    const lab = rgbToLab(rgb[0], rgb[1], rgb[2]);
    let best = null;
    let bestD = Infinity;
    for (const c of pal) {
      const d = deltaE(lab, c.lab);
      if (d < bestD) {
        bestD = d;
        best = c;
      }
    }
    return { ...best, deltaE: bestD };
  }

  function dedupeAndPickDiverse(mapped) {
    const sorted = [...mapped].sort((a, b) => b.ratio - a.ratio);
    const clusters = [];

    for (const m of sorted) {
      const lab = m.paletteLab;
      let target = null;
      let bestD = Infinity;
      for (const cluster of clusters) {
        const d = deltaE(lab, cluster.paletteLab);
        if ((d < MERGE_DELTA || cluster.pinyin === m.pinyin) && d < bestD) {
          bestD = d;
          target = cluster;
        }
      }
      if (target) {
        target.ratio += m.ratio;
        if (m.ratio > target.peakRatio) {
          target.peakRatio = m.ratio;
          target.rgb = m.rgb;
          target.name = m.name;
          target.pinyin = m.pinyin;
          target.hex = m.hex;
          target.paletteLab = m.paletteLab;
        }
        target.merged = true;
      } else {
        clusters.push({ ...m, peakRatio: m.ratio, merged: false });
      }
    }

    clusters.sort((a, b) => b.ratio - a.ratio);

    const picked = [];
    for (const c of clusters) {
      if (picked.length >= TARGET_COUNT) break;
      const tooClose = picked.some((p) => {
        const d = deltaE(c.paletteLab, p.paletteLab);
        return d < MIN_SEPARATION || c.pinyin === p.pinyin;
      });
      if (!tooClose) picked.push(c);
    }
    if (picked.length < TARGET_COUNT) {
      for (const c of clusters) {
        if (picked.length >= TARGET_COUNT) break;
        if (picked.some((p) => p.pinyin === c.pinyin)) continue;
        const tooClose = picked.some((p) => deltaE(c.paletteLab, p.paletteLab) < MIN_SEPARATION * 0.6);
        if (!tooClose) picked.push(c);
      }
    }
    if (picked.length < TARGET_COUNT) {
      for (const c of clusters) {
        if (picked.length >= TARGET_COUNT) break;
        if (!picked.some((p) => p.pinyin === c.pinyin)) picked.push(c);
      }
    }

    return picked.slice(0, TARGET_COUNT).map(({ rgb, ratio, name, pinyin, hex, deltaE: de, merged }) => ({
      rgb, ratio, name, pinyin, hex, deltaE: de, merged,
    }));
  }

  async function mapColors(extracted) {
    const pal = loadPalette();
    const mapped = extracted.map((item) => {
      const match = findNearest(item.rgb, pal);
      return {
        rgb: item.rgb,
        ratio: item.ratio,
        name: match.name,
        pinyin: match.pinyin,
        hex: match.hex,
        deltaE: match.deltaE,
        paletteLab: match.lab,
      };
    });

    return dedupeAndPickDiverse(mapped);
  }

  return { loadPalette, mapColors };
})();
