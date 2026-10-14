"""
Generates the two cards shown at the top of the README:

  assets/terminal-card.svg   ASCII art in a terminal window
  assets/info-card.svg       neofetch-style card with my info

Usage:
  pip install Pillow
  python generate_cards.py                     # ASCII art of my name
  python generate_cards.py --photo photo.jpg   # ASCII portrait from a photo
"""

import argparse
import base64
import html
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
FONTS = ASSETS / "fonts"

USERNAME = "ccao94"
FULL_NAME = "Cao Cuong Cao"

# Same palette as my portfolio
INK = "#0e100e"
PANEL = "#151814"
BORDER = "#2a3128"
CREAM = "#f3efe6"
MUTED = "#8a9183"
MATCHA = "#a9c49a"
FOREST = "#4a6741"

INFO = [
    ("Role", "Software Engineering student"),
    ("School", "EFREI Paris, M2 from Nov. 2026"),
    ("Looking for", "12-month apprenticeship"),
    ("Based in", "Paris area, France"),
]

STACK = [
    ("Backend", "Java, Spring Boot, C#, FastAPI"),
    ("Frontend", "Angular, React, TypeScript"),
    ("Data", "PostgreSQL, Spring Data JPA"),
    ("DevOps", "Docker, Kubernetes, GitHub Actions"),
    ("AI", "RAG, Mistral, ChromaDB, Presidio"),
]

HIGHLIGHTS = [
    "Built a CMDB-style tool at Thales AVS",
    "Led a team of 6 on SmartSoon (RAG)",
    "~50 PyTest tests on a price monitor",
    "French, English (C1), Vietnamese",
]

# Extra commands shown under the ASCII name (not with a photo, the card is tall enough)
COMMANDS = [
    ("ls projects/", ["monitoring  smartsoon  flighttracker  portfolio"]),
    ("cat now.txt", ["Building FlightTracker (Java, Spring Boot)", "Open to an apprenticeship from Nov. 2026"]),
]

# From light to dense: on a dark card, dense characters look brighter
RAMP = " .:-=+*#%@"


def esc(text):
    return html.escape(text, quote=True)


def font_face(name, file):
    data = base64.b64encode((FONTS / file).read_bytes()).decode()
    return f"@font-face{{font-family:'{name}';src:url(data:font/woff2;base64,{data}) format('woff2');}}"


FONT_CSS = font_face("Plex", "IBMPlexMono-Regular.woff2") + font_face("PlexMedium", "IBMPlexMono-Medium.woff2")


def window(width, height, title, body):
    """Wraps the content in a terminal window with a title bar."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>
{FONT_CSS}
text{{font-family:'Plex',ui-monospace,monospace;}}
.b{{font-family:'PlexMedium','Plex',ui-monospace,monospace;}}
.row{{opacity:0;animation:show .35s ease-out forwards;}}
.cursor{{animation:blink 1s step-end infinite;}}
@keyframes show{{from{{opacity:0;transform:translateY(4px);}}to{{opacity:1;transform:none;}}}}
@keyframes blink{{50%{{opacity:0;}}}}
</style>
<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="{INK}" stroke="{BORDER}"/>
<path d="M12.5 0.5h{width - 25}a12 12 0 0 1 12 12v22h-{width - 1}v-22a12 12 0 0 1 12-12z" fill="{PANEL}"/>
<line x1="0.5" y1="34.5" x2="{width - 0.5}" y2="34.5" stroke="{BORDER}"/>
<circle cx="20" cy="17.5" r="5" fill="{BORDER}"/><circle cx="37" cy="17.5" r="5" fill="{BORDER}"/><circle cx="54" cy="17.5" r="5" fill="{MATCHA}" opacity=".7"/>
<text x="{width / 2}" y="22" text-anchor="middle" font-size="12" fill="{MUTED}">{esc(title)}</text>
{body}
</svg>
"""


# ---------------------------------------------------------------------------
# ASCII art
# ---------------------------------------------------------------------------

def image_to_ascii(img, cols, rows):
    """Turns a grayscale image into lines of characters (bright pixel = dense char)."""
    img = img.convert("L").resize((cols, rows))
    img = ImageOps.autocontrast(img, cutoff=2)
    lines = []
    for y in range(rows):
        line = ""
        for x in range(cols):
            value = img.getpixel((x, y))
            line += RAMP[value * (len(RAMP) - 1) // 255]
        lines.append(line)
    return lines


def name_ascii(cols=72):
    """Renders "cao." with Playfair Display, then converts it to ASCII."""
    font = ImageFont.truetype(str(FONTS / "PlayfairDisplay-Bold.ttf"), 220)
    canvas = Image.new("L", (900, 300), 0)
    ImageDraw.Draw(canvas).text((20, 0), "cao.", font=font, fill=255)
    canvas = canvas.crop(canvas.getbbox())
    canvas = ImageOps.expand(canvas, border=16, fill=0)
    # Characters are about twice as tall as wide, so we halve the row count
    rows = round(cols * canvas.height / canvas.width * 0.5)
    return image_to_ascii(canvas, cols, rows)


def photo_ascii(path, cols=72):
    """Converts a portrait photo to ASCII. Tall photos are cropped to a square from the top."""
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    w, h = img.size
    if h > w:
        top = int(h * 0.06)
        img = img.crop((0, top, w, top + w))
    rows = round(cols * img.height / img.width * 0.5)
    return image_to_ascii(img, cols, rows)


def terminal_card(lines, commands=(), script="banner.sh"):
    char_w, line_h, pad = 6.6, 12, 20
    cols = max(len(line) for line in lines)
    width = round(cols * char_w + pad * 2)
    art_top = 34 + 22
    cmd_lines = sum(1 + len(out) for _, out in commands)
    height = art_top + len(lines) * line_h + cmd_lines * 20 + len(commands) * 10 + 60

    body = []
    for i, line in enumerate(lines):
        y = art_top + i * line_h
        delay = 0.15 + i * 0.035
        body.append(
            f'<text class="row" style="animation-delay:{delay:.2f}s" x="{pad}" y="{y}" font-size="11" '
            f'fill="{MATCHA}" xml:space="preserve">{esc(line)}</text>'
        )

    # Commands and their output, under the art
    y = art_top + len(lines) * line_h + 22
    delay = 0.15 + len(lines) * 0.035 + 0.2
    for command, output in commands:
        body.append(
            f'<text class="row" style="animation-delay:{delay:.2f}s" x="{pad}" y="{y}" font-size="12">'
            f'<tspan fill="{MATCHA}">{USERNAME}@github</tspan><tspan fill="{MUTED}">:~$ </tspan>'
            f'<tspan fill="{CREAM}">{esc(command)}</tspan></text>'
        )
        y += 20
        delay += 0.25
        for out in output:
            body.append(
                f'<text class="row" style="animation-delay:{delay:.2f}s" x="{pad}" y="{y}" font-size="12" '
                f'fill="{CREAM}" fill-opacity=".75" xml:space="preserve">{esc(out)}</text>'
            )
            y += 20
            delay += 0.12
        y += 10

    foot_y = height - 20
    end = delay + 0.2
    body.append(f'<line x1="0.5" y1="{foot_y - 18}" x2="{width - 0.5}" y2="{foot_y - 18}" stroke="{BORDER}"/>')
    body.append(
        f'<text class="row" style="animation-delay:{end:.2f}s" x="{pad}" y="{foot_y}" font-size="12">'
        f'<tspan fill="{MATCHA}">{USERNAME}@github</tspan><tspan fill="{MUTED}">:~$ whoami </tspan>'
        f'<tspan fill="{CREAM}">{esc(FULL_NAME)}</tspan></text>'
    )
    cursor_x = pad + (len(f"{USERNAME}@github:~$ whoami {FULL_NAME}") + 1) * 7.2
    body.append(f'<rect class="cursor" x="{cursor_x:.1f}" y="{foot_y - 11}" width="7" height="14" fill="{MATCHA}"/>')

    return window(width, height, f"{USERNAME}@github: ~$ ./{script}", "\n".join(body))


# ---------------------------------------------------------------------------
# Info card
# ---------------------------------------------------------------------------

def info_card():
    width, pad, key_x = 500, 26, 150
    y = 34 + 40
    rows = []
    i = 0

    def add(svg):
        nonlocal i
        rows.append(f'<g class="row" style="animation-delay:{0.2 + i * 0.07:.2f}s">{svg}</g>')
        i += 1

    add(
        f'<text x="{pad}" y="{y}" font-size="16" class="b"><tspan fill="{MATCHA}">{USERNAME}</tspan>'
        f'<tspan fill="{MUTED}"> @ </tspan><tspan fill="{CREAM}">github</tspan></text>'
    )
    y += 12
    add(f'<line x1="{pad}" y1="{y}" x2="{width - pad}" y2="{y}" stroke="{BORDER}"/>')
    y += 28

    for key, value in INFO:
        add(f'<text x="{pad}" y="{y}" font-size="13" fill="{MATCHA}" class="b">{esc(key)}</text>'
            f'<text x="{key_x}" y="{y}" font-size="13" fill="{CREAM}">{esc(value)}</text>')
        y += 23

    for title, items in (("Stack", STACK), ("Highlights", HIGHLIGHTS)):
        y += 14
        title_w = len(title) * 8 + 10
        add(f'<text x="{pad}" y="{y}" font-size="13" fill="{MUTED}" class="b">{title}</text>'
            f'<line x1="{pad + title_w}" y1="{y - 4}" x2="{width - pad}" y2="{y - 4}" stroke="{BORDER}"/>')
        y += 26
        for item in items:
            if isinstance(item, tuple):
                key, value = item
                add(f'<text x="{pad}" y="{y}" font-size="13" fill="{MATCHA}" class="b">{esc(key)}</text>'
                    f'<text x="{key_x}" y="{y}" font-size="13" fill="{CREAM}">{esc(value)}</text>')
            else:
                add(f'<rect x="{pad}" y="{y - 8}" width="5" height="5" fill="{FOREST}"/>'
                    f'<text x="{pad + 16}" y="{y}" font-size="13" fill="{CREAM}">{esc(item)}</text>')
            y += 23

    height = y + 10
    return window(width, height, f"{USERNAME}@github: ~$ neofetch", "\n".join(rows))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--photo", help="portrait photo to turn into ASCII art")
    args = parser.parse_args()

    if args.photo:
        card = terminal_card(photo_ascii(args.photo), script="portrait.sh")
    else:
        card = terminal_card(name_ascii(), COMMANDS)
    (ASSETS / "terminal-card.svg").write_text(card, encoding="utf-8")
    (ASSETS / "info-card.svg").write_text(info_card(), encoding="utf-8")
    print("Cards written to", ASSETS)


if __name__ == "__main__":
    main()
