"""angular glyph sheets (white on black) used as engraved / burning runes through box projection"""
from PIL import Image, ImageDraw, ImageFilter
import random, sys


def glyph(d, x, y, s, rng, w):
    # a glyph = a stem plus 2-4 angular strokes, all snapped to a small grid (reads as runic, not latin)
    g = lambda u, v: (x + u * s, y + v * s)
    d.line([g(0.5, 0.05), g(0.5, 0.95)], fill=255, width=w)
    for _ in range(rng.randint(2, 4)):
        kind = rng.random()
        if kind < 0.35:
            a = rng.choice([0.15, 0.35, 0.55]); b = a + rng.choice([0.2, 0.3])
            side = rng.choice([0.1, 0.9])
            d.line([g(0.5, a), g(side, b)], fill=255, width=w)
        elif kind < 0.6:
            a = rng.choice([0.2, 0.5, 0.75])
            d.line([g(0.15, a), g(0.85, a + rng.choice([-0.15, 0, 0.15]))], fill=255, width=w)
        elif kind < 0.8:
            a = rng.choice([0.2, 0.45]); h = 0.25
            side = rng.choice([0.15, 0.85])
            d.line([g(0.5, a), g(side, a + h / 2), g(0.5, a + h)], fill=255, width=w, joint="curve")
        else:
            a = rng.choice([0.3, 0.6])
            d.line([g(0.2, a - 0.15), g(0.8, a + 0.15)], fill=255, width=w)
            d.line([g(0.8, a - 0.15), g(0.2, a + 0.15)], fill=255, width=w)


def sheet(path, seed=1, res=1024, rows=6, cols=10, w=9, blur=1.2, border=True):
    rng = random.Random(seed)
    im = Image.new("L", (res, res), 0); d = ImageDraw.Draw(im)
    ch, cw = res / rows, res / cols
    for r in range(rows):
        for c in range(cols):
            s = min(ch, cw) * 0.72
            glyph(d, c * cw + (cw - s) / 2, r * ch + (ch - s) / 2, s, rng, w)
        if border:
            y = r * ch + 2
            d.line([(0, y), (res, y)], fill=255, width=max(2, w // 3))
    im = im.filter(ImageFilter.GaussianBlur(blur))
    im.save(path)
    return path


if __name__ == "__main__":
    sheet(sys.argv[1] if len(sys.argv) > 1 else "/home/claude/cos/out/runes_a.png")


def code_sheet(path, seed=3, res=1024, rows=12, cols=16, blur=0.8):
    """blocky 3x5 pixel glyphs + 1/0s: 'corrupted code'"""
    rng = random.Random(seed)
    im = Image.new("L", (res, res), 0); d = ImageDraw.Draw(im)
    ch, cw = res / rows, res / cols
    for r in range(rows):
        for c in range(cols):
            if rng.random() < 0.18: continue
            px = cw * 0.16; ox = c * cw + (cw - 3 * px) / 2; oy = r * ch + (ch - 5 * px) / 2
            bits = rng.getrandbits(15)
            for i in range(15):
                if bits >> i & 1:
                    x, y = i % 3, i // 3
                    d.rectangle([ox + x * px, oy + y * px, ox + (x + 1) * px - 1, oy + (y + 1) * px - 1], fill=255)
    im = im.filter(ImageFilter.GaussianBlur(blur)); im.save(path); return path
