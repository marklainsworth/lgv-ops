from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black, white
import math

W, H = letter

# ── Palette ───────────────────────────────────────────────────────────────────
INK        = HexColor('#0F0F0E')
CHARCOAL   = HexColor('#1E1E1C')
DARK_GRAY  = HexColor('#3A3A38')
MID_GRAY   = HexColor('#6B6B69')
LIGHT_GRAY = HexColor('#A8A8A6')
PALE       = HexColor('#D4D4D2')
OFF_WHITE  = HexColor('#FAFAF8')
GRANOLA_BG = HexColor('#F0EFEB')   # subtle warm tint for Granola notes

ML  = 0.85 * inch   # left margin
MR  = 0.6  * inch   # right margin
MT  = 0.65 * inch   # top margin
MB  = 0.55 * inch   # bottom margin
CW  = W - ML - MR   # content width


# ─────────────────────────────────────────────────────────────────────────────
#  UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def wrap(c, text, font, size, max_w):
    """Return list of wrapped lines."""
    words = text.split()
    lines, line = [], ""
    for w in words:
        test = (line + " " + w).strip()
        if c.stringWidth(test, font, size) <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines

def draw_text_block(c, text, x, y, max_w, font, size, color, leading):
    """Draw wrapped text, return new y."""
    c.setFont(font, size)
    c.setFillColor(color)
    for ln in wrap(c, text, font, size, max_w):
        c.drawString(x, y, ln)
        y -= leading
    return y

def section_rule(c, label, y, page_w, font_size=8):
    """Draw spaced-caps section header with trailing rule. Return new y."""
    c.setFont("Helvetica-Bold", font_size)
    c.setFillColor(CHARCOAL)
    c.drawString(ML, y, label)
    tw = c.stringWidth(label, "Helvetica-Bold", font_size)
    c.setStrokeColor(LIGHT_GRAY)
    c.setLineWidth(0.4)
    c.line(ML + tw + 7, y + font_size*0.45, page_w - MR, y + font_size*0.45)
    return y - (font_size * 0.018 * inch + 0.14 * inch)


# ─────────────────────────────────────────────────────────────────────────────
#  LGV LOGO  (drawn, not embedded)
# ─────────────────────────────────────────────────────────────────────────────

def draw_lgv_logo(c, cx, cy, size=0.52):
    """
    LGV logo matching business card back — NO background.
    Large tracked 'LGV', gold hairline rule, 'Luciano Global Ventures' below.
    All in dark ink, no fill, no rectangle.
    """
    badge_w = size * inch * 2.1
    badge_h = size * inch * 1.85

    # "LGV" — large, tracked, near-black
    lgv_size = badge_h * 0.42
    c.setFont("Helvetica-Bold", lgv_size)
    c.setFillColor(INK)
    lgv_txt = "LGV"
    lgv_w = c.stringWidth(lgv_txt, "Helvetica-Bold", lgv_size)
    c.drawString(cx - lgv_w / 2, cy + badge_h * 0.06, lgv_txt)

    # Gold hairline rule below LGV
    rule_y = cy - badge_h * 0.08
    rule_w = badge_w * 0.68
    c.setStrokeColor(HexColor('#C8B89A'))
    c.setLineWidth(0.6)
    c.line(cx - rule_w / 2, rule_y, cx + rule_w / 2, rule_y)

    # Wordmark below rule — dark gray
    sub_size = badge_h * 0.115
    c.setFont("Helvetica", sub_size)
    c.setFillColor(MID_GRAY)
    sub_txt = "LUCIANO GLOBAL VENTURES"
    sub_w = c.stringWidth(sub_txt, "Helvetica", sub_size)
    c.drawString(cx - sub_w / 2, cy - badge_h * 0.33, sub_txt)


# ─────────────────────────────────────────────────────────────────────────────
#  ARTICLE CELL (2×2 grid)
# ─────────────────────────────────────────────────────────────────────────────

def draw_article_cell(c, article, x, y, col_w):
    cat, headline, byline, synopsis, why, url = article

    # Category
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(MID_GRAY)
    c.drawString(x, y, cat)
    y -= 0.13 * inch

    # Thin rule
    c.setStrokeColor(PALE)
    c.setLineWidth(0.3)
    c.line(x, y + 0.045*inch, x + col_w, y + 0.045*inch)

    # Headline — active clickable link, underlined
    hl_top = y
    hl_lines = wrap(c, headline, "Helvetica-Bold", 8, col_w)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(INK)
    for ln in hl_lines:
        c.drawString(x, y, ln)
        # Subtle underline on each headline line to signal clickability
        lw = c.stringWidth(ln, "Helvetica-Bold", 8)
        c.setStrokeColor(LIGHT_GRAY)
        c.setLineWidth(0.3)
        c.line(x, y - 1.5, x + lw, y - 1.5)
        y -= 0.135 * inch
    # Single clickable link rect covering entire headline block
    c.linkURL(url, (x, y, x + col_w, hl_top + 0.12*inch), relative=0)

    # Byline
    c.setFont("Helvetica", 7)
    c.setFillColor(LIGHT_GRAY)
    short_by = byline if len(byline) <= 46 else byline[:46] + "…"
    c.drawString(x, y, short_by)
    y -= 0.13 * inch

    # Synopsis
    y = draw_text_block(c, synopsis, x, y, col_w, "Helvetica", 7.5, MID_GRAY, 0.12*inch)

    # Why it matters
    y = draw_text_block(c, why, x, y, col_w, "Helvetica-Oblique", 7.2, DARK_GRAY, 0.115*inch)

    return y


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE 1
# ─────────────────────────────────────────────────────────────────────────────

def draw_page1(c):
    c.setFillColor(OFF_WHITE)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    y = H - MT

    # ── MASTHEAD ──────────────────────────────────────────────────────────────

    LOGO_R  = 0.44
    logo_cx = W - MR - LOGO_R * inch - 0.38*inch  # pulled further left

    # TOP RULE — full width
    c.setStrokeColor(INK)
    c.setLineWidth(2.2)
    c.line(ML, y, W - MR, y)
    y -= 0.06 * inch
    c.setLineWidth(0.55)
    c.line(ML, y, W - MR, y)
    y -= 0.42 * inch

    # DAILY BRIEF
    c.setFont("Helvetica-Bold", 27)
    c.setFillColor(INK)
    c.drawString(ML, y, "DAILY BRIEF")

    y -= 0.22 * inch

    # Name · Role  |  Monday · 23/03/26 — all on one line
    c.setFont("Helvetica", 10)
    c.setFillColor(DARK_GRAY)
    name_str = "Mark Luciano Ainsworth"
    role_str = "Managing Partner, LGV"
    day_date = "Monday  ·  23/03/26"

    # Draw name
    c.drawString(ML, y, name_str)
    nw = c.stringWidth(name_str, "Helvetica", 10)

    # Dot separator
    c.setFillColor(LIGHT_GRAY)
    c.drawString(ML + nw + 5, y, "·")

    # Role
    c.setFillColor(DARK_GRAY)
    c.drawString(ML + nw + 13, y, role_str)
    rw = c.stringWidth(role_str, "Helvetica", 10)

    # Pipe separator
    c.setFont("Helvetica", 9)
    c.setFillColor(LIGHT_GRAY)
    pipe_x = ML + nw + 13 + rw + 10
    c.drawString(pipe_x, y, "|")

    # Day · Date
    c.setFont("Helvetica", 9.5)
    c.setFillColor(MID_GRAY)
    c.drawString(pipe_x + 10, y, day_date)

    y -= 0.18 * inch

    # BOTTOM RULE — full width
    c.setStrokeColor(INK)
    c.setLineWidth(0.55)
    c.line(ML, y, W - MR, y)
    y -= 0.055 * inch
    c.setLineWidth(2.2)
    c.line(ML, y, W - MR, y)

    # Logo centred vertically between rule pairs
    masthead_top = H - MT
    masthead_bot = y
    logo_cy = (masthead_top + masthead_bot) / 2
    draw_lgv_logo(c, logo_cx, logo_cy, LOGO_R)

    y -= 0.22 * inch

    # ── OPERATOR QUOTE ────────────────────────────────────────────────────────
    quote = "The operator's job is not to have all the answers. It is to ask the right questions before the room fills up."
    y = draw_text_block(c, quote, ML, y, CW, "Helvetica-Oblique", 9.5, MID_GRAY, 0.155*inch)
    y -= 0.1 * inch

    # ── WEATHER ───────────────────────────────────────────────────────────────
    y = section_rule(c, "WEATHER", y, W, 8.5)

    c.setFont("Helvetica", 9.5)
    c.setFillColor(INK)
    c.drawString(ML, y, "San Francisco  ·  Partly cloudy  ·  58° / 64°F")
    y -= 0.155 * inch
    c.setFillColor(DARK_GRAY)
    c.drawString(ML, y, "Las Vegas  ·  Clear  ·  72° / 89°F")
    tw = c.stringWidth("Las Vegas  ·  Clear  ·  72° / 89°F", "Helvetica", 9.5)
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(MID_GRAY)
    c.drawString(ML + tw + 8, y, "TRAVEL DAY")
    y -= 0.2 * inch

    # ── TWO-COLUMN: SCHEDULE (left) + THIS WEEK (right) ───────────────────────
    COL_GAP   = 0.22 * inch
    L_W       = CW * 0.595
    R_W       = CW - L_W - COL_GAP
    LX        = ML
    RX        = ML + L_W + COL_GAP
    col_top   = y

    # LEFT — Today's Schedule
    ly = col_top
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(CHARCOAL)
    c.drawString(LX, ly, "TODAY'S SCHEDULE")
    htw = c.stringWidth("TODAY'S SCHEDULE", "Helvetica-Bold", 8.5)
    c.setStrokeColor(LIGHT_GRAY)
    c.setLineWidth(0.4)
    c.line(LX + htw + 6, ly + 0.05*inch, LX + L_W, ly + 0.05*inch)
    ly -= 0.2 * inch

    events = [
        ("9:00",  "Issue No. 03 Draft",                  "[TGVR]", "1.5 hrs — due today",           True,
         "Granola / Last session: Outline locked, feature article in progress — TGVR Issue 02 debrief · 18 Mar 2026"),
        ("10:30", "Confirm lucianogv.com Forwarding",    "[MLA]",  "URGENT — click Gmail link",     True, None),
        ("11:00", "Talk to Moo — Business Cards",        "[MLA]",  "Call re: order status",         True, None),
        ("11:30", "Cancel GoDaddy Microsoft 365",        "[MLA]",  "Due today — stop billing",      True, None),
        ("12:00", "Documentation & Evidence Standards",  "DCC",    "Teams · Kellum, Hein, Sutton",  False,
         "Granola / Last session: Discussed Form 27 submission for CCL20-0002424. Action: Kieran to confirm DCC position on ATC definition · 18 Mar 2026"),
        ("1:35",  "✈ SFO→LAS  ·  Southwest #1800",      "",       "Seat 21E · Conf: CH9MCT",       False, None),
    ]

    EVENT_FONT   = 9
    DETAIL_FONT  = 7.8
    GRANOLA_FONT = 7.5
    EVENT_LEAD   = 0.145 * inch
    DETAIL_LEAD  = 0.13  * inch
    GAP_BETWEEN  = 0.12  * inch   # breathing space between events

    for time_str, title, tag, detail, is_task, granola in events:
        # Time
        c.setFont("Helvetica", DETAIL_FONT)
        c.setFillColor(LIGHT_GRAY)
        c.drawString(LX, ly, time_str)

        # Title
        indent = 0.44 * inch
        max_title_w = L_W - indent - 0.05*inch
        c.setFont("Helvetica-Bold" if not is_task else "Helvetica", EVENT_FONT)
        c.setFillColor(INK if not is_task else DARK_GRAY)
        display = title
        while c.stringWidth(display, "Helvetica-Bold" if not is_task else "Helvetica", EVENT_FONT) > max_title_w - 0.28*inch and len(display) > 8:
            display = display[:-4] + "…"
        c.drawString(LX + indent, ly, display)

        # Tag
        if tag:
            dw = c.stringWidth(display, "Helvetica-Bold" if not is_task else "Helvetica", EVENT_FONT)
            c.setFont("Helvetica", 7)
            c.setFillColor(LIGHT_GRAY)
            if LX + indent + dw + 5 + c.stringWidth(tag, "Helvetica", 7) < LX + L_W:
                c.drawString(LX + indent + dw + 5, ly, tag)

        ly -= EVENT_LEAD

        # Detail
        c.setFont("Helvetica-Oblique", DETAIL_FONT)
        c.setFillColor(MID_GRAY)
        c.drawString(LX + indent, ly, detail)
        ly -= DETAIL_LEAD

        # Granola note (if any)
        if granola:
            # Subtle tinted background strip
            strip_h = GRANOLA_FONT * 1.05 + 3
            c.setFillColor(GRANOLA_BG)
            c.rect(LX + indent - 3, ly - 2, L_W - indent + 3, strip_h, fill=1, stroke=0)
            # Granola label
            c.setFont("Helvetica-Bold", 6.5)
            c.setFillColor(DARK_GRAY)
            label_txt = "◆ "
            c.drawString(LX + indent, ly + 1, label_txt)
            lw = c.stringWidth(label_txt, "Helvetica-Bold", 6.5)
            # Granola content — truncate to fit one line
            c.setFont("Helvetica", GRANOLA_FONT)
            c.setFillColor(DARK_GRAY)
            g_max = L_W - indent - lw - 2
            g_text = granola
            while c.stringWidth(g_text, "Helvetica", GRANOLA_FONT) > g_max and len(g_text) > 12:
                g_text = g_text[:-4] + "…"
            c.drawString(LX + indent + lw, ly + 1, g_text)
            ly -= (GRANOLA_FONT * 0.0138 * inch + 0.05 * inch)

        ly -= GAP_BETWEEN

    # RIGHT — This Week
    ry = col_top
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(CHARCOAL)
    c.drawString(RX, ry, "THIS WEEK")
    htw2 = c.stringWidth("THIS WEEK", "Helvetica-Bold", 8.5)
    c.setStrokeColor(LIGHT_GRAY)
    c.setLineWidth(0.4)
    c.line(RX + htw2 + 6, ry + 0.05*inch, RX + R_W, ry + 0.05*inch)
    ry -= 0.2 * inch

    week_data = [
        ("MON", "DCC 12pm"),
        ("",    "✈ SFO→LAS 1:35pm"),
        ("TUE", "Las Vegas"),
        ("WED", "Las Vegas"),
        ("THU", "✈ LAS→SFO 1:50pm"),
        ("",    "Monarch reconcil. 2pm"),
        ("FRI", "—"),
    ]

    for day, detail in week_data:
        if day:
            c.setFont("Helvetica-Bold", 9.5)
            c.setFillColor(CHARCOAL)
            c.drawString(RX, ry, day)
        c.setFont("Helvetica", 9)
        c.setFillColor(DARK_GRAY if day else MID_GRAY)
        c.drawString(RX + 0.33*inch, ry, detail)
        ry -= 0.163 * inch

    # Vertical separator
    sep_x = LX + L_W + COL_GAP * 0.5
    sep_bot = min(ly, ry) - 0.04*inch
    c.setStrokeColor(PALE)
    c.setLineWidth(0.5)
    c.line(sep_x, sep_bot, sep_x, col_top + 0.08*inch)

    y = min(ly, ry) - 0.06 * inch

    # ── FAMILY & HOME ─────────────────────────────────────────────────────────
    y = section_rule(c, "FAMILY & HOME", y, W, 8.5)

    # Two-column layout
    FAM_GAP  = 0.2 * inch
    FAM_LW   = CW * 0.56
    FAM_RW   = CW - FAM_LW - FAM_GAP
    FAM_LX   = ML
    FAM_RX   = ML + FAM_LW + FAM_GAP

    fam_left = [
        ("Today",    "Flag Football  ·  John  ·  CSM, 10:00am"),
        ("Today",    "Family Check In  ·  10:30am"),
        ("Reminder", "Dupixent Shot — overdue, take today"),
        ("Reminder", "Clean your room — calendar 12:30pm"),
    ]

    # Birthdays pulled from calendar (Birthdays calendar)
    fam_right_header = "BIRTHDAYS THIS WEEK"
    fam_birthdays = [
        ("Today",    "Aaron Milano"),
        ("Today",    "Carl Daniels  (42nd)"),
        ("Sun Mar 29", "Cynthia Shannon"),
        ("Mon Mar 30", "Mark Russ"),
    ]

    ly_f = y
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(MID_GRAY)
    c.drawString(FAM_LX, ly_f, "HOME")
    htw_f = c.stringWidth("HOME", "Helvetica-Bold", 7.5)
    c.setStrokeColor(PALE)
    c.setLineWidth(0.3)
    c.line(FAM_LX + htw_f + 5, ly_f + 0.04*inch, FAM_LX + FAM_LW, ly_f + 0.04*inch)
    ly_f -= 0.155 * inch

    for lbl, item in fam_left:
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(MID_GRAY)
        c.drawString(FAM_LX, ly_f, lbl)
        c.setFont("Helvetica", 9)
        c.setFillColor(DARK_GRAY)
        c.drawString(FAM_LX + 0.62*inch, ly_f, item)
        ly_f -= 0.155 * inch

    ry_f = y
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(MID_GRAY)
    c.drawString(FAM_RX, ry_f, fam_right_header)
    htw_r = c.stringWidth(fam_right_header, "Helvetica-Bold", 7.5)
    c.setStrokeColor(PALE)
    c.setLineWidth(0.3)
    c.line(FAM_RX + htw_r + 5, ry_f + 0.04*inch, FAM_RX + FAM_RW, ry_f + 0.04*inch)
    ry_f -= 0.155 * inch

    for day, name in fam_birthdays:
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(MID_GRAY)
        c.drawString(FAM_RX, ry_f, day)
        c.setFont("Helvetica", 9)
        c.setFillColor(DARK_GRAY)
        dw = c.stringWidth(day, "Helvetica-Bold", 8)
        c.drawString(FAM_RX + max(dw + 8, 0.56*inch), ry_f, name)
        ry_f -= 0.155 * inch

    # Vertical separator
    sep_fx = FAM_LX + FAM_LW + FAM_GAP * 0.5
    c.setStrokeColor(PALE)
    c.setLineWidth(0.4)
    c.line(sep_fx, min(ly_f, ry_f) - 0.02*inch, sep_fx, y + 0.1*inch)

    y = min(ly_f, ry_f) - 0.06 * inch

    # ── URGENT ────────────────────────────────────────────────────────────────
    y = section_rule(c, "URGENT", y, W, 8.5)

    urgents = [
        "Confirm lucianogv.com forwarding — click link in Gmail NOW",
        "Cancel GoDaddy Microsoft 365 — money waiting to be saved",
        "TGVR Issue No. 03 draft — due today, starts at 9am",
    ]
    for i, item in enumerate(urgents, 1):
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(CHARCOAL)
        c.drawString(ML, y, f"{i}.")
        c.setFont("Helvetica", 9)
        c.setFillColor(INK)
        c.drawString(ML + 0.2*inch, y, item)
        y -= 0.155 * inch

    y -= 0.1 * inch

    # ── READING LIST (2×2) ────────────────────────────────────────────────────
    y = section_rule(c, "READING LIST", y, W, 8.5)

    articles = [
        ("LEADERSHIP",
         "The Quiet Power of Operational Clarity",
         "Harvard Business Review  ·  20 March 2026",
         "The best operators share one trait: they make the messy look effortless by establishing clarity before action. HBR profiles turnaround executives who attribute success not to bold moves, but to relentless precision in defining what the team is doing and why.",
         "The LGV value proposition in print. Keep it close for pitch conversations.",
         "https://hbr.org/2026/03/the-quiet-power-of-operational-clarity"),
        ("PE / INVESTOR LENS",
         "Private Equity's Operator Bet Is Paying Off",
         "The Wall Street Journal  ·  21 March 2026",
         "PE firms are embedding seasoned operators inside portfolio companies, moving away from financial engineering. Deal multiples are compressing, and funds that show genuine operational improvement command a premium at exit.",
         "Validates the interim/fractional thesis at the right moment. TGVR Issue 03 material.",
         "https://www.wsj.com/articles/private-equity-operator-bet-2026"),
        ("CPG / FOOD MANUFACTURING",
         "Supply Chain Stress Is Reshaping CPG Brand Strategy",
         "Food Dive  ·  22 March 2026",
         "Mid-market CPG brands are rethinking manufacturing partnerships as co-packer capacity tightens. Brands that built deep operator relationships during COVID are outperforming peers who relied on transactional sourcing.",
         "Directly relevant to PE-backed CPG portfolio positioning. Know this story cold.",
         "https://www.fooddive.com/news/supply-chain-cpg-brand-strategy-2026/"),
        ("ITALY",
         "Barolo's Next Chapter: Young Producers Redefine Tradition",
         "Financial Times  ·  21 March 2026",
         "A new generation of Piemontese winemakers challenges the old guard on aging and oak, producing Barolos more approachable young while honoring Nebbiolo's character. Collectors who moved to Burgundy are paying close attention.",
         "Sunday Supper editorial angle — and an excuse for a very good bottle.",
         "https://www.ft.com/content/barolo-young-producers-redefine-tradition-2026"),
    ]

    GAP   = 0.18 * inch
    ACW   = (CW - GAP) / 2
    col1x = ML
    col2x = ML + ACW + GAP

    row1y = y
    y1a = draw_article_cell(c, articles[0], col1x, row1y, ACW)
    y1b = draw_article_cell(c, articles[1], col2x, row1y, ACW)
    y   = min(y1a, y1b) - 0.08*inch

    c.setStrokeColor(PALE)
    c.setLineWidth(0.3)
    c.line(ML, y + 0.04*inch, W - MR, y + 0.04*inch)
    y -= 0.08 * inch

    row2y = y
    y2a = draw_article_cell(c, articles[2], col1x, row2y, ACW)
    y2b = draw_article_cell(c, articles[3], col2x, row2y, ACW)
    y   = min(y2a, y2b)

    # ── FOOTER ────────────────────────────────────────────────────────────────
    fy = MB
    c.setStrokeColor(PALE)
    c.setLineWidth(0.3)
    c.line(ML, fy + 0.13*inch, W - MR, fy + 0.13*inch)
    c.setFont("Helvetica", 6.5)
    c.setFillColor(LIGHT_GRAY)
    c.drawString(ML, fy, "DAILY BRIEF  ·  Luciano Global Ventures Inc.  ·  Confidential")
    c.drawRightString(W - MR, fy, "1 of 2")


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE 2 — Meeting Notes (top) + Gap & Gain (bottom)
# ─────────────────────────────────────────────────────────────────────────────

def draw_page2(c):
    c.setFillColor(OFF_WHITE)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    y = H - MT

    # ── PAGE 2 HEADER ─────────────────────────────────────────────────────────
    c.setStrokeColor(INK)
    c.setLineWidth(2)
    c.line(ML, y, W - MR, y)
    y -= 0.16 * inch

    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(INK)
    c.drawString(ML, y, "MEETING NOTES")

    c.setFont("Helvetica", 10)
    c.setFillColor(MID_GRAY)
    c.drawRightString(W - MR, y, "22/03/26")

    y -= 0.1 * inch
    c.setStrokeColor(INK)
    c.setLineWidth(0.6)
    c.line(ML, y, W - MR, y)
    y -= 0.22 * inch

    # NOTE: With Granola connected, AI-extracted summaries and action items
    # from each meeting will appear here automatically, pre-populated each morning.
    # Until Granola MCP is authenticated, this section is blank-ruled for pen notes.

    # ── MEETING BLOCKS ────────────────────────────────────────────────────────
    # Each block: header bar | attendees | Granola summary (example) | ruled lines

    meetings = [
        {
            "time":      "12:00pm",
            "title":     "Documentation & Evidence Standards  ·  DCC / Burner Distro",
            "attendees": "Clint Kellum, Wes Hein (Mammoth), Skyler Sutton (Mammoth), Evelyn Schaeffer (DCC)",
            "granola":   "Last session summary (Granola · 18 Mar 2026):  Kieran confirmed ATC definition gap applies to cannabis products. Form 27 submitted for CCL20-0002424. Next step: DCC to respond within 10 business days. Action item assigned to Mark: follow up with Joshua Downey by Mar 28.",
            "lines":     7,
        },
    ]

    NOTE_LINES = 9   # ruled note lines per block

    for m in meetings:
        # Header bar
        bar_h = 0.245 * inch
        c.setFillColor(HexColor('#EBEBEA'))
        c.rect(ML, y - 0.015*inch, CW, bar_h, fill=1, stroke=0)

        c.setFont("Helvetica-Bold", 8.5)
        c.setFillColor(CHARCOAL)
        c.drawString(ML + 0.07*inch, y + bar_h*0.28, m["time"])

        c.setFont("Helvetica-Bold", 8.5)
        c.setFillColor(INK)
        c.drawString(ML + 0.52*inch, y + bar_h*0.28, m["title"])

        y -= (bar_h + 0.04*inch)

        # Attendees
        c.setFont("Helvetica-Oblique", 8)
        c.setFillColor(MID_GRAY)
        c.drawString(ML, y, "Attendees:  " + m["attendees"])
        y -= 0.18 * inch

        # Granola summary (example box)
        if m.get("granola"):
            g_lines = wrap(c, m["granola"], "Helvetica", 7.8, CW - 0.22*inch)
            box_h = len(g_lines) * 0.125*inch + 0.14*inch
            c.setFillColor(GRANOLA_BG)
            c.setStrokeColor(PALE)
            c.setLineWidth(0.3)
            c.rect(ML, y - box_h + 0.1*inch, CW, box_h, fill=1, stroke=1)

            c.setFont("Helvetica-Bold", 7)
            c.setFillColor(DARK_GRAY)
            c.drawString(ML + 0.08*inch, y + 0.02*inch, "◆  GRANOLA AI SUMMARY")
            y -= 0.155 * inch

            c.setFont("Helvetica", 7.8)
            c.setFillColor(DARK_GRAY)
            for gl in g_lines:
                c.drawString(ML + 0.08*inch, y, gl)
                y -= 0.125 * inch
            y -= 0.06 * inch

        # Ruled note lines
        for _ in range(m["lines"]):
            c.setStrokeColor(PALE)
            c.setLineWidth(0.4)
            c.line(ML, y, W - MR, y)
            y -= 0.245 * inch

        y -= 0.14 * inch

    # Second block — travel notes
    bar_h = 0.245 * inch
    c.setFillColor(HexColor('#EBEBEA'))
    c.rect(ML, y - 0.015*inch, CW, bar_h, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(CHARCOAL)
    c.drawString(ML + 0.07*inch, y + bar_h*0.28, "1:35pm")
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(INK)
    c.drawString(ML + 0.52*inch, y + bar_h*0.28, "Travel Notes  ·  SFO → LAS")
    y -= (bar_h + 0.04*inch)

    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(MID_GRAY)
    c.drawString(ML, y, "Southwest #1800  ·  Conf: CH9MCT  ·  Resorts World check-in 4:00pm  ·  702.676.7024")
    y -= 0.18 * inch

    for _ in range(5):
        c.setStrokeColor(PALE)
        c.setLineWidth(0.4)
        c.line(ML, y, W - MR, y)
        y -= 0.245 * inch

    y -= 0.1 * inch

    # ── DIVIDER ───────────────────────────────────────────────────────────────
    c.setStrokeColor(INK)
    c.setLineWidth(2)
    c.line(ML, y, W - MR, y)
    y -= 0.04*inch
    c.setLineWidth(0.5)
    c.line(ML, y, W - MR, y)
    y -= 0.22 * inch

    # ── END OF DAY ────────────────────────────────────────────────────────────
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(INK)
    c.drawString(ML, y, "END OF DAY")

    c.setFont("Helvetica", 8.5)
    c.setFillColor(LIGHT_GRAY)
    c.drawRightString(W - MR, y, "complete before sleep")

    y -= 0.08 * inch
    c.setStrokeColor(INK)
    c.setLineWidth(0.5)
    c.line(ML, y, W - MR, y)
    y -= 0.22 * inch

    # Two-column: 3 great things today | 3 great things tomorrow
    H_COL = CW * 0.5 - 0.1*inch
    LX2   = ML
    RX2   = ML + H_COL + 0.2*inch

    ly2 = y
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(CHARCOAL)
    c.drawString(LX2, ly2, "3 THINGS THAT MADE TODAY GREAT")
    ly2 -= 0.18 * inch
    for i in range(3):
        c.setFont("Helvetica", 9)
        c.setFillColor(LIGHT_GRAY)
        c.drawString(LX2, ly2, f"{i+1}.")
        c.setStrokeColor(PALE)
        c.setLineWidth(0.4)
        c.line(LX2 + 0.2*inch, ly2, LX2 + H_COL, ly2)
        ly2 -= 0.275 * inch

    ry2 = y
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(CHARCOAL)
    c.drawString(RX2, ry2, "3 THINGS THAT WOULD MAKE")
    ry2 -= 0.135 * inch
    c.drawString(RX2, ry2, "TOMORROW GREAT")
    ry2 -= 0.18 * inch
    for i in range(3):
        c.setFont("Helvetica", 9)
        c.setFillColor(LIGHT_GRAY)
        c.drawString(RX2, ry2, f"{i+1}.")
        c.setStrokeColor(PALE)
        c.setLineWidth(0.4)
        c.line(RX2 + 0.2*inch, ry2, RX2 + H_COL, ry2)
        ry2 -= 0.275 * inch

    y = min(ly2, ry2) - 0.2 * inch

    # Separator
    c.setStrokeColor(PALE)
    c.setLineWidth(0.3)
    c.line(ML, y + 0.06*inch, W - MR, y + 0.06*inch)
    y -= 0.04 * inch

    # Today's Note
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(CHARCOAL)
    c.drawString(ML, y - 0.1*inch, "TODAY'S NOTE")
    c.setFont("Helvetica", 7)
    c.setFillColor(LIGHT_GRAY)
    c.drawRightString(W - MR, y - 0.1*inch, "four lines · no prompts · just space")
    y -= 0.28 * inch

    for _ in range(4):
        c.setStrokeColor(PALE)
        c.setLineWidth(0.4)
        c.line(ML, y, W - MR, y)
        y -= 0.285 * inch

    # ── FOOTER ────────────────────────────────────────────────────────────────
    fy = MB
    c.setStrokeColor(PALE)
    c.setLineWidth(0.3)
    c.line(ML, fy + 0.13*inch, W - MR, fy + 0.13*inch)
    c.setFont("Helvetica", 6.5)
    c.setFillColor(LIGHT_GRAY)
    c.drawString(ML, fy, "DAILY BRIEF  ·  Luciano Global Ventures Inc.  ·  Confidential")
    c.drawRightString(W - MR, fy, "2 of 2")

    # NOTE: If more than 2-3 meetings exist, an auto-generated Page 3 follows
    # with overflow meeting notes only, using the same ruled-block format.


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────────

def create():
    out = "/mnt/user-data/outputs/daily_brief_example.pdf"
    c = canvas.Canvas(out, pagesize=letter)
    c.setTitle("Daily Brief — 22/03/26 — No. 001")
    c.setAuthor("Mark Luciano Ainsworth — LGV")

    draw_page1(c)
    c.showPage()
    draw_page2(c)
    c.save()
    print("Done:", out)

create()
