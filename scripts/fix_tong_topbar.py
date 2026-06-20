#!/usr/bin/env python3
"""修复「彤」书签顶栏：单字色名放大，与双字色名视觉平衡。"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
NEW_DIR = ROOT / "assets" / "color-bookmarks" / "new"
OUT_PATH = NEW_DIR / "cbc79_彤.png"

W, H = 418, 1015
SPLIT_Y = 345
CIRCLE_CX, CIRCLE_CY = 208, 150
CIRCLE_R = 76
COLOR_RGB = (0xF3, 0x53, 0x36)
NAME_TEXT = "彤"
HEX_TEXT = "#F35336"
TEXT_COLOR = (25, 48, 70)
HEX_COLOR = (52, 65, 76)
NAME_Y = 268
HEX_Y = 318
NAME_FONT_SIZE = 56
HEX_FONT_SIZE = 30

FONT_CANDIDATES = [
    Path(r"C:\Windows\Fonts\STKAITI.TTF"),
    Path(r"C:\Windows\Fonts\simkai.ttf"),
]


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for fp in FONT_CANDIDATES:
        if fp.exists():
            try:
                return ImageFont.truetype(str(fp), size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def build_paper_header(art: Image.Image) -> Image.Image:
    paper = art.getpixel((25, 25))
    return Image.new("RGB", (W, SPLIT_Y), paper)


def main() -> None:
    art = Image.open(OUT_PATH).convert("RGB")
    if art.size != (W, H):
        art = art.resize((W, H), Image.Resampling.LANCZOS)

    header = build_paper_header(art)
    draw = ImageDraw.Draw(header)
    draw.ellipse(
        (CIRCLE_CX - CIRCLE_R, CIRCLE_CY - CIRCLE_R, CIRCLE_CX + CIRCLE_R, CIRCLE_CY + CIRCLE_R),
        fill=COLOR_RGB,
    )

    name_font = load_font(NAME_FONT_SIZE)
    hex_font = load_font(HEX_FONT_SIZE)
    draw.text((CIRCLE_CX, NAME_Y), NAME_TEXT, fill=TEXT_COLOR, font=name_font, anchor="mm")
    draw.text((CIRCLE_CX, HEX_Y), HEX_TEXT, fill=HEX_COLOR, font=hex_font, anchor="mm")

    out = Image.new("RGB", (W, H))
    out.paste(header, (0, 0))
    out.paste(art.crop((0, SPLIT_Y, W, H)), (0, SPLIT_Y))
    out.save(OUT_PATH, "PNG")
    print(f"已保存 → {OUT_PATH.name}（色名 {NAME_FONT_SIZE}px，色值 {HEX_FONT_SIZE}px）")


if __name__ == "__main__":
    main()
