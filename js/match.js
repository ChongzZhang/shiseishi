/**
 * 逐像素 RGB → 中国传统色名
 * - 高明度：降低 ΔL 权重，避免浅色坍缩为近白
 * - 色度加权：低饱和背景票数降低，突出有彩度的主色
 */
const ColorMatch = (() => {
  let palette = null;
  const TARGET_COUNT = 5;
  const CHROMA_BASE = 0.05;
  const CHROMA_REF = 35;
  const CHROMA_POWER = 1.3;

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

  function chroma(lab) {
    return Math.hypot(lab[1], lab[2]);
  }

  /** 高明度时降低亮度差权重，保留色相/色度区分 */
  function matchDistance(lab, plab) {
    const avgL = (lab[0] + plab[0]) / 2;
    let wL = 1;
    if (avgL > 70) wL = 0.15;
    else if (avgL > 50) wL = 0.5;
    const dL = lab[0] - plab[0];
    const da = lab[1] - plab[1];
    const db = lab[2] - plab[2];
    return Math.sqrt(wL * dL * dL + da * da + db * db);
  }

  function pixelWeight(lab) {
    const c = chroma(lab);
    return CHROMA_BASE + (c / CHROMA_REF) ** CHROMA_POWER;
  }

  function loadPalette() {
    if (palette) return palette;
    if (typeof COLOR_PALETTE !== 'undefined' && COLOR_PALETTE.length) {
      palette = COLOR_PALETTE;
      return palette;
    }
    throw new Error('色板未加载，请确认已引入 js/palette.js');
  }

  function findNearest(lab, pal) {
    let best = null;
    let bestD = Infinity;
    for (const c of pal) {
      const d = matchDistance(lab, c.lab);
      if (d < bestD) {
        bestD = d;
        best = c;
      }
    }
    return { ...best, deltaE: bestD };
  }

  function mapFromPixels(data, width, height) {
    const pal = loadPalette();
    const counts = new Map();
    let totalWeight = 0;

    for (let i = 0; i < data.length; i += 4) {
      if (data[i + 3] < 128) continue;
      const rgb = [data[i], data[i + 1], data[i + 2]];
      const lab = rgbToLab(rgb[0], rgb[1], rgb[2]);
      const w = pixelWeight(lab);
      const match = findNearest(lab, pal);
      totalWeight += w;

      const entry = counts.get(match.pinyin);
      if (entry) {
        entry.weight += w;
      } else {
        counts.set(match.pinyin, {
          weight: w,
          name: match.name,
          pinyin: match.pinyin,
          hex: match.hex,
          rgb: match.rgb,
          deltaE: match.deltaE,
        });
      }
    }

    if (totalWeight === 0) return [];

    return [...counts.values()]
      .sort((a, b) => b.weight - a.weight)
      .slice(0, TARGET_COUNT)
      .map(({ weight, name, pinyin, hex, rgb, deltaE: de }) => ({
        rgb,
        ratio: weight / totalWeight,
        name,
        pinyin,
        hex,
        deltaE: de,
      }));
  }

  return { loadPalette, mapFromPixels };
})();
