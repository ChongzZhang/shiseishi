/**
 * 逐像素 RGB → 中国传统色名（CIELAB ΔE76 最近邻），统计出现次数取前五
 */
const ColorMatch = (() => {
  let palette = null;
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

  /**
   * 对每个不透明像素找最近中国色，按出现次数取前五
   */
  function mapFromPixels(data, width, height) {
    const pal = loadPalette();
    const counts = new Map();
    let validPixels = 0;

    for (let i = 0; i < data.length; i += 4) {
      if (data[i + 3] < 128) continue;
      validPixels++;
      const rgb = [data[i], data[i + 1], data[i + 2]];
      const match = findNearest(rgb, pal);
      const entry = counts.get(match.pinyin);
      if (entry) {
        entry.count += 1;
      } else {
        counts.set(match.pinyin, {
          count: 1,
          name: match.name,
          pinyin: match.pinyin,
          hex: match.hex,
          rgb: match.rgb,
          deltaE: match.deltaE,
        });
      }
    }

    if (validPixels === 0) return [];

    return [...counts.values()]
      .sort((a, b) => b.count - a.count)
      .slice(0, TARGET_COUNT)
      .map(({ count, name, pinyin, hex, rgb, deltaE: de }) => ({
        rgb,
        ratio: count / validPixels,
        name,
        pinyin,
        hex,
        deltaE: de,
      }));
  }

  return { loadPalette, mapFromPixels };
})();
