#!/usr/bin/env python3
"""Monte Carlo 估算 RGB 立方体中各色 Voronoi 体积占比，生成稀有度分。"""

import json
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
COLORS_PATH = SCRIPT_DIR / "../data/colors.json"
OUT_JS = SCRIPT_DIR / "../js/rarity-data.js"
OUT_REPORT = SCRIPT_DIR / "../data/rarity_report.json"

SAMPLES = 2_000_000
CHUNK = 200_000


def rgb_to_lab(r, g, b):
  """sRGB -> CIELAB，与 gen_palette.py / match.js 一致。"""
  def lin(c):
    c = np.asarray(c, dtype=np.float64) / 255.0
    return np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)

  rr, gg, bb = lin(r), lin(g), lin(b)
  x = (rr * 0.4124 + gg * 0.3576 + bb * 0.1805) * 100
  y = (rr * 0.2126 + gg * 0.7152 + bb * 0.0722) * 100
  z = (rr * 0.0193 + gg * 0.1192 + bb * 0.9505) * 100

  def f(t):
    return np.where(t > 0.008856, np.cbrt(t), (7.787 * t) + (16 / 116))

  fx, fy, fz = f(x / 95.047), f(y / 100), f(z / 108.883)
  L = (116 * fy) - 16
  a = 500 * (fx - fy)
  b_star = 200 * (fy - fz)
  return np.stack([L, a, b_star], axis=-1)


def load_palette():
  colors = json.loads(COLORS_PATH.read_text(encoding="utf-8"))
  seen = set()
  palette = []
  for c in colors:
    key = c["pinyin"]
    if key in seen:
      continue
    seen.add(key)
    r, g, b = c["RGB"]
    palette.append({
      "name": c["name"],
      "pinyin": key,
      "hex": c["hex"],
      "rgb": c["RGB"],
    })
  labs = np.array([rgb_to_lab(r, g, b) for r, g, b in (p["rgb"] for p in palette)], dtype=np.float64)
  return palette, labs


def match_distance_batch(sample_lab, pal_labs):
  """向量化 matchDistance，与 match.js 一致。"""
  diff = sample_lab[:, None, :] - pal_labs[None, :, :]
  avg_l = (sample_lab[:, None, 0] + pal_labs[None, :, 0]) / 2
  w_l = np.where(avg_l > 70, 0.15, np.where(avg_l > 50, 0.5, 1.0))
  d_l = diff[:, :, 0]
  d_a = diff[:, :, 1]
  d_b = diff[:, :, 2]
  dist = np.sqrt(w_l * d_l * d_l + d_a * d_a + d_b * d_b)
  return np.argmin(dist, axis=1)


def monte_carlo_counts(pal_labs, n_samples):
  counts = np.zeros(len(pal_labs), dtype=np.int64)
  remaining = n_samples
  while remaining > 0:
    batch = min(CHUNK, remaining)
    rgb = np.random.randint(0, 256, size=(batch, 3), dtype=np.int32)
    lab = rgb_to_lab(rgb[:, 0], rgb[:, 1], rgb[:, 2])
    nearest = match_distance_batch(lab, pal_labs)
    np.add.at(counts, nearest, 1)
    remaining -= batch
  return counts


def volume_to_scores(volumes):
  """按 volume 升序百分位映射：最稀有 100，最常见 1。并列 volume 共享 score。"""
  n = len(volumes)
  if n <= 1:
    return [100] if n == 1 else []

  order = np.argsort(volumes, kind="stable")
  ranks = np.empty(n, dtype=np.int64)
  ranks[order] = np.arange(n)

  # 并列：取组内最高 rank（更稀有）
  sorted_vols = volumes[order]
  group_rank = ranks.copy()
  i = 0
  while i < n:
    j = i
    while j + 1 < n and sorted_vols[j + 1] == sorted_vols[i]:
      j += 1
    best_rank = min(ranks[order[i : j + 1]])
    for k in range(i, j + 1):
      group_rank[order[k]] = best_rank
    i = j + 1

  scores = np.round(1 + 99 * (n - 1 - group_rank) / (n - 1)).astype(int)
  return scores.tolist()


def main():
  palette, pal_labs = load_palette()
  print(f"色板 {len(palette)} 色，Monte Carlo N={SAMPLES:,}…")
  counts = monte_carlo_counts(pal_labs, SAMPLES)
  volumes = counts.astype(np.float64) / SAMPLES

  scores = volume_to_scores(volumes)
  rarity_map = {}
  report = []

  order = np.argsort(volumes)
  for rank, idx in enumerate(order):
    p = palette[idx]
    entry = {
      "volume": round(float(volumes[idx]), 8),
      "score": int(scores[idx]),
    }
    rarity_map[p["pinyin"]] = entry
    report.append({
      "rank": rank,
      "name": p["name"],
      "pinyin": p["pinyin"],
      "hex": p["hex"],
      **entry,
    })

  OUT_JS.write_text(
    "\n".join([
      "/** 自动生成 — 运行 scripts/gen_rarity.py 更新 */",
      f"const COLOR_RARITY = {json.dumps(rarity_map, ensure_ascii=False, separators=(',', ':'))};",
      "",
    ]),
    encoding="utf-8",
  )
  OUT_REPORT.write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
  )

  total = float(volumes.sum())
  top = report[-3:]
  bottom = report[:3]
  print(f"写入 {OUT_JS.name}、{OUT_REPORT.name}")
  print(f"体积总和 ≈ {total:.6f}")
  print("最常见:", ", ".join(f"{x['name']}({x['score']})" for x in top))
  print("最稀有:", ", ".join(f"{x['name']}({x['score']})" for x in bottom))


if __name__ == "__main__":
  main()
