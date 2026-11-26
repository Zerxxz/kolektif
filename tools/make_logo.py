#!/usr/bin/env python3
"""Kolektif — pixel logo generator (v2).

Everything is drawn at 1x on a small canvas and upscaled with NEAREST, so the
edges stay hard and read as pixel art. The mark is a stack of coins (the pot a
ROSCA rotates) inside two rotation arrows; the wordmark sits to the right.
"""
from __future__ import annotations

import math
import os
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "brand")

BG = (15, 18, 32)
INK = (240, 242, 255)
AMBER = (255, 181, 71)
AMBER_DARK = (196, 122, 36)
TEAL = (94, 234, 212)
MUTED = (126, 138, 172)

FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    " ": ["00000"] * 7,
}


def text_w(s: str, scale: int = 1, gap: int = 1) -> int:
    return len(s) * (5 + gap) * scale - gap * scale


def draw_text(d, xy, s, color, scale=1, gap=1):
    x, y = xy
    for ch in s.upper():
        rows = FONT.get(ch)
        if rows:
            for ry, row in enumerate(rows):
                for rx, cell in enumerate(row):
                    if cell == "1":
                        d.rectangle([x + rx * scale, y + ry * scale,
                                     x + rx * scale + scale - 1, y + ry * scale + scale - 1], fill=color)
        x += (5 + gap) * scale


def disc(d, cx, cy, rx, ry, face, edge):
    """One coin: ellipse with a darker bottom half, drawn aliased on purpose."""
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=face)
    d.arc([cx - rx, cy - ry, cx + rx, cy + ry], 0, 180, fill=edge)
    d.arc([cx - rx + 1, cy - ry + 1, cx + rx - 1, cy + ry - 1], 0, 180, fill=edge)


def arc_arrow(d, cx, cy, r, start, end, color):
    for deg in range(start, end, 2):
        a = math.radians(deg)
        x = cx + int(round(r * math.cos(a)))
        y = cy + int(round(r * math.sin(a)))
        d.rectangle([x, y, x + 2, y + 2], fill=color)


def draw_mark(d, cx, cy):
    # rotation arrows: one over the top-left, one under the bottom-right
    arc_arrow(d, cx, cy, 20, 200, 320, TEAL)
    arc_arrow(d, cx, cy, 20, 20, 140, TEAL)
    # arrow heads
    d.rectangle([cx - 23, cy - 14, cx - 16, cy - 8], fill=TEAL)
    d.rectangle([cx + 16, cy + 8, cx + 23, cy + 14], fill=TEAL)
    # coin stack: three discs, bottom first
    disc(d, cx, cy + 8, 14, 5, AMBER_DARK, (150, 88, 24))
    disc(d, cx, cy + 3, 14, 5, AMBER, AMBER_DARK)
    disc(d, cx, cy - 2, 14, 5, AMBER, AMBER_DARK)
    # top face + monogram
    d.ellipse([cx - 14, cy - 9, cx + 14, cy + 1], fill=(255, 214, 138))
    draw_text(d, (cx - 7, cy - 8), "K", BG, scale=1, gap=1)


def logo(bg, path, size=(200, 64), up=8, wordmark=True):
    img = Image.new("RGB", size, bg)
    d = ImageDraw.Draw(img)
    draw_mark(d, 26, 30)
    if wordmark:
        draw_text(d, (62, 16), "KOLEKTIF", INK, scale=3, gap=1)
        draw_text(d, (62, 44), "ARISAN ARCADE", TEAL, scale=2, gap=1)
    img = img.resize((size[0] * up, size[1] * up), Image.Resampling.NEAREST)
    img.save(path)
    return path


def mark(bg, path, size=72, up=8):
    img = Image.new("RGB", (size, size), bg)
    d = ImageDraw.Draw(img)
    draw_mark(d, size // 2, size // 2)
    img = img.resize((size * up, size * up), Image.Resampling.NEAREST)
    img.save(path)
    return path


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    p1 = logo(BG, os.path.join(OUT, "kolektif-logo.png"))
    p2 = logo((0, 0, 0), os.path.join(OUT, "kolektif-logo-dark.png"))
    p3 = mark(BG, os.path.join(OUT, "kolektif-mark.png"))
    for p in (p1, p2, p3):
        im = Image.open(p).convert("RGB")
        w, h = im.size
        # sanity: is there ink in the wordmark area?
        crop = im.crop((int(w * 0.30), int(h * 0.18), w, int(h * 0.55)))
        colors = crop.getcolors(maxcolors=100000) or []
        bright = sum(c for c, px in colors if isinstance(px, tuple) and sum(px) > 400)
        print(f"{p}  {w}x{h}  wordmark_pixels={bright}")
    print("done")
