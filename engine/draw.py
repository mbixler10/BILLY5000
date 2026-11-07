"""Small drawing helpers every page can use."""
from .display import graphics, font, color


def fill(canvas, x, y, w, h, rgb):
    r, g, b = rgb
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            canvas.SetPixel(xx, yy, r, g, b)


def alert_bar(canvas, code, kind, bar_rgb, text_rgb):
    """Red top line: airport code on the left, WARNING/ADVISORY/etc on the right."""
    fill(canvas, 0, 0, 64, 9, bar_rgb)
    text(canvas, "5x7", 1, 7, text_rgb, code)
    text(canvas, "5x7", 64 - text_width("5x7", kind), 7, text_rgb, kind)


def text_width(font_name, text):
    f = font(font_name)
    return sum(f.CharacterWidth(ord(c)) for c in text)


def text(canvas, font_name, x, y, rgb, s):
    """Draw text with its baseline at y. Returns the width drawn."""
    return graphics.DrawText(canvas, font(font_name), x, y, color(rgb), s)


def centered(canvas, font_name, y, rgb, s, width=64):
    x = (width - text_width(font_name, s)) // 2
    text(canvas, font_name, x, y, rgb, s)


def marquee(canvas, font_name, y, rgb, s, t, width=64, speed=20, pause=1.0):
    """Centered if it fits. Otherwise holds still for `pause` seconds, then scrolls
    left on a loop. `t` = seconds since the page appeared."""
    w = text_width(font_name, s)
    if w <= width:
        centered(canvas, font_name, y, rgb, s, width)
        return
    gap = 16
    scrolled = max(0.0, t - pause) * speed
    x = -(int(scrolled) % (w + gap))
    text(canvas, font_name, x, y, rgb, s)
    text(canvas, font_name, x + w + gap, y, rgb, s)


def clock(canvas, x, baseline, rgb, hhmm):
    """Big 7x13 time with a clean two-square colon (the font's own colon looks
    like two little + signs). Returns the width drawn."""
    hh, mm = hhmm.split(":")
    w = text(canvas, "7x13", x, baseline, rgb, hh)
    r, g, b = rgb
    cx = x + w + 1
    for top in (baseline - 8, baseline - 3):
        for dx in (0, 1):
            for dy in (0, 1):
                canvas.SetPixel(cx + dx, top + dy, r, g, b)
    w += 4
    w += text(canvas, "7x13", x + w, baseline, rgb, mm)
    return w


def clock_width(hhmm):
    hh, mm = hhmm.split(":")
    return text_width("7x13", hh) + 4 + text_width("7x13", mm)
