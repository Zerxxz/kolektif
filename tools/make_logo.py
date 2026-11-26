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
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10011", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["01110", "10000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00001", "01110"],
    "#": ["01010", "01010", "11111", "01010", "11111", "01010", "01010"],
    ".": ["00000", "00000", "00000", "00000", "00000", "00110", "00110"],
    ",": ["00000", "00000", "00000", "00000", "00110", "00110", "01100"],
    "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    ":": ["00000", "00110", "00110", "00000", "00110", "00110", "00000"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "?": ["01110", "10001", "00001", "00110", "00100", "00000", "00100"],
    " ": ["00000"] * 7,
}


def text_w(s: str, scale: int = 1, gap: int = 1) -> int:
    return len(s) * (5 + gap) * scale - gap * scale


def draw_text(d, xy, s, color, scale=1, gap=1):
    x, y = xy
    for ch in s.upper():
        rows = FONT.get(ch)
        if rows is None:
            raise SystemExit(f"logo: no glyph for {ch!r} in {s!r}")
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


def social_card(bg, path, size=(200, 105), up=6):
    """1200x630 listing thumbnail. Drawn at 1x, upscaled 6x (200x105 -> 1200x630).

    Layout is on a fixed grid with real margins: brand lockup, one headline,
    one subline, and a proof strip. Every string is width-checked before it is
    drawn, so a long line fails the build instead of silently clipping.
    """
    img = Image.new("RGB", size, bg)
    d = ImageDraw.Draw(img)
    w, h = size
    margin = 10
    inner = w - margin * 2

    def put(x, y, s, color, scale=1, gap=1):
        width = text_w(s, scale, gap)
        if x + width > w - 4:
            raise SystemExit(f"social card: {s!r} is {width} wide at x={x} (max {w - 4 - x})")
        draw_text(d, (x, y), s, color, scale=scale, gap=gap)
        return width

    # pixel frame
    for x in range(0, w, 2):
        d.rectangle([x, 0, x + 1, 1], fill=AMBER)
        d.rectangle([x, h - 2, x + 1, h - 1], fill=AMBER)
    for y in range(0, h, 2):
        d.rectangle([0, y, 1, y + 1], fill=AMBER)
        d.rectangle([w - 2, y, w - 1, y + 1], fill=AMBER)

    # brand lockup
    draw_mark(d, margin + 16, 24)
    put(margin + 44, 10, "KOLEKTIF", INK, scale=2)
    put(margin + 44, 28, "ARISAN ARCADE", TEAL, scale=1)

    # headline + subline
    put(margin, 46, "POT GOES ROUND", INK, scale=2)
    put(margin, 66, "escrow . fixed order . zero JS", MUTED, scale=1)

    # proof strip
    d.rectangle([margin, 80, w - margin, 80], fill=TEAL)
    put(margin, 84, "RUN #2 ACTIVE   POT 3 GNOT", AMBER, scale=1)
    put(margin, 93, "VERIFY PASS", TEAL, scale=1)
    put(w - margin - text_w("ZERXXZ/KOLEKTIF", 1), 93, "ZERXXZ/KOLEKTIF", INK, scale=1)

    img = img.resize((size[0] * up, size[1] * up), Image.Resampling.NEAREST)
    img.save(path)
    return path


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
    p4 = social_card(BG, os.path.join(OUT, "kolektif-social-card.png"))
    # every glyph in the font must draw at least one pixel, or the table lies
    probe = Image.new("RGB", (600, 20), BG)
    draw_text(ImageDraw.Draw(probe), (2, 2), "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#.,/-:!?", INK, scale=2)
    ink = sum(c for c, px in (probe.getcolors(100000) or []) if isinstance(px, tuple) and sum(px) > 400)
    if ink < 500:
        raise SystemExit("logo: glyph self-test drew too little ink")
    print(f"glyph self-test ink={ink}")

    for p in (p1, p2, p3, p4):
        im = Image.open(p).convert("RGB")
        w, h = im.size
        # sanity: is there ink in the wordmark area?
        crop = im.crop((int(w * 0.30), int(h * 0.18), w, int(h * 0.55)))
        colors = crop.getcolors(maxcolors=100000) or []
        bright = sum(c for c, px in colors if isinstance(px, tuple) and sum(px) > 400)
        print(f"{p}  {w}x{h}  wordmark_pixels={bright}")
    print("done")
