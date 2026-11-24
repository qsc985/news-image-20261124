"""Build-time script: draw the 1024x1024 newspaper front page entry.png.

Run once:  python3 draw_news.py
Reads nothing but the story constants below; writes entry.png next to
this script. Pure Python 3 standard library: a small built-in 5x7
bitmap font rendered onto an RGB pixel buffer, then encoded as a PNG
with zlib (filter 0, no interlace). No Pillow, no system fonts, no
third-party code.
"""

import struct
import textwrap
import zlib

W = H = 1024
MARGIN = 36

BLACK = (20, 20, 20)
GREY = (90, 90, 90)
RED = (178, 34, 34)
PAPER = (250, 247, 238)
RULE = (60, 60, 60)
DARK = (30, 30, 34)
GOLD = (255, 210, 90)
OFFWHITE = (235, 235, 235)

# ---------------------------------------------------------------- font
# 5x7 bitmap font: each glyph is 7 rows of 5 bits, '#' set, '.' clear.
# Glyph advance is 6 pixels (5 + 1 spacing). Only ASCII is used.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    'a': (".....", ".....", ".###.", "....#", ".####", "#...#", ".####"),
    'b': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    'c': (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    'd': ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    'e': (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    'f': ("..##.", ".#...", ".#...", "####.", ".#...", ".#...", ".#..."),
    'g': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'h': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'i': ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
    'j': ("...#.", ".....", "..##.", "...#.", "...#.", "...#.", "...#."),
    'k': ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    'l': (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'm': (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    'n': (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'o': (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    'p': (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    'q': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'r': (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    's': (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    't': (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    'u': (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    'v': (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'w': (".....", ".....", "#...#", "#...#", "#.#.#", "#.#.#", ".#.#."),
    'x': (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    'y': (".....", ".....", "#...#", "#...#", "#...#", ".####", "....#"),
    'z': (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    '0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    '&': (".###.", "#...#", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '+': (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '*': (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    '_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    '<': ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    '>': (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    '@': (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
    '#': (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    # Bullet and em dash, mapped from their unicode forms at draw time.
    '\u2022': (".....", ".###.", ".###.", ".###.", ".....", ".....", "....."),
    '\u2014': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '\u201c': (".##.#", ".##.#", ".##.#", ".....", ".....", ".....", "....."),
    '\u201d': (".##.#", ".##.#", ".##.#", ".....", ".....", ".....", "....."),
    '\u2019': ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
}


def text_width(text, scale):
    """Pixel width of `text` at the given font scale (monospace)."""
    return len(text) * 6 * scale


def draw_text(pixels, text, x, y, scale, color):
    """Draw `text` with its top-left corner at (x, y). Unknown glyphs
    become blanks; curly quotes and dashes are normalised first."""
    text = (text.replace("\u2018", "'").replace("\u2019", "'")
            .replace("\u201c", '"').replace("\u201d", '"'))
    for ch in text:
        glyph = FONT.get(ch)
        if glyph:
            for row_i, row in enumerate(glyph):
                for col_i, bit in enumerate(row):
                    if bit == '#':
                        for dy in range(scale):
                            for dx in range(scale):
                                px = x + col_i * scale + dx
                                py = y + row_i * scale + dy
                                if 0 <= px < W and 0 <= py < H:
                                    pixels[py * W + px] = color
        x += 6 * scale
    return x


def wrap_text(text, max_chars):
    """Greedy word wrap on character count (monospace font)."""
    lines = []
    for para in text.split("\n"):
        lines.extend(textwrap.wrap(para, width=max_chars) or [""])
    return lines


def draw_para(pixels, text, x, y, width, scale, color=BLACK):
    """Draw wrapped text; return the y just below the last line."""
    max_chars = max(1, width // (6 * scale))
    leading = 7 * scale + scale // 2 + 2
    for line in wrap_text(text, max_chars):
        draw_text(pixels, line, x, y, scale, color)
        y += leading
    return y


def rect(pixels, x0, y0, x1, y1, color):
    for py in range(max(0, y0), min(H, y1)):
        base = py * W
        for px in range(max(0, x0), min(W, x1)):
            pixels[base + px] = color


def hline(pixels, y, x0=MARGIN, x1=W - MARGIN, width=2, color=RULE):
    for dy in range(width):
        for px in range(x0, x1):
            pixels[(y + dy) * W + px] = color


def headline_block(pixels, x, y, width, kicker, headline, body,
                   head_scale=4, body_scale=2, kicker_color=RED):
    draw_text(pixels, kicker, x, y, 2, kicker_color)
    y += 7 * 2 + 6
    y = draw_para(pixels, headline, x, y, width, head_scale)
    y += 6
    y = draw_para(pixels, body, x, y, width, body_scale)
    return y


def encode_png(pixels):
    """Encode an RGB pixel buffer as a PNG (8-bit, colour type 2)."""
    raw = bytearray()
    for row in range(H):
        raw.append(0)  # filter: none
        base = row * W
        for i in range(W):
            raw.extend(pixels[base + i])
    data = zlib.compress(bytes(raw), 9)

    def chunk(kind, payload):
        return (struct.pack(">I", len(payload)) + kind + payload +
                struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", data) + chunk(b"IEND", b""))


def main():
    pixels = [PAPER] * (W * H)

    # ---- Masthead -------------------------------------------------
    title = "THE WORLD TODAY"
    scale = 9
    tw = text_width(title, scale)
    y = 18
    draw_text(pixels, title, (W - tw) // 2, y, scale, BLACK)
    y += 7 * scale + 12
    hline(pixels, y, width=3)
    y += 10
    dateline = ("TUESDAY 24 NOVEMBER 2026  \u2022  ONE IMAGE \u2014 SIX STORIES "
                "FROM AROUND THE GLOBE")
    draw_text(pixels, dateline, (W - text_width(dateline, 2)) // 2, y, 2, BLACK)
    y += 7 * 2 + 12
    hline(pixels, y, width=1)

    # ---- Lead story: Nvidia brings Huang back ---------------------
    y += 10
    lead_w = W - 2 * MARGIN
    y = headline_block(
        pixels, MARGIN, y, lead_w,
        "LEAD  \u2022  TECH  \u2022  SANTA CLARA",
        "Nvidia brings back Huang as CEO after Trump steps in",
        "Nvidia's board on Monday reinstated Jensen Huang as chief "
        "executive, 11 days after he resigned over an affair with a woman "
        "suspected of being a Chinese spy. The board said it had received "
        "input from senior levels of the US government and was confident "
        "his return posed no national security risk. President Donald "
        "Trump, who dialled into a board meeting to argue for Huang's "
        "return, took credit for the reversal, and Nvidia shares soared "
        "33 percent.",
        head_scale=5, body_scale=2)
    y += 10
    hline(pixels, y, width=1)

    # ---- Three-column row -----------------------------------------
    y += 8
    col_w = (W - 2 * MARGIN - 2 * 24) // 3
    xs = [MARGIN, MARGIN + col_w + 24, MARGIN + 2 * (col_w + 24)]
    stories = [
        ("CONFLICT  \u2022  HORMUZ",
         "Iran vows every means to break US blockade",
         "Iran said on Monday it would use all its tools to confront a US "
         "naval blockade, a day after President Donald Trump threatened "
         "to sink Iranian ships that try to break it. Tankers have "
         "gathered near Kharg Island as Tehran weighs a test."),
        ("WAR AT SEA  \u2022  LIBYA",
         "Ukraine sinks Russian corvette off Libya",
         "President Volodymyr Zelenskyy said on Monday that Ukrainian "
         "naval drones sank the Russian corvette Merkury off Libya, "
         "2,400 km from the front line. A Ka-27 helicopter aboard was "
         "destroyed and the cargo ship MV Angara was also hit."),
        ("EUROPE  \u2022  BRUSSELS",
         "EU unveils 22nd sanctions package on Russia",
         "The European Commission on Monday proposed its 22nd package of "
         "sanctions on Russia, targeting some 60 banks for removal from "
         "SWIFT and crypto platforms used to evade sanctions. More than "
         "70 shadow-fleet ships would also be listed."),
    ]
    row_end = y
    for x, (kick, head, body) in zip(xs, stories):
        end = headline_block(pixels, x, y, col_w, kick, head, body,
                             head_scale=3, body_scale=2)
        row_end = max(row_end, end)
    y = row_end + 8
    hline(pixels, y, width=1)

    # ---- Two-column row -------------------------------------------
    y += 8
    col2_w = (W - 2 * MARGIN - 24) // 2
    stories2 = [
        ("DISASTER  \u2022  INDONESIA",
         "Factory fire toll rises to 24; about 30 missing",
         "Indonesia confirmed on Monday that 24 people were killed in a "
         "fire that tore through a candy factory in Banten province on "
         "Saturday. Rescuers searched the unstable wreckage for about 30 "
         "people still missing, while relatives waited at a police "
         "hospital for DNA tests."),
        ("DIPLOMACY  \u2022  NEW DELHI",
         "India and Nepal sign 8 deals in $1.63bn pact",
         "India announced a $1.63 billion development package for Nepal on "
         "Monday as Prime Ministers Narendra Modi and Balendra Shah "
         "signed eight agreements covering space technology, health, "
         "policing, governance and agriculture. The leaders also launched "
         "the Saryu-Kamala Express train linking Ayodhya and Janakpur."),
    ]
    row_end = y
    for x, (kick, head, body) in zip([MARGIN, MARGIN + col2_w + 24], stories2):
        end = headline_block(pixels, x, y, col2_w, kick, head, body,
                             head_scale=3, body_scale=2)
        row_end = max(row_end, end)
    y = row_end + 4

    # ---- In Brief strip -------------------------------------------
    strip_h = 100
    rect(pixels, MARGIN, y, W - MARGIN, y + strip_h, DARK)
    draw_text(pixels, "IN BRIEF", MARGIN + 14, y + 10, 2, GOLD)
    briefs = [
        "UK to host the 2035 Women's World Cup; a US-led bid gets the 2031 edition.",
        "Democrats clinch a historic US House majority of at least 258 seats.",
        "India-New Zealand Test in Wellington ends in a draw; NZ finish 239/5.",
        "Waymo pulls driverless taxis from all US freeways after a California ban.",
    ]
    by = y + 32
    for b in briefs:
        lines = wrap_text("\u2022  " + b, (W - 2 * MARGIN - 28) // 12)
        for line in lines:
            draw_text(pixels, line, MARGIN + 14, by, 2, OFFWHITE)
            by += 17
    draw_text(pixels,
              "Sources: Reuters, AP, The Hindu BusinessLine - see SOURCES.md",
              MARGIN, y + strip_h + 6, 1, GREY)

    with open("entry.png", "wb") as handle:
        handle.write(encode_png(pixels))
    print(f"wrote entry.png 1024x1024 (page bottom y={y + strip_h + 20})")


if __name__ == "__main__":
    main()
