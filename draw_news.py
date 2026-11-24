#!/usr/bin/env python3
"""Render the front page of 'The World Today' for Tuesday 24 November 2026.

A single 1024x1024 newspaper front page summarising six real world-news
stories from Monday 23 November 2026, plus an In Brief strip. Written from
scratch for the 2026-11-24 edition. Requires Pillow.

Usage:
    python3 draw_news.py            # writes entry.png next to this file
"""

from __future__ import annotations

import os

from PIL import Image, ImageDraw, ImageFont

WIDTH = 1024
HEIGHT = 1024
MARGIN = 38
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

PAPER = (247, 243, 232)
INK = (18, 18, 18)
MUTED = (90, 84, 72)
ACCENT = (148, 24, 24)
RULE = (40, 40, 40)
LIGHT_RULE = (180, 172, 156)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont,
         max_width: int) -> list[str]:
    """Greedy word wrap using the font's real metrics."""
    lines: list[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            trial = current + " " + word
            if draw.textlength(trial, font=fnt) <= max_width:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_wrapped(draw: ImageDraw.ImageDraw, x: int, y: int, text: str,
                 fnt: ImageFont.FreeTypeFont, max_width: int,
                 fill=INK, leading: int | None = None) -> int:
    """Draw wrapped text; return the y coordinate just below the last line."""
    if leading is None:
        leading = fnt.size + 6
    for line in wrap(draw, text, fnt, max_width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def centred(draw: ImageDraw.ImageDraw, y: int, text: str,
            fnt: ImageFont.FreeTypeFont, fill=INK) -> int:
    width = draw.textlength(text, font=fnt)
    draw.text(((WIDTH - width) / 2, y), text, font=fnt, fill=fill)
    return y + fnt.size + 6


def rule(draw: ImageDraw.ImageDraw, y: int, x0: int, x1: int, width: int = 1,
         fill=RULE) -> None:
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def kicker(draw: ImageDraw.ImageDraw, x: int, y: int, text: str) -> int:
    fnt = font(SANS_BOLD, 14)
    draw.text((x, y), text.upper(), font=fnt, fill=ACCENT)
    return y + 21


def headline(draw: ImageDraw.ImageDraw, x: int, y: int, text: str,
             size: int, max_width: int, leading: int | None = None) -> int:
    fnt = font(SERIF_BOLD, size)
    return draw_wrapped(draw, x, y, text, fnt, max_width, leading=leading)


def main() -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(image)
    left = MARGIN
    right = WIDTH - MARGIN
    content_w = right - left

    # ---------- Masthead ----------
    y = 20
    y = centred(draw, y, "TUESDAY, 24 NOVEMBER 2026", font(SANS_BOLD, 16), MUTED)
    y += 2
    y = centred(draw, y, "The World Today", font(SERIF_BOLD, 60))
    y = centred(draw, y, "Six stories that shaped the world — in one page",
                font(SERIF_ITALIC, 17), MUTED)
    y += 4
    rule(draw, y, left, right, width=4)
    y += 6
    rule(draw, y, left, right, width=1)
    y += 10

    # ---------- Lead story: Nvidia / Huang ----------
    y = kicker(draw, left, y, "Lead story — Markets · Washington")
    y = headline(draw, left, y,
                 "Nvidia brings back Huang as CEO after Trump steps in",
                 size=31, max_width=content_w, leading=37)
    y += 2
    body = (
        "Nvidia's board voted unanimously on Monday to reinstate Jensen Huang "
        "as president and chief executive, eleven days after he resigned over "
        "revelations of extramarital affairs, including one with a woman "
        "suspected of being a Chinese spy. The board said it had received "
        "\u201cinput from senior levels of the United States government\u201d and "
        "was confident the return posed no national security risk. President "
        "Donald Trump dialled into a board meeting to argue for Huang's "
        "return, telling CNBC his intervention was 'very important.' "
        "Shares soared 33%, adding more than $900 billion in "
        "market value. Huang will testify before the US Senate on 3 December."
    )
    y = draw_wrapped(draw, left, y, body, font(SERIF, 18), content_w,
                     leading=22)
    y += 8
    rule(draw, y, left, right, width=2)
    y += 12

    # ---------- Stories 2-5 in a two-column grid ----------
    stories = [
        ("Middle East", "Iran vows every means to break US blockade",
         "Tehran said on Monday it would use all its tools to confront the "
         "US naval blockade of its ports, a day after President Trump warned "
         "Iranian tankers that tried to break it would end up \u201cat the "
         "bottom of the sea\u201d. More than a dozen Iranian oil tankers have "
         "gathered near Kharg Island as Tehran weighs testing it."),
        ("Ukraine war", "Ukraine sinks Russian corvette off Libya",
         "President Volodymyr Zelenskyy said Ukrainian forces sank the "
         "Russian corvette Merkury off Libya using seven Ukrainian-made "
         "naval drones. The ship, commissioned in 2023, was docked at the "
         "Benghazi naval base, about 2,400 km from the front line. The "
         "cargo vessel MV Angara was also hit."),
        ("Europe", "EU unveils 22nd sanctions package on Russia",
         "The European Commission proposed its 22nd sanctions package "
         "against Russia on Monday. It targets some 60 Russian banks, all "
         "to be removed from SWIFT, and cracks down on crypto networks used "
         "to evade sanctions. More than 70 shadow-fleet vessels would be "
         "listed."),
        ("Asia", "Factory fire toll rises to 24; about 30 missing",
         "Indonesian authorities confirmed 24 people were killed in a fire "
         "that tore through a building of the PT Fonusa Agung Mulia "
         "confectionery factory in Cikande, Banten, on Saturday evening. "
         "About 30 people remained missing as rescuers searched the "
         "burned-out structure; about 300 were on shift when it started."),
    ]
    col_w = (content_w - 28) // 2
    grid_top = y
    row_h = 168
    for i, (section, title, text) in enumerate(stories):
        col = i % 2
        row = i // 2
        x = left + col * (col_w + 28)
        yy = grid_top + row * row_h
        yy = kicker(draw, x, yy, section)
        yy = headline(draw, x, yy, title, size=22, max_width=col_w,
                      leading=26)
        yy = draw_wrapped(draw, x, yy + 2, text, font(SERIF, 14), col_w,
                          leading=18)
        if col == 0:
            draw.line([(left + col_w + 14, grid_top + row * row_h),
                       (left + col_w + 14,
                        grid_top + row * row_h + row_h - 14)],
                      fill=LIGHT_RULE, width=1)
    y = grid_top + 2 * row_h
    rule(draw, y, left, right, width=2)
    y += 12

    # ---------- Story 6: India-Nepal, full width ----------
    y = kicker(draw, left, y, "South Asia")
    y = headline(draw, left, y,
                 "India and Nepal sign eight deals in $1.63bn pact",
                 size=24, max_width=content_w, leading=29)
    y = draw_wrapped(
        draw, left, y + 2,
        "Prime Minister Narendra Modi announced a $1.63 billion development "
        "cooperation package for Nepal after talks with Prime Minister "
        "Balendra Shah in New Delhi. The two sides signed eight agreements "
        "covering satellite communications, forensic science, police "
        "training and health, and launched the Saryu-Kamala Express train "
        "linking Ayodhya and Janakpur.",
        font(SERIF, 16), content_w, leading=20)
    y += 10
    rule(draw, y, left, right, width=2)
    y += 10

    # ---------- In Brief strip: one line per item ----------
    briefs = [
        ("Sport", "UK to host the 2035 Women's World Cup; a US-led bid "
                  "gets the 2031 edition."),
        ("Politics", "Democrats clinch a historic US House majority of at "
                     "least 258 seats."),
        ("Sport", "India–New Zealand Test in Wellington ends in a draw; "
                  "New Zealand finish 239/5."),
        ("Tech", "Waymo pulls driverless taxis from all US freeways after "
                 "a California ban."),
    ]
    draw.rectangle([left, y, right, y + 24], fill=INK)
    draw.text((left + 10, y + 4), "IN BRIEF", font=font(SANS_BOLD, 15),
              fill=PAPER)
    y += 24
    for tag, text in briefs:
        tag_text = tag.upper() + " — "
        tag_fnt = font(SANS_BOLD, 13)
        body_fnt = font(SERIF, 14)
        draw.text((left, y + 2), tag_text, font=tag_fnt, fill=ACCENT)
        tag_w = draw.textlength(tag_text, font=tag_fnt)
        lines = wrap(draw, text, body_fnt, content_w - tag_w)
        draw.text((left + tag_w, y + 2), lines[0], font=body_fnt, fill=INK)
        y += 18
    y += 2

    print(f"Layout finished at y={y} of {HEIGHT}")
    image.save(OUT_PATH, format="PNG", optimize=True)
    size = os.path.getsize(OUT_PATH)
    print(f"Wrote {OUT_PATH}: {image.size[0]}x{image.size[1]}, "
          f"{size} bytes")


if __name__ == "__main__":
    main()
