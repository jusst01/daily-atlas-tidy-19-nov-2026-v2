import os
import sys
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1024, 1024

PAPER = (240, 242, 244)
CARD = (253, 254, 255)
INK = (24, 28, 34)
GREY = (100, 106, 112)
ACCENT = (52, 70, 92)
TEAL = (44, 96, 88)
NAVY = (30, 44, 66)
BORDER = (190, 198, 206)
DATE_CHECK_RED = (172, 62, 44)

CONT_COLOURS = {
    'Americas': (168, 62, 44),
    'Europe': (58, 84, 128),
    'Mideast': (186, 122, 38),
    'Africa': (122, 106, 52),
    'Asia': (116, 80, 148),
    'Oceania': (44, 124, 134)
}

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"

def get_font(name, size):
    mapping = {
        "Sans-Bold": "DejaVuSans-Bold.ttf",
        "Sans": "DejaVuSans.ttf",
        "Serif-Bold": "DejaVuSerif-Bold.ttf",
        "Serif": "DejaVuSerif.ttf",
        "Serif-Italic": "DejaVuSerif-Italic.ttf"
    }
    path = os.path.join(FONT_DIR, mapping.get(name, "DejaVuSans.ttf"))
    if not os.path.exists(path):
        path = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
    return ImageFont.truetype(path, size)

def wrap(text, font, max_width):
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        if font.getlength(test_line) <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                lines.append(word)
                current_line = []
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def block(draw, x, y, w, text, font, line_height, max_y, fill=INK):
    lines = wrap(text, font, w)
    clip_failed = 0
    for line in lines:
        if y + line_height > max_y:
            clip_failed += 1
            break
        draw.text((x, y), line, fill=fill, font=font)
        y += line_height
    return y, clip_failed

def chip(draw, cx, cy, r, n, fill=ACCENT):
    draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=fill)
    f = get_font("Sans-Bold", max(8, int(1.12*r)))
    draw.text((cx, cy), str(n), fill="white", font=f, anchor="mm")

def mute(col):
    return tuple(int(c + (PAPER[i] - c) * 0.52) for i, c in enumerate(col))

# World map mask data
MAP_SPANS = {
    1: [(8,11), (27,30), (48,50), (59,61)],
    2: [(1,6), (9,23), (26,31), (44,70)],
    3: [(1,7), (8,25), (27,31), (38,70)],
    4: [(2,8), (9,26), (28,30), (37,70)],
    5: [(3,8), (10,26), (31,31), (37,70)],
    6: [(5,8), (11,25), (32,33), (34,70)],
    7: [(10,24), (32,32), (33,69)],
    8: [(10,23), (32,45), (46,66)],
    9: [(10,23), (33,44), (45,66)],
    10: [(10,23), (33,43), (44,63)],
    11: [(10,22), (32,38), (39,47), (48,64)],
    12: [(11,21), (33,53), (55,62)],
    13: [(11,17), (33,48), (49,53), (54,60)],
    14: [(13,16), (33,45), (49,52), (55,60)],
    15: [(11,11), (34,45), (50,51), (56,58)],
    16: [(34,44), (46,47), (56,58), (60,61)],
    17: [(34,45), (56,62)],
    18: [(35,45), (58,63)],
    19: [(17,22), (35,45), (58,64)],
    20: [(17,23), (37,44), (60,66)],
    21: [(18,23), (38,44), (64,68)],
    22: [(18,24), (38,44), (60,67)],
    23: [(18,24), (39,44), (46,46), (60,68)],
    24: [(18,24), (39,44), (46,46), (59,68)],
    25: [(18,23), (39,44), (46,46), (59,67)],
    26: [(18,23), (40,44), (60,66)],
    27: [(18,22), (40,43), (61,65)],
    28: [(18,22), (40,43), (61,65), (71,71)],
    29: [(19,21), (40,42), (62,64)],
    30: [(19,21), (40,42), (62,63), (71,72)],
    31: [(19,20), (63,63)],
    32: [(19,20), (70,71)],
    33: [(19,19)],
    34: [(19,19)],
    35: [(19,19)],
    36: [(19,19)]
}

def get_continent(lon, lat):
    if lon < -30:
        return 'Americas'
    if lon >= 112 and lat < -11:
        return 'Oceania'
    if lon >= 52:
        return 'Asia'
    if lat >= 42:
        return 'Europe'
    if lon >= 20 and lat >= 12:
        return 'Mideast'
    if lat >= 35:
        return 'Europe'
    return 'Africa'

def draw_scene_strip(draw, x, y, w, h, kind, fig_text=None):
    draw.rectangle((x, y, x+w, y+h), fill=(230, 235, 240))
    if kind == 'tanker':
        # Ship hull and flame
        draw.polygon([(x+20, y+h-8), (x+w-20, y+h-8), (x+w-30, y+h-18), (x+30, y+h-18)], fill=INK)
        draw.ellipse((x+w/2-6, y+8, x+w/2+6, y+24), fill=(220, 100, 30))
    elif kind == 'bridge':
        # Bridge pylons and broken span
        draw.rectangle((x+30, y+10, x+40, y+h-4), fill=GREY)
        draw.rectangle((x+w-40, y+10, x+w-30, y+h-4), fill=GREY)
        draw.line((x+35, y+15, x+w/2-10, y+20), fill=INK, width=3)
        draw.line((x+w/2+10, y+20, x+w-35, y+15), fill=DATE_CHECK_RED, width=3)
    elif kind == 'lockdown':
        # Shutter lines and lock
        for yy in range(y+6, y+h-4, 6):
            draw.line((x+10, yy, x+w-10, yy), fill=GREY, width=1)
        draw.rectangle((x+w/2-8, y+h/2-8, x+w/2+8, y+h/2+8), fill=(180, 150, 50))
    elif kind == 'climate':
        # Globe circle
        draw.ellipse((x+w/2-14, y+4, x+w/2+14, y+32), outline=TEAL, width=2)
        draw.arc((x+w/2-14, y+4, x+w/2+14, y+32), 0, 360, fill=TEAL)
    elif kind == 'exam':
        # Paper and phone crossed out
        draw.rectangle((x+25, y+6, x+w-25, y+h-6), outline=INK, fill="white")
        draw.line((x+35, y+14, x+w-35, y+14), fill=GREY, width=2)
        draw.line((x+35, y+22, x+w-50, y+22), fill=GREY, width=2)
        draw.line((x+20, y+4, x+w-20, y+h-4), fill=DATE_CHECK_RED, width=2)
    elif kind == 'markets':
        # Falling polyline
        draw.line([(x+15, y+10), (x+60, y+20), (x+110, y+15), (x+w-15, y+h-8)], fill=DATE_CHECK_RED, width=2)
    elif kind == 'ipo':
        # Large $83
        f = get_font("Sans-Bold", 20)
        draw.text((x+15, y+6), "$83", fill=ACCENT, font=f)
    elif kind == 'jobs':
        # Briefcase
        draw.rectangle((x+w/2-14, y+12, x+w/2+14, y+30), fill=ACCENT, outline=INK)
        draw.arc((x+w/2-6, y+4, x+w/2+6, y+14), 180, 360, fill=INK, width=2)
    elif kind == 'claims':
        # Rising polyline
        draw.line([(x+15, y+h-10), (x+60, y+22), (x+110, y+15), (x+w-15, y+8)], fill=(200, 120, 30), width=2)
    elif kind == 'cyclone':
        # Spiral arcs
        cx_s, cy_s = x + w/2, y + h/2
        draw.arc((cx_s-12, cy_s-12, cx_s+12, cy_s+12), 0, 270, fill=TEAL, width=2)
        draw.arc((cx_s-20, cy_s-20, cx_s+20, cy_s+20), 45, 315, fill=TEAL, width=2)
    elif kind == 'diploma':
        # Diploma scroll
        draw.rectangle((x+30, y+10, x+w-30, y+24), fill="white", outline=INK)
        draw.ellipse((x+w/2-6, y+12, x+w/2+6, y+22), fill=DATE_CHECK_RED)
    elif kind == 'storm':
        # Cloud and rain
        draw.ellipse((x+30, y+6, x+w-30, y+22), fill=GREY)
        for xx in range(x+40, x+w-30, 12):
            draw.line((xx, y+24, xx-4, y+h-4), fill=ACCENT, width=2)
    else:
        draw.rectangle((x+10, y+6, x+w-10, y+h-6), fill=GREY)

    if fig_text:
        f_fig = get_font("Sans-Bold", 14)
        draw.text((x+w-12, y+18), fig_text, fill=INK, font=f_fig, anchor="rm")

def draw_page():
    img = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(img)

    drawn_stories = set()
    pasted_kinds = set()
    clip_failures = 0

    # 1. MASTHEAD (V3 Redesign: Eyebrow, largest title, dek)
    draw.text((24, 8), "THE WORLD IN ONE DAY · THE DAILY ATLAS", fill=ACCENT, font=get_font("Sans-Bold", 11))
    draw.text((1000, 8), "33 STORIES · ONE PAGE", fill=INK, font=get_font("Sans-Bold", 11), anchor="ra")

    display_date = "Thursday 19 November 2026"
    f_title = get_font("Serif-Bold", 58)
    draw.text((512, 28), display_date, fill=INK, font=f_title, anchor="ma")

    dek_text = "Trump, Xi and Putin share one table · The World Court finds genocide in Myanmar · A 13-year wait for a game ends"
    draw.text((512, 94), dek_text, fill=GREY, font=get_font("Sans", 10.5), anchor="ma")

    draw.line((24, 110, 1000, 110), fill=ACCENT, width=3)
    draw.line((24, 115, 1000, 115), fill=ACCENT, width=1)

    # 2. REGION BAR
    bar_y = 120
    region_data = [
        ("ASIA", 11, CONT_COLOURS['Asia']),
        ("MIDDLE EAST", 5, CONT_COLOURS['Mideast']),
        ("EUROPE", 6, CONT_COLOURS['Europe']),
        ("AFRICA", 1, CONT_COLOURS['Africa']),
        ("AMERICAS", 8, CONT_COLOURS['Americas']),
        ("OCEANIA", 2, CONT_COLOURS['Oceania'])
    ]
    total_w = 1000 - 24
    seg_w = total_w / 6.0
    for i, (name, count, col) in enumerate(region_data):
        x1 = 24 + int(i * seg_w)
        x2 = 24 + int((i + 1) * seg_w) - 2
        draw.rectangle((x1, bar_y, x2, bar_y+26), fill=col)
        draw.text(((x1+x2)/2, bar_y+13), f"{name} {count}", fill="white", font=get_font("Sans-Bold", 11.5), anchor="mm")

    # 3. STAT STRIP
    stat_y = bar_y + 32
    stat_data = [
        ("3", "presidents at one table"),
        ("9–6", "the genocide ruling"),
        ("$81.3bn", "Anthropic's record IPO"),
        ("551,864", "S. Korea's exam sitters"),
        ("−1.95%", "Hang Seng close"),
        ("589M", "children in war zones")
    ]
    stat_w = total_w / 6.0
    for i, (fig, cap) in enumerate(stat_data):
        x1 = 24 + int(i * stat_w)
        x2 = 24 + int((i + 1) * stat_w) - 2
        draw.rectangle((x1, stat_y, x2, stat_y+48), fill=CARD, outline=BORDER)
        draw.text(((x1+x2)/2, stat_y+14), fig, fill=INK, font=get_font("Sans-Bold", 15), anchor="mm")
        draw.text(((x1+x2)/2, stat_y+36), cap, fill=GREY, font=get_font("Sans", 8.5), anchor="mm")

    # 4. FEATURED TILES (3)
    feat_y = stat_y + 56
    feat_data = [
        # Story 3 (GTA VI) first, Story 1 (Shenzhen) second, Story 2 (ICJ) third
        {
            "id": 3, "kind": "games",
            "kick": "GAMES · LAUNCH DAY", "tag": "13 YEARS AFTER GTA V", "tag_col": (16, 22, 34),
            "chip": "CONFIRMED · SENSOR TOWER",
            "head": "GTA VI is out: launch day lands",
            "summ": "Midnight launch on PS5 and Xbox; ~17M copies and $1.65B in pre-sales estimated; 212 GB install."
        },
        {
            "id": 1, "kind": "summit",
            "kick": "CHINA · APEC SUMMIT", "tag": "FIRST-EVER TRILATERAL", "tag_col": NAVY,
            "chip": "CONFIRMED · REUTERS/AP",
            "head": "Trump, Xi, Putin: first three-way summit",
            "summ": "90 minutes in Shenzhen; a joint declaration on nuclear-risk dialogue, UN reform and oil supply."
        },
        {
            "id": 2, "kind": "court",
            "kick": "THE HAGUE · WORLD COURT", "tag": "ROHINGYA JUDGMENT", "tag_col": ACCENT,
            "chip": "CONFIRMED · ICJ",
            "head": "ICJ: Myanmar committed genocide",
            "summ": "A 9-6 ruling - the first time the Court has found a state responsible for genocide. Reparations ordered."
        }
    ]

    card_w = 317
    card_gap = 13
    for i, item in enumerate(feat_data):
        x = 24 + i * (card_w + card_gap)
        y = feat_y
        draw.rectangle((x, y, x+card_w, y+162), fill=CARD, outline=BORDER)
        drawn_stories.add(item["id"])

        # Paste artwork across top 74px
        art_path = f"assets/{item['kind']}.jpg"
        if os.path.exists(art_path):
            try:
                art_img = Image.open(art_path)
                # Center crop to 317:74 ratio
                aw, ah = art_img.size
                target_ratio = card_w / 74.0
                curr_ratio = aw / ah
                if curr_ratio > target_ratio:
                    new_w = int(ah * target_ratio)
                    left = (aw - new_w) // 2
                    art_img = art_img.crop((left, 0, left + new_w, ah))
                else:
                    new_h = int(aw / target_ratio)
                    top = (ah - new_h) // 2
                    art_img = art_img.crop((0, top, aw, top + new_h))
                art_img = art_img.resize((card_w, 74), Image.Resampling.LANCZOS)
                img.paste(art_img, (x, y))
                pasted_kinds.add(item['kind'])
            except Exception as e:
                print(f"Error loading {art_path}: {e}")

        # Tag bar from y+48 to y+74
        tag_y1 = y + 48
        tag_y2 = y + 74
        draw.rectangle((x, tag_y1, x+card_w, tag_y2), fill=item['tag_col'])
        draw.rectangle((x, tag_y1, x+5, tag_y2), fill=ACCENT if item['tag_col'] != ACCENT else INK)
        draw.text((x+14, (tag_y1+tag_y2)/2), item['tag'], fill="white", font=get_font("Sans-Bold", 11), anchor="lm")

        # Number chip & kicker
        chip(draw, x+16, y+86, 9.5, item["id"], ACCENT)
        draw.text((x+32, y+86), item["kick"], fill=ACCENT, font=get_font("Sans-Bold", 10), anchor="lm")

        # Source chip right side
        chip_text = item["chip"]
        f_schip = get_font("Sans-Bold", 8)
        pw = int(f_schip.getlength(chip_text)) + 14
        draw.rounded_rectangle((x+card_w-8-pw, y+78, x+card_w-8, y+94), radius=7, fill=(90, 88, 80))
        draw.text((x+card_w-8-pw/2, y+86), chip_text, fill="white", font=f_schip, anchor="mm")

        # Headline & Summary
        ny, c_err = block(draw, x+10, y+96, card_w-20, item["head"], get_font("Serif-Bold", 15), 16, y+134)
        clip_failures += c_err
        block(draw, x+10, ny+2, card_w-20, item["summ"], get_font("Serif", 9), 11, y+160)

    # 5. GRID TILES (12 cards, 4 cols x 3 rows)
    grid_data = [
        (4, "IRAN · GULF", "Tehran: two supertankers hit mines, ablaze", "IRGC claim; AP could not confirm.", "tanker", "CLAIM · IRGC"),
        (5, "UKRAINE · WAR", "Crimean Bridge struck a third time", "Putin rules out a truce, vows a harsher reply.", "bridge", "CONFIRMED · REUTERS"),
        (6, "BANGLADESH · UNREST", "Nationwide shutdown; two killed", "97 Border Guard platoons deployed.", "lockdown", "CONFIRMED · REUTERS"),
        (7, "CLIMATE · COP31", "Talks go to the wire, draft thins", "Fossil language out; $120bn target missing.", "climate", "CONFIRMED · REUTERS"),
        (8, "S. KOREA · EXAMS", "Exam-day dragnet catches 98", "Emergency alerts flushed out hidden phones.", "exam", "CONFIRMED · KJD"),
        (9, "ASIA · MARKETS", "Hang Seng −1.95% at a 4-month low", "Taiwan −4.4%; ASX falls a sixth day.", "markets", "CONFIRMED · EXCHANGES"),
        (10, "TECH · IPO", "Anthropic debuts as ANT", "Priced Wed at $83 - a record $81.3bn raise.", "ipo", "CONFIRMED · WIRES"),
        (11, "AUSTRALIA · JOBS", "Jobless hits 4.9%, a 4-year high", "Employment falls 43,500 in October.", "jobs", "CONFIRMED · ABS"),
        (12, "US · LABOUR", "Jobless claims edge up to 203,000", "Continuing claims jump 70,000 to 1.76M.", "claims", "CONFIRMED · REUTERS"),
        (13, "INDIA · WEATHER", "Cyclone Akvan closes on the coast", "Landfall due Friday; 72,000 evacuated.", "cyclone", "CONFIRMED · IMD"),
        (14, "TURKEY · LAW", "İmamoğlu degree revocation upheld", "Council of State rules; sentence was Wed.", "diploma", "CONFIRMED · TURKISH MINUTE"),
        (15, "US · WEATHER", "Storm sags south; LA on flood alert", "SF's record rain fell Wednesday.", "storm", "CONFIRMED · BLOOMBERG")
    ]

    gy = feat_y + 162 + 14
    draw.line((24, gy-7, 1000, gy-7), fill=INK, width=1)

    grid_w = 236
    grid_h = 86
    grid_gap_x = 10
    grid_gap_y = 8

    for idx, (gid, gkick, ghead, gsumm, gkind, gchip) in enumerate(grid_data):
        row = idx // 4
        col = idx % 4
        x = 24 + col * (grid_w + grid_gap_x)
        y0 = gy + row * (grid_h + grid_gap_y)

        draw.rectangle((x, y0, x+grid_w, y0+grid_h), fill=CARD, outline=BORDER)
        drawn_stories.add(gid)

        # Scene strip across top 30px
        fig_str = None
        if gid == 8: fig_str = "551,864"
        elif gid == 9: fig_str = "−1.95%"
        elif gid == 10: fig_str = "$83"
        elif gid == 11: fig_str = "4.9%"
        elif gid == 12: fig_str = "203K"
        elif gid == 13: fig_str = "72K"

        draw_scene_strip(draw, x, y0, grid_w, 30, gkind, fig_str)

        # Number chip & kicker
        chip(draw, x+12, y0+40, 6, gid, ACCENT)
        draw.text((x+22, y0+40), gkick, fill=ACCENT, font=get_font("Sans-Bold", 8), anchor="lm")

        # Source chip right
        schip_col = DATE_CHECK_RED if gchip.startswith("CLAIM") else GREY
        f_sc = get_font("Sans-Bold", 7)
        pw = int(f_sc.getlength(gchip)) + 10
        draw.text((x+grid_w-8, y0+40), gchip, fill=schip_col, font=f_sc, anchor="rm")

        # Headline & Summary
        hny, c_err = block(draw, x+8, y0+48, grid_w-16, ghead, get_font("Serif-Bold", 11), 12, y0+70)
        clip_failures += c_err
        block(draw, x+8, hny+1, grid_w-16, gsumm, get_font("Serif", 8), 9, y0+84)

    # 6. BOTTOM BAND (Map on right, briefs on left in 2 columns)
    by = gy + 3 * (grid_h + grid_gap_y) + 6
    draw.line((24, by-6, 1000, by-6), fill=INK, width=1)

    hy = by + 4
    draw.text((24, hy), "ALSO ON THURSDAY 19 NOVEMBER 2026", fill=INK, font=get_font("Sans-Bold", 11))
    draw.text((700, hy), "WHERE IT HAPPENED", fill=ACCENT, font=get_font("Sans-Bold", 11))

    # Continent legend centered
    legend_items = [("Americas", CONT_COLOURS['Americas']), ("Europe", CONT_COLOURS['Europe']),
                    ("Mideast", CONT_COLOURS['Mideast']), ("Africa", CONT_COLOURS['Africa']),
                    ("Asia", CONT_COLOURS['Asia']), ("Oceania", CONT_COLOURS['Oceania'])]

    # Draw legend at top center of bottom band
    leg_x = 330
    for name, col in legend_items:
        draw.ellipse((leg_x, hy+3, leg_x+7, hy+10), fill=col)
        draw.text((leg_x+10, hy+6), name, fill=INK, font=get_font("Sans", 8), anchor="lm")
        leg_x += int(get_font("Sans", 8).getlength(name)) + 22

    briefs_y = hy + 22
    briefs_data = [
        (16, "Berlin:", "Ukraine's allies meet - Merz hosts Macron, Burnham, Tusk, Meloni, Rutte and US envoys Witkoff & Kushner"),
        (17, "Russia:", "fires 98 drones and Onyx missiles overnight; 4 killed, 36 injured across Ukraine in the past day"),
        (18, "Gaza:", "army says the Yellow Line operation is complete; movement restored, Salahudeen road reopened"),
        (19, "Children:", "Record 589M children - nearly 1 in 4 - lived in war zones in 2025, Save the Children counts"),
        (20, "BOJ:", "Ueda: rate hikes will continue; yen near 160 to the dollar, December move expected"),
        (21, "Walmart:", "beats: Q3 revenue $188.8B, up 5.2%; full-year guidance raised again"),
        (22, "Lenovo:", "posts record $30.2B quarter on AI servers, up 48%; AI revenue $10.8B"),
        (23, "Nigeria:", "Tinubu asks parliament to decriminalise attempted suicide"),
        (24, "India-Japan:", "2+2 opens in Tokyo; missile and maritime tech cooperation agreed"),
        (25, "Seoul:", "entertainment stocks surge - CJ ENM +20% - on hopes China's content ban is thawing"),
        (26, "Washington:", "Lame-duck scramble: Dec 11 funding deadline, 17 Senate days left"),
        (27, "Tennis:", "Ash Barty and Shingo Kunieda elected to the Tennis Hall of Fame; induction next August"),
        (28, "ATP Finals:", "Shelton beats Jodar 7-6, 7-5 in the Turin group stage"),
        (29, "Brazil:", "Lula: no hurry to name the cabinet for his new term starting in January"),
        (30, "Science:", "A sugar from a gut bacterium boosts visceral-fat burning, Duke-NUS researchers find"),
        (31, "Liverpool:", "wins £1M to advance a new antibiotic class for drug-resistant pneumonia"),
        (32, "Alipay+:", "links 50+ global e-wallets to Brazil's Pix instant payments"),
        (33, "Delhi:", "schools reopen as GRAP III pollution curbs are lifted on cleaner air")
    ]

    # Two columns for briefs: col 1 (x=24, w=310), col 2 (x=350, w=310)
    col_w = 310
    col1_briefs = briefs_data[:9]
    col2_briefs = briefs_data[9:]

    f_brief = get_font("Sans", 9)
    line_h = 12

    def draw_brief_column(start_x, start_y, items):
        cy = start_y
        for num, bold_word, rest in items:
            drawn_stories.add(num)
            # Chip at cy
            chip(draw, start_x+8, cy+6, 5.5, num, ACCENT)
            text_str = f"{bold_word} {rest}"
            lines = wrap(text_str, f_brief, col_w - 24)
            for l_idx, line in enumerate(lines):
                # Bold the bold_word on first line
                x_text = start_x + 20
                if l_idx == 0:
                    # Draw bold word
                    draw.text((x_text, cy), bold_word, fill=INK, font=get_font("Sans-Bold", 9))
                    bw = get_font("Sans-Bold", 9).getlength(bold_word + " ")
                    draw.text((x_text + bw, cy), rest if bold_word not in line else line[len(bold_word):].strip(), fill=INK, font=f_brief)
                else:
                    draw.text((x_text, cy), line, fill=INK, font=f_brief)
                cy += line_h
            cy += 4
        return cy

    cy1 = draw_brief_column(24, briefs_y, col1_briefs)
    cy2 = draw_brief_column(350, briefs_y, col2_briefs)
    max_briefs_y = max(cy1, cy2)

    map_top = briefs_y
    map_height = max(180, max_briefs_y - map_top)
    map_left = 680
    map_width = 320
    map_box = (map_left, map_top, map_left + map_width, map_top + map_height)

    # Draw map box background
    draw.rectangle(map_box, fill=(240, 238, 230), outline=BORDER)

    # Draw land cells in map
    rows = len(MAP_SPANS)
    cell_h = map_height / float(rows)
    cols = 73
    cell_w = map_width / float(cols)

    for r_idx in range(1, rows + 1):
        spans = MAP_SPANS.get(r_idx, [])
        lat = 78 - (r_idx - 0.5) * (134.0 / rows)
        for c_start, c_end in spans:
            for c_idx in range(c_start, c_end + 1):
                lon = -168 + (c_idx - 0.5) * (360.0 / cols)
                cont = get_continent(lon, lat)
                col = mute(CONT_COLOURS.get(cont, GREY))
                rx1 = map_left + (c_idx - 1) * cell_w - 0.2
                ry1 = map_top + (r_idx - 1) * cell_h - 0.2
                rx2 = map_left + c_idx * cell_w + 0.2
                ry2 = map_top + r_idx * cell_h + 0.2
                draw.rectangle((rx1, ry1, rx2, ry2), fill=col)

    # Pin data for all 33 stories
    pins_data = {
        1: (114.05, 22.55, 0, -9, 'Asia'),
        2: (4.3, 52.07, -6, -6, 'Europe'),
        3: (-80.2, 25.8, 0, -6, 'Americas'),
        4: (56.3, 26.6, 4, 0, 'Mideast'),
        5: (36.6, 45.3, 6, -4, 'Europe'),
        6: (90.4, 23.8, 6, 0, 'Asia'),
        7: (30.7, 36.9, -8, -6, 'Mideast'),
        8: (126.98, 37.57, 0, -9, 'Asia'),
        9: (114.2, 22.3, 13, 7, 'Asia'),
        10: (-74.0, 40.7, -4, -9, 'Americas'),
        11: (149.1, -35.3, 0, -6, 'Oceania'),
        12: (-77.0, 38.9, -12, -8, 'Americas'),
        13: (80.3, 15.9, 6, 4, 'Asia'),
        14: (32.9, 39.9, -8, 6, 'Mideast'),
        15: (-118.2, 34.05, -6, -6, 'Americas'),
        16: (13.4, 52.5, 8, -6, 'Europe'),
        17: (30.5, 50.4, 8, 4, 'Europe'),
        18: (34.3, 31.4, -10, 8, 'Mideast'),
        19: (31.95, 31.95, 8, 10, 'Mideast'),
        20: (139.7, 35.7, 0, -8, 'Asia'),
        21: (-94.2, 36.4, 0, -6, 'Americas'),
        22: (114.2, 22.3, -15, -9, 'Asia'),
        23: (7.5, 9.1, 0, 0, 'Africa'),
        24: (139.7, 35.7, 13, 6, 'Asia'),
        25: (126.98, 37.57, 11, 8, 'Asia'),
        26: (-77.0, 38.9, 13, 8, 'Americas'),
        27: (144.97, -37.8, 0, -6, 'Oceania'),
        28: (7.7, 45.1, -8, -10, 'Europe'),
        29: (-47.9, -15.8, 0, 4, 'Americas'),
        30: (103.8, 1.35, 0, 4, 'Asia'),
        31: (-2.98, 53.4, -8, -6, 'Europe'),
        32: (-46.6, -23.55, 0, 4, 'Americas'),
        33: (77.2, 28.6, -8, -6, 'Asia')
    }

    for s_id, (lon, lat, dx, dy, cont) in pins_data.items():
        px = map_left + (lon + 168) / 360.0 * map_width + dx
        py = map_top + (78 - lat) / 134.0 * map_height + dy
        pcol = CONT_COLOURS.get(cont, ACCENT)
        chip(draw, px, py, 6.5, s_id, pcol)

    # 7. DATE CHECK STRIP (Full-width strip at bottom, <= 3 lines)
    dc_y = max(max_briefs_y, map_top + map_height) + 12
    draw.rectangle((24, dc_y, 1000, dc_y+42), fill=CARD, outline=DATE_CHECK_RED, width=2)

    # Left red label box
    draw.rectangle((24, dc_y, 86, dc_y+42), fill=DATE_CHECK_RED)
    draw.text((55, dc_y+13), "DATE", fill="white", font=get_font("Sans-Bold", 10), anchor="mm")
    draw.text((55, dc_y+29), "CHECK", fill="white", font=get_font("Sans-Bold", 10), anchor="mm")

    dc_text = "DATE CHECK ✓ Every story on this page happened, or was first reported, on Thursday 19 November 2026. LEFT OUT AS OTHER DAYS' NEWS: EU's €45bn Ukraine loan plan (18 NOV) · Iran fires on Kuwait and Bahrain (18 NOV) · Nvidia results (17 NOV) · Jeffries named US speaker (18 NOV) · Carney on China ties (18 NOV) · Siberia An-12 crash (Tue 17 Nov) · IAEA Yongbyon warning (Wed 18 Nov) · İmamoğlu jailed and banned (Wed 18 Nov) · GTA VI reviews, Metacritic 99 (Wed 18 Nov) · Nasser Hospital strike (Thu 12 Nov)."
    f_dc = get_font("Sans", 8.5)
    lines_dc = wrap(dc_text, f_dc, 890)
    dc_cy = dc_y + 6
    for line in lines_dc[:3]:
        draw.text((96, dc_cy), line, fill=INK, font=f_dc)
        dc_cy += 11

    # Footer
    fy2 = dc_y + 48
    draw.line((24, fy2, 1000, fy2), fill=INK, width=1)
    draw.text((512, fy2+6), "CLAIM = one side's account, not independently confirmed.", fill=INK, font=get_font("Serif-Italic", 9), anchor="ma")
    draw.text((512, fy2+22), "Every story happened or was first reported on Thursday 19 November 2026 · Disputed claims are attributed · Sources: Reuters · AP · AFP · Yonhap · ABS · IMD · ICJ · Save the Children", fill=GREY, font=get_font("Sans", 8), anchor="ma")

    # Save
    out_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "entry.png")
    img.save(out_path, "PNG")

    # Assertions
    print(f"Drawn stories count: {len(drawn_stories)}")
    assert len(drawn_stories) == 33, f"Expected 33 stories drawn, got {len(drawn_stories)}"
    print(f"Pasted featured kinds: {pasted_kinds}")
    assert len(pasted_kinds) == 3, f"Expected 3 featured artworks pasted, got {len(pasted_kinds)}"
    assert clip_failures == 0, f"Clip failures detected: {clip_failures}"
    assert os.path.exists(out_path), "entry.png not generated"
    size_bytes = os.path.getsize(out_path)
    print(f"entry.png size: {size_bytes} bytes")
    assert size_bytes <= 1048576, f"entry.png exceeds 1MB: {size_bytes}"
    print("All draw assertions passed successfully!")

if __name__ == "__main__":
    draw_page()
