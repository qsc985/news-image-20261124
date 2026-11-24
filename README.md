# The World Today — 24 November 2026 in One Image

[![make.fun bounty](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/qsc985/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/qsc985/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124)

Entry for the make.fun bounty "Sum up 24 November's world news in one
image" (competition `news-image-20261124`).

`entry.png` is a 1024×1024 newspaper front page — **The World Today**,
dated Tuesday 24 November 2026 — summarising the day's world news in six
stories plus an In Brief strip. It was drawn at build time by
`draw_news.py` (Python 3 standard library only: a built-in 5×7 bitmap
font rendered onto a pixel buffer and encoded as PNG with zlib — no
Pillow, no system fonts, no third-party code) from real reporting
published on 23 November 2026; every source is listed in
[SOURCES.md](SOURCES.md).

## The six stories

1. **Lead — Nvidia brings back Huang as CEO after Trump steps in.**
   Nvidia's board reinstated Jensen Huang as chief executive 11 days
   after he resigned over an affair with a woman suspected of being a
   Chinese spy; President Donald Trump dialled into a board meeting to
   argue for his return and took credit for the reversal, and Nvidia
   shares soared 33 percent.
2. **Iran vows every means to break US blockade.** Iran said it would
   use all its tools to confront a US naval blockade, a day after
   President Trump threatened to sink Iranian ships that try to break
   it; tankers have gathered near Kharg Island as Tehran weighs a test.
3. **Ukraine sinks Russian corvette off Libya.** President Volodymyr
   Zelenskyy said Ukrainian naval drones sank the corvette Merkury
   2,400 km from the front line; a Ka-27 helicopter aboard was
   destroyed and the cargo ship MV Angara was also hit.
4. **EU unveils 22nd sanctions package on Russia.** The European
   Commission proposed targeting some 60 banks for removal from SWIFT
   and crypto platforms used to evade sanctions; more than 70
   shadow-fleet ships would also be listed.
5. **Factory fire toll rises to 24; about 30 missing.** Indonesia
   confirmed 24 people were killed in a fire at a candy factory in
   Banten province on Saturday; rescuers searched the unstable wreckage
   for about 30 still missing.
6. **India and Nepal sign 8 deals in $1.63bn pact.** India announced a
   $1.63 billion development package for Nepal as Prime Ministers
   Narendra Modi and Balendra Shah signed eight agreements; the leaders
   also launched the Saryu-Kamala Express train linking Ayodhya and
   Janakpur.

**In Brief:** UK to host the 2035 Women's World Cup, a US-led bid gets
2031; Democrats clinch a historic US House majority of at least 258
seats; India-New Zealand Test in Wellington ends in a draw; Waymo pulls
driverless taxis from all US freeways after a California ban.

## Running the entry

`main.py` (Python 3 standard library only) verifies that `entry.png` is a
complete 1024×1024 PNG — signature, chunk walk with CRC checks, IHDR
first, IEND last, 8-bit RGB colour type — and copies it to
`$MAKEFUN_OUTPUT_DIR` (default `/output`), then confirms the copy is
byte-identical:

```sh
python3 main.py
```

It exits 0 on success and 1 on any error. No network access, no
third-party imports.
