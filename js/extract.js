/**
 * Canvas 取色：过滤中性背景，合并相近色，返回差异明显的 Top5 RGB
 */
const ColorExtract = (() => {
  const MAX_SIZE = 512;
  const SAT_MIN = 0.08;
  const LUM_MAX = 0.95;
  const LUM_MIN = 0.05;
  const QUANT_BITS = 5;
  const MERGE_DELTA = 22;
  const MIN_SEPARATION = 28;
  const TARGET_COUNT = 5;
  const CLUSTER_EXPORT = 20;

  function rgbToHsl(r, g, b) {
    r /= 255; g /= 255; b /= 255;
    const max = Math.max(r, g, b), min = Math.min(r, g, b);
    let h, s, l = (max + min) / 2;
    if (max === min) {
      h = s = 0;
    } else {
      const d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      switch (max) {
        case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
        case g: h = ((b - r) / d + 2) / 6; break;
        default: h = ((r - g) / d + 4) / 6;
      }
    }
    return { h, s, l };
  }

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

  function quantize(v) {
    const shift = 8 - QUANT_BITS;
    return (v >> shift) << shift;
  }

  function loadImage(file) {
    return new Promise((resolve, reject) => {
      const url = URL.createObjectURL(file);
      const img = new Image();
      img.onload = () => {
        URL.revokeObjectURL(url);
        resolve(img);
      };
      img.onerror = () => {
        URL.revokeObjectURL(url);
        reject(new Error('图片加载失败'));
      };
      img.src = url;
    });
  }

  /** 合并相近色簇，保留各簇像素量最大的代表色 */
  function clusterColors(entries) {
    const clusters = [];
    for (const item of entries) {
      const lab = rgbToLab(item.rgb[0], item.rgb[1], item.rgb[2]);
      let bestCluster = null;
      let bestD = Infinity;
      for (const cluster of clusters) {
        const d = deltaE(lab, cluster.lab);
        if (d < MERGE_DELTA && d < bestD) {
          bestD = d;
          bestCluster = cluster;
        }
      }
      if (bestCluster) {
        bestCluster.count += item.count;
        if (item.count > bestCluster.peakCount) {
          bestCluster.peakCount = item.count;
          bestCluster.rgb = item.rgb;
          bestCluster.lab = lab;
        }
      } else {
        clusters.push({
          rgb: item.rgb,
          count: item.count,
          peakCount: item.count,
          lab,
        });
      }
    }
    return clusters.sort((a, b) => b.count - a.count);
  }

  /** 从簇中贪心选取差异明显的前 N 色 */
  function pickDiverse(clusters, n = TARGET_COUNT) {
    const picked = [];
    for (const c of clusters) {
      if (picked.length >= n) break;
      const tooClose = picked.some((p) => deltaE(c.lab, p.lab) < MIN_SEPARATION);
      if (!tooClose) picked.push(c);
    }
    if (picked.length < n) {
      for (const c of clusters) {
        if (picked.length >= n) break;
        if (picked.some((p) => p.rgb.join() === c.rgb.join())) continue;
        const tooClose = picked.some((p) => deltaE(c.lab, p.lab) < MIN_SEPARATION * 0.65);
        if (!tooClose) picked.push(c);
      }
    }
    if (picked.length < n) {
      for (const c of clusters) {
        if (picked.length >= n) break;
        if (!picked.some((p) => p.rgb.join() === c.rgb.join())) picked.push(c);
      }
    }
    return picked.slice(0, n);
  }

  function buildResult(counts, validPixels, previewUrl) {
    if (validPixels === 0) {
      return { colors: [], previewUrl, validPixels: 0 };
    }
    const entries = [...counts.entries()]
      .sort((a, b) => b[1] - a[1])
      .map(([key, count]) => {
        const [r, g, b] = key.split(',').map(Number);
        return { rgb: [r, g, b], count };
      });
    const clusters = clusterColors(entries);
    const top = clusters.slice(0, CLUSTER_EXPORT);
    const colors = top.map((c) => ({
      rgb: c.rgb,
      count: c.count,
      ratio: c.count / validPixels,
    }));
    return { colors, previewUrl, validPixels };
  }

  function scanPixels(data, filterFn) {
    const counts = new Map();
    let validPixels = 0;
    for (let i = 0; i < data.length; i += 4) {
      if (data[i + 3] < 128) continue;
      const r = data[i], g = data[i + 1], b = data[i + 2];
      if (!filterFn(r, g, b)) continue;
      const qr = quantize(r), qg = quantize(g), qb = quantize(b);
      const key = `${qr},${qg},${qb}`;
      counts.set(key, (counts.get(key) || 0) + 1);
      validPixels++;
    }
    return { counts, validPixels };
  }

  function extractFromImage(img, filterFn) {
    const scale = Math.min(1, MAX_SIZE / Math.max(img.width, img.height));
    const w = Math.max(1, Math.round(img.width * scale));
    const h = Math.max(1, Math.round(img.height * scale));
    const canvas = document.createElement('canvas');
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    ctx.drawImage(img, 0, 0, w, h);
    const { data } = ctx.getImageData(0, 0, w, h);
    const previewUrl = canvas.toDataURL('image/jpeg', 0.85);
    const { counts, validPixels } = scanPixels(data, filterFn);
    return buildResult(counts, validPixels, previewUrl);
  }

  function extractTopColors(file) {
    return loadImage(file).then((img) =>
      extractFromImage(img, (r, g, b) => {
        const { s, l } = rgbToHsl(r, g, b);
        return s >= SAT_MIN && l <= LUM_MAX && l >= LUM_MIN;
      })
    );
  }

  function extractTopColorsRelaxed(file) {
    return loadImage(file).then((img) =>
      extractFromImage(img, (r, g, b) => {
        const { s, l } = rgbToHsl(r, g, b);
        return !(s < 0.04 && (l > 0.97 || l < 0.03));
      })
    );
  }

  function extractWithFallback(file) {
    return extractTopColors(file).then((result) => {
      if (result.validPixels > 0) return result;
      return extractTopColorsRelaxed(file);
    });
  }

  return { extractTopColors: extractWithFallback };
})();
