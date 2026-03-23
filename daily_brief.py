from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

W, H = letter

# ── Palette — maximum contrast for e-ink ─────────────────────────────────────
INK        = HexColor('#000000')   # pure black
CHARCOAL   = HexColor('#0F0F0E')   # near black
DARK_GRAY  = HexColor('#1A1A18')   # very dark — used for most body text
MID_GRAY   = HexColor('#2A2A28')   # dark gray — nothing lighter than this
LIGHT_GRAY = HexColor('#2A2A28')   # same as MID — no more washout
PALE       = HexColor('#888888')   # rules — solid and visible
OFF_WHITE  = HexColor('#FAFAF8')
GRANOLA_BG = HexColor('#EBEBEA')
GOLD       = HexColor('#C8B89A')

ML  = 0.85 * inch
MR  = 0.6  * inch
MT  = 0.65 * inch
MB  = 0.55 * inch
CW  = W - ML - MR

# ── Font size scale — bumped throughout ──────────────────────────────────────
# Desktop → reMarkable mapping:
#   6.5pt  → 8pt
#   7pt    → 9pt
#   7.2pt  → 9pt
#   7.5pt  → 9.5pt
#   7.8pt  → 9.5pt
#   8pt    → 10pt
#   8.5pt  → 11pt
#   9pt    → 11pt
#   9.5pt  → 12pt
#   10pt   → 12pt
#   13pt   → 15pt
#   27pt   → 28pt (masthead stays close)

# ─────────────────────────────────────────────────────────────────────────────
#  LIVE DATA
# ─────────────────────────────────────────────────────────────────────────────

DATA = {
    "day_name":       "Sunday",
    "date_str":       "22/03/26",
    "operator_quote": '"Confine yourself to the present." — Marcus Aurelius, Meditations',
    "weather_home":   "San Francisco  ·  Partly cloudy → sunny  ·  Low 52°  High 70°F  ·  W winds 5–10 mph",
    "weather_travel": "Las Vegas  ·  Sunny, record heat wave  ·  Low 65°  High 92°F  ·  Extreme heat advisory",
    "travel_label":   "Traveling Tomorrow",
    "week_events": [
        ("MON", "Issue 03 Draft [TGVR]  9:00am"),
        ("",    "DCC / Burner Distro  12:00pm"),
        ("",    "✈ SFO→LAS SW#1800  1:35pm"),
        ("TUE", "Las Vegas — Resorts World"),
        ("WED", "Las Vegas — Resorts World"),
        ("THU", "✈ LAS→SFO SW#1718  1:50pm"),
        ("FRI", "Monarch reconciliation  2:00pm"),
    ],
    "schedule": [
        ("10:00", "Flag Football — John",         "",        "College of San Mateo · CSM Field",     True,  None),
        ("10:30", "Ainsworth Family Check In",    "",        "Weekly · Bonnie + Mark",               True,  None),
        ("12:00", "Dupixent Shot",               "[MLA]",   "OVERDUE since Dec 10 — do today",      False, None),
        ("12:30", "Clean Your Room",             "[Family]","30 min — overdue from Mar 22",          False, None),
        ("17:00", "Apollo | TuttoFood Outreach", "[MLA]",   "Turn on — Motion task",                False, None),
    ],
    "family_home": [
        ("Today",  "Flag Football  ·  John  ·  CSM, 10:00am"),
        ("Today",  "Family Check In  ·  10:30am"),
        ("O/DUE",  "Dupixent Shot — overdue since Dec 10"),
        ("Today",  "Clean your room — overdue"),
    ],
    "birthdays": [
        ("Mon Mar 23", "Aaron Milano"),
        ("Mon Mar 23", "Carl Daniels  (42nd)"),
    ],
    "urgent": [
        "Confirm lucianogv.com email forwarding — DONE, verified",
        "Dupixent Shot — severely overdue (since Dec 10, 2025) — take today",
        "Cancel GoDaddy Microsoft 365 — due Monday, stop billing before you board",
        "TGVR Issue No. 03 draft — due Monday, 1.5 hrs starting 9:00am",
        "Talk to Moo about Business Cards — overdue from yesterday",
    ],
    "articles": [
        (
            "LEADERSHIP",
            "COO Excellence: The Next Generation of Leadership",
            "McKinsey Talks Operations  ·  13 March 2026",
            "The COO role now sits at the intersection of strategy, execution, and CEO partnership. McKinsey maps the five-part framework: vision, plan, relationships, talent, personal operating model.",
            "The LGV mandate in print. Read before your next intro call with a PE sponsor.",
            "https://www.mckinsey.com/capabilities/operations/our-insights/coo-excellence-the-next-generation-of-leadership"
        ),
        (
            "PE / INVESTOR LENS",
            "Ontario Teachers' Overhauls PE Approach After First Loss in 16 Years",
            "Bloomberg  ·  10 March 2026",
            "The $200B fund booked its first PE loss since 2009 — down C$10B — and is retrenching to three sectors only: financial services, technology, and services.",
            "PE firms showing genuine operational improvement will command a premium at exit. TGVR Issue 03 material.",
            "https://www.bloomberg.com/news/articles/2026-03-10/spacex-gold-drive-gains-at-ontario-teachers-despite-private-equity-losses"
        ),
        (
            "CPG / FOOD MANUFACTURING",
            "Ingredient Supply Chain Strategies in 2026: Domestic Sourcing Now a Must",
            "Food Business News  ·  January 2026",
            "Tariff pressure is forcing a hard shift toward domestic sourcing for vanilla, pea protein, and cocoa. Pre-tariff resilience builders are clearly outperforming.",
            "Know the domestic sourcing argument cold — it is showing up in every PE portfolio board deck.",
            "https://www.foodbusinessnews.net/articles/29581-ingredient-supply-chain-strategies-in-2026"
        ),
        (
            "ITALY  ·  SUNDAY WILDCARD",
            "Italian Wine Exports Cross €8 Billion — Restaurants Still Pour Local",
            "ItalianFood.net  ·  12 March 2026",
            "Italy hits €8B in annual exports yet 70–75% of restaurant lists stay hyper-regional. Rising trend: one quality glass over a cheap bottle.",
            "Sunday Supper editorial angle — the hyperlocal wine story is a great hook for a regional Italian menu post.",
            "https://news.italianfood.net/2026/03/12/italian-wine-conquers-global-markets/"
        ),
    ],
    "meetings": [
        {
            "time":      "MON 12:00pm",
            "title":     "Documentation & Evidence Standards  ·  DCC / Burner Distro",
            "attendees": "Clint Kellum (DCC), Wes Hein (Mammoth), Skyler Sutton (Mammoth), Evelyn Schaeffer (DCC)",
            "platform":  "Microsoft Teams  ·  ID: 277 747 295 950 95  ·  Passcode: Q6eS2Lj6",
            "granola":   None,
            "lines":     8,
        },
        {
            "time":      "MON 1:35pm",
            "title":     "✈  SFO → LAS  ·  Southwest #1800",
            "attendees": "Solo travel",
            "platform":  "Seat 21E  ·  Conf: CH9MCT  ·  Resorts World check-in 4:00pm  ·  702.676.7024",
            "granola":   None,
            "lines":     5,
        },
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
#  UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def wrap(c, text, font, size, max_w):
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
    c.setFont(font, size)
    c.setFillColor(color)
    for ln in wrap(c, text, font, size, max_w):
        c.drawString(x, y, ln)
        y -= leading
    return y

def section_rule(c, label, y, font_size=11):
    """Section header with trailing rule — bumped to 11pt for reMarkable."""
    c.setFont("Helvetica-Bold", font_size)
    c.setFillColor(CHARCOAL)
    c.drawString(ML, y, label)
    tw = c.stringWidth(label, "Helvetica-Bold", font_size)
    c.setStrokeColor(PALE)
    c.setLineWidth(0.9)   # was 0.4 — heavier for e-ink
    c.line(ML + tw + 7, y + font_size * 0.45, W - MR, y + font_size * 0.45)
    return y - 0.24 * inch

# ─────────────────────────────────────────────────────────────────────────────
#  LGV LOGO
# ─────────────────────────────────────────────────────────────────────────────

def draw_lgv_logo(c, cx, cy, size=0.52):
    badge_h = size * inch * 1.85
    badge_w = size * inch * 2.1
    lgv_size = badge_h * 0.42
    # Draw LGV with manual letter spacing
    letter_gap = lgv_size * 0.18
    c.setFont("Helvetica-Bold", lgv_size)
    c.setFillColor(INK)
    lw = c.stringWidth("L", "Helvetica-Bold", lgv_size)
    gw = c.stringWidth("G", "Helvetica-Bold", lgv_size)
    vw = c.stringWidth("V", "Helvetica-Bold", lgv_size)
    total_w = lw + gw + vw + 2 * letter_gap
    lx = cx - total_w / 2
    ly = cy + badge_h * 0.06
    c.drawString(lx, ly, "L")
    c.drawString(lx + lw + letter_gap, ly, "G")
    c.drawString(lx + lw + letter_gap + gw + letter_gap, ly, "V")
    # Rule — pure black
    rule_y = cy - badge_h * 0.08
    rule_w = badge_w * 0.72
    c.setStrokeColor(INK)
    c.setLineWidth(1.0)
    c.line(cx - rule_w / 2, rule_y, cx + rule_w / 2, rule_y)
    # Wordmark — pure black
    sub_size = badge_h * 0.115
    c.setFont("Helvetica", sub_size)
    c.setFillColor(INK)
    sub_txt = "LUCIANO GLOBAL VENTURES"
    sub_w = c.stringWidth(sub_txt, "Helvetica", sub_size)
    c.drawString(cx - sub_w / 2, cy - badge_h * 0.33, sub_txt)

# ─────────────────────────────────────────────────────────────────────────────
#  ARTICLE CELL
# ─────────────────────────────────────────────────────────────────────────────

def draw_article_cell(c, article, x, y, col_w, floor_y=None):
    """Draw article cell. floor_y is a hard bottom — nothing draws below it."""
    cat, headline, byline, synopsis, why, url = article
    top_y = y

    def ok(cur_y, margin=0.10):
        return floor_y is None or cur_y > floor_y + margin * inch

    # Category label
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(INK)
    if ok(y): c.drawString(x, y, cat)
    y -= 0.15 * inch

    # Rule
    c.setStrokeColor(PALE)
    c.setLineWidth(0.6)
    c.line(x, y + 0.045 * inch, x + col_w, y + 0.045 * inch)

    # Headline
    hl_top = y
    hl_lines = wrap(c, headline, "Helvetica-Bold", 10, col_w)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(INK)
    for ln in hl_lines:
        if ok(y):
            c.drawString(x, y, ln)
            hlw = c.stringWidth(ln, "Helvetica-Bold", 10)
            c.setStrokeColor(LIGHT_GRAY)
            c.setLineWidth(0.4)
            c.line(x, y - 1.5, x + hlw, y - 1.5)
        y -= 0.155 * inch
    c.linkURL(url, (x, y, x + col_w, hl_top + 0.14 * inch), relative=0)

    # Byline
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(INK)
    short_by = byline if len(byline) <= 46 else byline[:46] + "…"
    if ok(y): c.drawString(x, y, short_by)
    y -= 0.145 * inch

    # Synopsis — hard cap at 3 lines
    syn_lines = wrap(c, synopsis, "Helvetica", 9.5, col_w)[:3]
    c.setFont("Helvetica", 9.5)
    c.setFillColor(INK)
    for ln in syn_lines:
        if ok(y): c.drawString(x, y, ln)
        y -= 0.138 * inch
    y -= 0.03 * inch

    # Why it matters — hard cap at 2 lines
    why_lines = wrap(c, "▶  " + why, "Helvetica-BoldOblique", 9, col_w)[:2]
    c.setFont("Helvetica-BoldOblique", 9)
    c.setFillColor(INK)
    for ln in why_lines:
        if ok(y): c.drawString(x, y, ln)
        y -= 0.132 * inch

    return y

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE 1
# ─────────────────────────────────────────────────────────────────────────────

def draw_page1(c, data):
    c.setFillColor(OFF_WHITE)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    y = H - MT

    # ── MASTHEAD ──────────────────────────────────────────────────────────────
    LOGO_R  = 0.44
    logo_cx = W - MR - LOGO_R * inch - 0.38 * inch

    c.setStrokeColor(INK)
    c.setLineWidth(2.5)   # slightly heavier
    c.line(ML, y, W - MR, y)
    y -= 0.06 * inch
    c.setLineWidth(0.7)
    c.line(ML, y, W - MR, y)
    y -= 0.32 * inch

    # DAILY BRIEF — 28pt (was 27)
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(INK)
    c.drawString(ML, y, "DAILY BRIEF")
    y -= 0.18 * inch

    # Byline — 12pt (was 10)
    c.setFont("Helvetica", 12)
    c.setFillColor(DARK_GRAY)
    name_str = "Mark Luciano Ainsworth"
    role_str = "Managing Partner, LGV"
    day_date = f"{data['day_name']}  ·  {data['date_str']}"

    c.drawString(ML, y, name_str)
    nw = c.stringWidth(name_str, "Helvetica", 12)
    c.setFillColor(MID_GRAY)
    c.drawString(ML + nw + 5, y, "·")
    c.setFillColor(DARK_GRAY)
    c.drawString(ML + nw + 14, y, role_str)
    rw = c.stringWidth(role_str, "Helvetica", 12)
    c.setFont("Helvetica", 11)
    c.setFillColor(MID_GRAY)
    pipe_x = ML + nw + 14 + rw + 10
    c.drawString(pipe_x, y, "|")
    c.setFont("Helvetica", 11)
    c.setFillColor(MID_GRAY)
    c.drawString(pipe_x + 10, y, day_date)
    y -= 0.20 * inch

    c.setStrokeColor(INK)
    c.setLineWidth(0.7)
    c.line(ML, y, W - MR, y)
    y -= 0.06 * inch
    c.setLineWidth(2.5)
    c.line(ML, y, W - MR, y)

    masthead_top = H - MT
    masthead_bot = y
    logo_cy = (masthead_top + masthead_bot) / 2
    draw_lgv_logo(c, logo_cx, logo_cy, LOGO_R)

    y -= 0.14 * inch

    # ── OPERATOR QUOTE — 11pt (was 9.5) ──────────────────────────────────────
    y = draw_text_block(c, data["operator_quote"], ML, y, CW, "Helvetica-BoldOblique", 11, INK, 0.17 * inch)
    y -= 0.15 * inch

    # ── WEATHER ───────────────────────────────────────────────────────────────
    y = section_rule(c, "WEATHER", y)

    # Weather lines — 11pt (was 9.5)
    c.setFont("Helvetica", 11)
    c.setFillColor(INK)
    c.drawString(ML, y, data["weather_home"])
    y -= 0.175 * inch

    if data.get("weather_travel"):
        c.setFillColor(INK)
        c.drawString(ML, y, data["weather_travel"])
        if data.get("travel_label"):
            tw2 = c.stringWidth(data["weather_travel"], "Helvetica", 11)
            c.setFont("Helvetica-Bold", 9)
            c.setFillColor(INK)
            c.drawString(ML + tw2 + 8, y, data["travel_label"])
    y -= 0.24 * inch

    # ── TWO-COLUMN: SCHEDULE (left) + THIS WEEK (right) ───────────────────────
    COL_GAP = 0.22 * inch
    L_W     = CW * 0.595
    R_W     = CW - L_W - COL_GAP
    LX      = ML
    RX      = ML + L_W + COL_GAP
    col_top = y

    # LEFT — TODAY'S SCHEDULE
    ly = col_top
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(CHARCOAL)
    c.drawString(LX, ly, "TODAY'S SCHEDULE")
    htw = c.stringWidth("TODAY'S SCHEDULE", "Helvetica-Bold", 11)
    c.setStrokeColor(PALE)
    c.setLineWidth(0.8)
    c.line(LX + htw + 6, ly + 0.055 * inch, LX + L_W, ly + 0.055 * inch)
    ly -= 0.22 * inch

    EVENT_FONT  = 11   # was 9
    DETAIL_FONT = 9.5  # was 7.8
    EVENT_LEAD  = 0.165 * inch
    DETAIL_LEAD = 0.148 * inch
    GAP_BETWEEN = 0.12  * inch

    for time_str, title, tag, detail, is_task, granola in data["schedule"]:
        c.setFont("Helvetica-Bold", DETAIL_FONT)
        c.setFillColor(INK)
        c.drawString(LX, ly, time_str)
        indent = 0.48 * inch
        max_title_w = L_W - indent - 0.05 * inch
        fn = "Helvetica" if is_task else "Helvetica-Bold"
        c.setFont(fn, EVENT_FONT)
        c.setFillColor(DARK_GRAY if is_task else INK)
        display = title
        while c.stringWidth(display, fn, EVENT_FONT) > max_title_w - 0.28 * inch and len(display) > 8:
            display = display[:-4] + "…"
        c.drawString(LX + indent, ly, display)
        if tag:
            dw = c.stringWidth(display, fn, EVENT_FONT)
            c.setFont("Helvetica", 8)
            c.setFillColor(MID_GRAY)
            if LX + indent + dw + 5 + c.stringWidth(tag, "Helvetica", 8) < LX + L_W:
                c.drawString(LX + indent + dw + 5, ly, tag)
        ly -= EVENT_LEAD
        c.setFont("Helvetica-Oblique", DETAIL_FONT)
        c.setFillColor(INK)
        c.drawString(LX + indent, ly, detail)
        ly -= DETAIL_LEAD
        if granola:
            strip_h = 9 * 1.05 + 3
            c.setFillColor(GRANOLA_BG)
            c.rect(LX + indent - 3, ly - 2, L_W - indent + 3, strip_h, fill=1, stroke=0)
            c.setFont("Helvetica-Bold", 7.5)
            c.setFillColor(DARK_GRAY)
            label_txt = "◆ "
            c.drawString(LX + indent, ly + 1, label_txt)
            lw2 = c.stringWidth(label_txt, "Helvetica-Bold", 7.5)
            c.setFont("Helvetica", 9)
            c.setFillColor(DARK_GRAY)
            g_max = L_W - indent - lw2 - 2
            g_text = granola
            while c.stringWidth(g_text, "Helvetica", 9) > g_max and len(g_text) > 12:
                g_text = g_text[:-4] + "…"
            c.drawString(LX + indent + lw2, ly + 1, g_text)
            ly -= (9 * 0.0138 * inch + 0.05 * inch)
        ly -= GAP_BETWEEN

    # RIGHT — THIS WEEK
    ry = col_top
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(CHARCOAL)
    c.drawString(RX, ry, "THIS WEEK")
    htw2 = c.stringWidth("THIS WEEK", "Helvetica-Bold", 11)
    c.setStrokeColor(PALE)
    c.setLineWidth(0.8)
    c.line(RX + htw2 + 6, ry + 0.055 * inch, RX + R_W, ry + 0.055 * inch)
    ry -= 0.22 * inch

    for day, detail in data["week_events"]:
        if day:
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(CHARCOAL)
            c.drawString(RX, ry, day)
        c.setFont("Helvetica", 10)
        c.setFillColor(INK)
        c.drawString(RX + 0.36 * inch, ry, detail)
        ry -= 0.175 * inch

    sep_x = LX + L_W + COL_GAP * 0.5
    sep_bot = min(ly, ry) - 0.04 * inch
    c.setStrokeColor(PALE)
    c.setLineWidth(0.6)
    c.line(sep_x, sep_bot, sep_x, col_top + 0.08 * inch)

    y = min(ly, ry) - 0.06 * inch

    # ── FAMILY & HOME ─────────────────────────────────────────────────────────
    y = section_rule(c, "FAMILY & HOME", y)

    FAM_GAP = 0.2 * inch
    FAM_LW  = CW * 0.56
    FAM_RW  = CW - FAM_LW - FAM_GAP
    FAM_LX  = ML
    FAM_RX  = ML + FAM_LW + FAM_GAP

    ly_f = y
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(MID_GRAY)
    c.drawString(FAM_LX, ly_f, "HOME")
    htw_f = c.stringWidth("HOME", "Helvetica-Bold", 9)
    c.setStrokeColor(PALE)
    c.setLineWidth(0.6)
    c.line(FAM_LX + htw_f + 5, ly_f + 0.045 * inch, FAM_LX + FAM_LW, ly_f + 0.045 * inch)
    ly_f -= 0.175 * inch

    for lbl, item in data["family_home"]:
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(MID_GRAY)
        c.drawString(FAM_LX, ly_f, lbl)
        c.setFont("Helvetica", 10)
        c.setFillColor(DARK_GRAY)
        # Fixed indent of 0.52 inch — enough for longest label "O/DUE"
        c.drawString(FAM_LX + 0.52 * inch, ly_f, item)
        ly_f -= 0.168 * inch

    ry_f = y
    bday_hdr = "BIRTHDAYS THIS WEEK"
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(MID_GRAY)
    c.drawString(FAM_RX, ry_f, bday_hdr)
    htw_r = c.stringWidth(bday_hdr, "Helvetica-Bold", 9)
    c.setStrokeColor(PALE)
    c.setLineWidth(0.6)
    c.line(FAM_RX + htw_r + 5, ry_f + 0.045 * inch, FAM_RX + FAM_RW, ry_f + 0.045 * inch)
    ry_f -= 0.175 * inch

    for day, name in data["birthdays"]:
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(MID_GRAY)
        c.drawString(FAM_RX, ry_f, day)
        c.setFont("Helvetica", 10)
        c.setFillColor(INK)
        dw = c.stringWidth(day, "Helvetica-Bold", 10)
        c.drawString(FAM_RX + max(dw + 8, 0.75 * inch), ry_f, name)
        ry_f -= 0.168 * inch

    sep_fx = FAM_LX + FAM_LW + FAM_GAP * 0.5
    c.setStrokeColor(PALE)
    c.setLineWidth(0.5)
    c.line(sep_fx, min(ly_f, ry_f) - 0.02 * inch, sep_fx, y + 0.1 * inch)

    y = min(ly_f, ry_f) - 0.06 * inch

    # ── URGENT ────────────────────────────────────────────────────────────────
    y = section_rule(c, "URGENT", y)

    for i, item in enumerate(data["urgent"], 1):
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(CHARCOAL)
        c.drawString(ML, y, f"{i}.")
        c.setFont("Helvetica", 11)
        c.setFillColor(INK)
        lines = wrap(c, item, "Helvetica", 11, CW - 0.24 * inch)
        for ln in lines:
            c.drawString(ML + 0.22 * inch, y, ln)
            y -= 0.160 * inch
        if not lines:
            y -= 0.160 * inch
        y -= 0.02 * inch

    y -= 0.06 * inch

    # ── READING LIST (2×2) ────────────────────────────────────────────────────
    y = section_rule(c, "READING LIST", y)

    GAP   = 0.18 * inch
    ACW   = (CW - GAP) / 2
    col1x = ML
    col2x = ML + ACW + GAP

    # Calculate available space from current y to footer, split into 2 equal rows
    # Reserve space for: divider rule (0.08) + footer area (MB + 0.2in)
    available = y - MB - 0.18 * inch
    # Each row gets half minus the divider gap (0.16 total: 0.08 above + 0.08 below)
    ROW_H = (available - 0.16 * inch) / 2

    row1y = y
    row1_floor = row1y - ROW_H
    y1a = draw_article_cell(c, data["articles"][0], col1x, row1y, ACW, floor_y=row1_floor)
    y1b = draw_article_cell(c, data["articles"][1], col2x, row1y, ACW, floor_y=row1_floor)
    # Row 2 starts exactly at row1_floor — equal height guaranteed
    y = row1_floor - 0.08 * inch

    c.setStrokeColor(PALE)
    c.setLineWidth(0.6)
    c.line(ML, y + 0.04 * inch, W - MR, y + 0.04 * inch)
    y -= 0.08 * inch

    row2y = y
    row2_floor = row2y - ROW_H
    draw_article_cell(c, data["articles"][2], col1x, row2y, ACW, floor_y=row2_floor)
    draw_article_cell(c, data["articles"][3], col2x, row2y, ACW, floor_y=row2_floor)

    # ── FOOTER — 8pt (was 6.5) ────────────────────────────────────────────────
    fy = MB
    c.setStrokeColor(PALE)
    c.setLineWidth(0.6)
    c.line(ML, fy + 0.13 * inch, W - MR, fy + 0.13 * inch)
    c.setFont("Helvetica", 8)
    c.setFillColor(INK)
    c.drawString(ML, fy, "DAILY BRIEF  ·  Luciano Global Ventures Inc.  ·  Confidential")
    c.drawRightString(W - MR, fy, "1 of 2")


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE 2
# ─────────────────────────────────────────────────────────────────────────────

def draw_page2(c, data):
    c.setFillColor(OFF_WHITE)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    y = H - MT

    # ── PAGE 2 HEADER ─────────────────────────────────────────────────────────
    c.setStrokeColor(INK)
    c.setLineWidth(2.5)
    c.line(ML, y, W - MR, y)
    y -= 0.17 * inch

    c.setFont("Helvetica-Bold", 15)   # was 13
    c.setFillColor(INK)
    c.drawString(ML, y, "MEETING NOTES  ·  MONDAY PREVIEW")

    c.setFont("Helvetica", 12)
    c.setFillColor(MID_GRAY)
    c.drawRightString(W - MR, y, f"{data['date_str']}  →  23/03/26")

    y -= 0.11 * inch
    c.setStrokeColor(INK)
    c.setLineWidth(0.8)
    c.line(ML, y, W - MR, y)
    y -= 0.24 * inch

    # Granola note — 10pt (was 8)
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(INK)
    c.drawString(ML, y, "Granola: not connected this session — ruled lines below are open for pen notes.")
    y -= 0.26 * inch

    # ── MEETING BLOCKS ────────────────────────────────────────────────────────
    for m in data["meetings"]:
        bar_h = 0.27 * inch
        c.setFillColor(HexColor('#E5E5E3'))
        c.rect(ML, y - 0.015 * inch, CW, bar_h, fill=1, stroke=0)

        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(CHARCOAL)
        c.drawString(ML + 0.07 * inch, y + bar_h * 0.28, m["time"])

        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(INK)
        c.drawString(ML + 0.78 * inch, y + bar_h * 0.28, m["title"])
        y -= (bar_h + 0.05 * inch)

        # Attendees — 10pt (was 8)
        c.setFont("Helvetica-Oblique", 10)
        c.setFillColor(INK)
        c.drawString(ML, y, "Attendees:  " + m["attendees"])
        y -= 0.175 * inch

        # Platform — 9.5pt (was 7.8)
        c.setFont("Helvetica-Oblique", 9.5)
        c.setFillColor(INK)
        c.drawString(ML, y, m["platform"])
        y -= 0.195 * inch

        # Ruled note lines — slightly taller spacing
        for _ in range(m["lines"]):
            c.setStrokeColor(PALE)
            c.setLineWidth(0.6)
            c.line(ML, y, W - MR, y)
            y -= 0.265 * inch

        y -= 0.15 * inch

    # ── DIVIDER ───────────────────────────────────────────────────────────────
    c.setStrokeColor(INK)
    c.setLineWidth(2.5)
    c.line(ML, y, W - MR, y)
    y -= 0.045 * inch
    c.setLineWidth(0.7)
    c.line(ML, y, W - MR, y)
    y -= 0.24 * inch

    # ── END OF DAY ────────────────────────────────────────────────────────────
    c.setFont("Helvetica-Bold", 15)   # was 13
    c.setFillColor(INK)
    c.drawString(ML, y, "END OF DAY")
    c.setFont("Helvetica", 10)
    c.setFillColor(INK)
    c.drawRightString(W - MR, y, "complete before sleep")

    y -= 0.09 * inch
    c.setStrokeColor(INK)
    c.setLineWidth(0.7)
    c.line(ML, y, W - MR, y)
    y -= 0.24 * inch

    H_COL = CW * 0.5 - 0.1 * inch
    LX2   = ML
    RX2   = ML + H_COL + 0.2 * inch

    ly2 = y
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(CHARCOAL)
    c.drawString(LX2, ly2, "3 THINGS THAT MADE TODAY GREAT")
    ly2 -= 0.20 * inch
    for i in range(3):
        c.setFont("Helvetica", 11)
        c.setFillColor(MID_GRAY)
        c.drawString(LX2, ly2, f"{i+1}.")
        c.setStrokeColor(PALE)
        c.setLineWidth(0.6)
        c.line(LX2 + 0.22 * inch, ly2, LX2 + H_COL, ly2)
        ly2 -= 0.29 * inch

    ry2 = y
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(CHARCOAL)
    c.drawString(RX2, ry2, "3 THINGS THAT WOULD MAKE")
    ry2 -= 0.145 * inch
    c.drawString(RX2, ry2, "TOMORROW GREAT")
    ry2 -= 0.20 * inch
    for i in range(3):
        c.setFont("Helvetica", 11)
        c.setFillColor(MID_GRAY)
        c.drawString(RX2, ry2, f"{i+1}.")
        c.setStrokeColor(PALE)
        c.setLineWidth(0.6)
        c.line(RX2 + 0.22 * inch, ry2, RX2 + H_COL, ry2)
        ry2 -= 0.29 * inch

    y = min(ly2, ry2) - 0.22 * inch

    c.setStrokeColor(PALE)
    c.setLineWidth(0.5)
    c.line(ML, y + 0.06 * inch, W - MR, y + 0.06 * inch)
    y -= 0.05 * inch

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(CHARCOAL)
    c.drawString(ML, y - 0.11 * inch, "TODAY'S NOTE")
    c.setFont("Helvetica", 9)
    c.setFillColor(INK)
    c.drawRightString(W - MR, y - 0.11 * inch, "four lines · no prompts · just space")
    y -= 0.30 * inch

    for _ in range(4):
        c.setStrokeColor(PALE)
        c.setLineWidth(0.6)
        c.line(ML, y, W - MR, y)
        y -= 0.30 * inch

    # ── FOOTER — 8pt (was 6.5) ────────────────────────────────────────────────
    fy = MB
    c.setStrokeColor(PALE)
    c.setLineWidth(0.6)
    c.line(ML, fy + 0.13 * inch, W - MR, fy + 0.13 * inch)
    c.setFont("Helvetica", 8)
    c.setFillColor(INK)
    c.drawString(ML, fy, "DAILY BRIEF  ·  Luciano Global Ventures Inc.  ·  Confidential")
    c.drawRightString(W - MR, fy, "2 of 2")


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────────

def create(out_path):
    cv = canvas.Canvas(out_path, pagesize=letter)
    cv.setTitle(f"Daily Brief — {DATA['date_str']} — LGV")
    cv.setAuthor("Mark Luciano Ainsworth — LGV")
    draw_page1(cv, DATA)
    cv.showPage()
    draw_page2(cv, DATA)
    cv.save()
    print(f"PDF written: {out_path}")

if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/Daily Brief 22.03.2026.pdf"
    create(out)
