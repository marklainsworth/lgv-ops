"""
LGV Daily Brief — daily_brief.py
Canonical script · github.com/marklainsworth/lgv-ops
Version: 2.0 — unified build (calendar + scheduling + brief)

SCHEDULE TUPLE FORMAT:
  (time_str, title, tag, detail, is_task, granola_or_None)
  is_task=True  → single line (title · tag · due today if applicable)
  is_task=False → two lines  (bold title + italic detail)

POMODORO BREAK RULE (applied automatically in schedule renderer):
  After consecutive task blocks: 1st → 5 min break, 2nd → 10 min, 3rd → 15 min
  Counter resets after any non-task block or after 3rd break.
  Break rows are inserted automatically — do NOT add them manually to DATA["schedule"].

DATA DICT — populate fresh each run via the unified Claude API prompt.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black, white
from datetime import datetime
import math, os

W, H = letter

INK        = HexColor('#000000')
CHARCOAL   = HexColor('#000000')
DARK_GRAY  = HexColor('#000000')
MID_GRAY   = HexColor('#000000')
LIGHT_GRAY = HexColor('#000000')
PALE       = HexColor('#000000')
OFF_WHITE  = HexColor('#FAFAF8')
GOLD       = HexColor('#C8B89A')
GRANOLA_BG = HexColor('#F0EFEB')

ML  = 0.425 * inch
MR  = 0.3   * inch
MT  = 0.325 * inch
MB  = 0.275 * inch
CW  = W - ML - MR

# ---------------------------------------------------------------------------
# DATA — populated by the unified Claude prompt at runtime
# ---------------------------------------------------------------------------
DATA = {
    "day_name":      "Tuesday",
    "date_str":      "24/03/26",
    "operator_quote": "Plans are useless. Planning is indispensable. — Dwight D. Eisenhower",
    "weather_home":  "San Francisco  \u00b7  Partly cloudy  \u00b7  High 68\u00b0F",
    "weather_travel": "Las Vegas  \u00b7  Clear  \u00b7  High 96\u00b0F",
    "travel_label":  None,
    "week_events": [
        ("TUE", "TGVR Draft 9\u201310am  \u00b7  CFK Booth 10am\u20134:30pm"),
        ("WED", "TGVR Draft Block 3 9am  \u00b7  CFK Booth 10am\u20135pm"),
        ("THU", "CFK Booth 10am\u20134pm  \u00b7  LAS\u2192SFO 1:50pm  \u00b7  Peet\u2019s / Mostafa 4pm"),
        ("FRI", "Task blocks 9:30am\u201312pm  \u00b7  Monarch 2pm"),
        ("SAT", "Flag Football 10am  \u00b7  Family Check-In 10:30am"),
    ],
    # schedule: (time, title, tag, detail, is_task, granola)
    # Breaks are auto-inserted — do NOT add them here
    "schedule": [
        ("9:00",  "Issue No. 03 draft",          "[TGVR]", "Block 1 of 3 \u2014 30/30/30",  True,  None),
        ("9:30",  "Issue No. 03 draft",          "[TGVR]", "Block 2 of 3",                   True,  None),
        ("10:00", "CFK Booth \u2014 Pizza Expo", "",       "LVCC Booth #3206 \u00b7 10am\u20134:30pm", False, None),
        ("12:00", "Lunch \u2014 Not Available",  "",       "Blocked",                          False, None),
    ],
    # birthdays only — used in FAMILY & HOME right column
    "family_home": [
        ("Sun 29",  "Cynthia Shannon \u2014 Birthday"),
        ("Mon 30",  "Mark Russ \u2014 Birthday"),
    ],
    "urgent": [
        "Issue No. 03 draft \u2014 OVERDUE since Mar 23 \u00b7 blocks 1 & 2 on calendar now",
        "Pay tax lawyer \u2014 OVERDUE since Mar 24 \u00b7 scheduled Fri Mar 27",
        "Confirm Peets with Mostafa \u2014 Thu Mar 26 4pm \u00b7 his cell 650-520-8515",
    ],
    # articles: (CATEGORY, headline, byline, synopsis, why, url)
    "articles": [
        (
            "LEADERSHIP",
            "When Senior Leaders Lack People Skills, Transformations Fail",
            "Harvard Business Review  \u00b7  March 19, 2026",
            "A chief transformation officer discovered six weeks in that engagement scores had dropped 40% and turnover had doubled \u2014 and no one at the executive table saw it coming. HBR outlines four strategies: diagnose the gap without making it personal, build the skill through repetition not training, redesign the system to compensate, and know when to replace rather than develop.",
            "The interim operator\u2019s advantage: you see the people-skills gap before the board does. Pattern recognition from day one.",
            "https://hbr.org/2026/03/when-senior-leaders-lack-people-skills-transformations-fail"
        ),
        (
            "PE / INVESTOR LENS",
            "McKinsey Global Private Markets 2026: CEO Alpha Is the New Value Creation Edge",
            "McKinsey & Company  \u00b7  February 10, 2026",
            "McKinsey\u2019s tenth annual private markets report finds that 60\u201370% of PE-backed companies experience a CEO change during ownership, and more than 60% of replacements are first-time CEOs. The firms winning in 2026 are those with operating groups engaged earlier in diligence \u2014 60% now use them to identify bankable improvements before the deal closes.",
            "This is the TGVR Issue 03 thesis in a single data point. LGV\u2019s value is front-loaded \u2014 that\u2019s the conversation to have with GPs.",
            "https://www.mckinsey.com/industries/private-capital/our-insights/global-private-markets-report"
        ),
        (
            "CPG / FOOD MANUFACTURING",
            "Food Giants Cast a Sour Mood on Consumer Spending in 2026",
            "Food Dive  \u00b7  February 19, 2026",
            "Major CPG executives warn of a prolonged spending downturn as inflation-weary consumers refuse to return to pre-2022 buying habits. Despite price cuts, marketing investments, and packaging changes, volumes remain weak. Nestl\u00e9 forecasts 1\u20132% category growth. Conagra is holding flat.",
            "Every PE-backed food portfolio is fighting this right now. Operators who know how to drive volume without destroying margin are the asset.",
            "https://www.fooddive.com/news/food-giants-cast-a-sour-mood-on-consumer-spending-in-2026/812403/"
        ),
        (
            "ITALY \u2014 FOOD & CULTURE",
            "Italian Cuisine Named UNESCO Heritage \u2014 2026 Is Its First Full Year",
            "360ItalyMarket  \u00b7  March 2026",
            "UNESCO\u2019s December 2025 inscription of Italian cuisine as Intangible Cultural Heritage \u2014 the first time an entire national culinary tradition has received the designation \u2014 is reshaping how Italy positions its food exports globally. Italian food exports hit a record \u20ac70.7 billion.",
            "Eat Sunday Supper sits at the intersection of every trend driving this: heritage, authenticity, Sunday ritual, family transmission. The UNESCO moment is the hook.",
            "https://www.360italymarket.com/en/blog/food-trends-2026-b92.html"
        ),
    ],
    "meetings": [
        {
            "time":      "10:00am \u2013 4:30pm",
            "title":     "CFK Booth \u2014 International Pizza Expo",
            "attendees": "Chefs Feeding Kids team \u00b7 LVCC Booth #3206",
            "platform":  "In person \u00b7 Las Vegas Convention Center",
            "granola":   None,
            "lines":     6,
        },
    ],
}


# ---------------------------------------------------------------------------
# Pomodoro break cadence helper
# ---------------------------------------------------------------------------
BREAK_LABELS = {1: "5-min break", 2: "10-min break", 3: "15-min break"}
BREAK_DURATIONS = {1: "5 min", 2: "10 min", 3: "15 min"}

def inject_pomodoro_breaks(schedule):
    """
    Walk the schedule tuples and insert break rows after consecutive task blocks.
    Break cadence: 1st task → 5 min, 2nd → 10 min, 3rd → 15 min, then resets.
    A non-task event resets the counter.
    Returns new list with break rows inserted.
    Break row format: (time_str, label, "", duration, "BREAK", None)
    """
    result = []
    consecutive = 0
    for entry in schedule:
        time_str, title, tag, detail, is_task, granola = entry
        result.append(entry)
        if is_task:
            consecutive += 1
            step = ((consecutive - 1) % 3) + 1
            label = BREAK_LABELS[step]
            dur   = BREAK_DURATIONS[step]
            result.append((time_str, label, "", dur, "BREAK", None))
        else:
            consecutive = 0
    return result


# ---------------------------------------------------------------------------
# Utility draw functions
# ---------------------------------------------------------------------------
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

def section_rule(c, label, y, page_w, font_size=8.5):
    c.setFont("Helvetica-Bold", font_size)
    c.setFillColor(INK)
    c.drawString(ML, y, label)
    tw = c.stringWidth(label, "Helvetica-Bold", font_size)
    c.setStrokeColor(INK)
    c.setLineWidth(0.6)
    c.line(ML + tw + 7, y + font_size * 0.45, page_w - MR, y + font_size * 0.45)
    return y - 0.22 * inch

def draw_lgv_logo(c, cx, cy, size=0.52):
    badge_h = size * inch * 1.85
    badge_w = size * inch * 2.1
    lgv_size = badge_h * 0.42
    c.setFont("Helvetica-Bold", lgv_size)
    c.setFillColor(INK)
    lgv_txt  = "LGV"
    lgv_w    = c.stringWidth(lgv_txt, "Helvetica-Bold", lgv_size)
    letter_gap = lgv_size * 0.18
    total_w  = lgv_w + letter_gap * (len(lgv_txt) - 1)
    lx = cx - total_w / 2
    for ch in lgv_txt:
        c.drawString(lx, cy + badge_h * 0.06, ch)
        lx += c.stringWidth(ch, "Helvetica-Bold", lgv_size) + letter_gap
    rule_y = cy - badge_h * 0.08
    rule_w = badge_w * 0.68
    c.setStrokeColor(INK)
    c.setLineWidth(1.0)
    c.line(cx - rule_w / 2, rule_y, cx + rule_w / 2, rule_y)
    sub_size = badge_h * 0.115
    c.setFont("Helvetica", sub_size)
    c.setFillColor(INK)
    sub_txt = "LUCIANO GLOBAL VENTURES"
    sub_w   = c.stringWidth(sub_txt, "Helvetica", sub_size)
    c.drawString(cx - sub_w / 2, cy - badge_h * 0.33, sub_txt)

def draw_article_cell(c, article, x, y, col_w):
    cat, headline, byline, synopsis, why, url = article
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(INK)
    c.drawString(x, y, cat)
    y -= 0.1 * inch
    c.setStrokeColor(INK)
    c.setLineWidth(0.6)
    c.line(x, y + 0.04 * inch, x + col_w, y + 0.04 * inch)
    y -= 0.1 * inch
    hl_top  = y
    hl_lines = wrap(c, headline, "Helvetica-Bold", 9.5, col_w)[:2]
    c.setFont("Helvetica-Bold", 9.5)
    c.setFillColor(INK)
    for ln in hl_lines:
        c.drawString(x, y, ln)
        y -= 0.145 * inch
    c.linkURL(url, (x, y, x + col_w, hl_top + 0.12 * inch), relative=0)
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(INK)
    short_by = byline if len(byline) <= 52 else byline[:52] + "\u2026"
    c.drawString(x, y, short_by)
    y -= 0.135 * inch
    syn_lines = wrap(c, synopsis, "Helvetica", 9, col_w)[:3]
    c.setFont("Helvetica", 9)
    c.setFillColor(INK)
    for ln in syn_lines:
        c.drawString(x, y, ln)
        y -= 0.125 * inch
    y -= 0.02 * inch
    why_lines = wrap(c, why, "Helvetica-Oblique", 8.5, col_w)[:1]
    c.setFont("Helvetica-Oblique", 8.5)
    c.setFillColor(INK)
    for ln in why_lines:
        c.drawString(x, y, ln)
        y -= 0.12 * inch
    return y


# ---------------------------------------------------------------------------
# Page 1
# ---------------------------------------------------------------------------
def draw_page1(c):
    c.setFillColor(OFF_WHITE)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    y = H - MT

    LOGO_R  = 0.44
    logo_cx = W - MR - LOGO_R * inch - 0.38 * inch

    # Masthead rules
    c.setStrokeColor(INK)
    c.setLineWidth(2.2)
    c.line(ML, y, W - MR, y)
    y -= 0.06 * inch
    c.setLineWidth(0.55)
    c.line(ML, y, W - MR, y)
    y -= 0.32 * inch

    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(INK)
    c.drawString(ML, y, "DAILY BRIEF")
    y -= 0.18 * inch

    c.setFont("Helvetica", 10)
    c.setFillColor(INK)
    name_str = "Mark Luciano Ainsworth"
    role_str = "Managing Partner, LGV"
    day_date = DATA["day_name"] + "  \u00b7  " + DATA["date_str"]
    c.drawString(ML, y, name_str)
    nw = c.stringWidth(name_str, "Helvetica", 10)
    c.drawString(ML + nw + 5, y, "\u00b7")
    c.drawString(ML + nw + 13, y, role_str)
    rw = c.stringWidth(role_str, "Helvetica", 10)
    pipe_x = ML + nw + 13 + rw + 10
    c.setFont("Helvetica", 9)
    c.drawString(pipe_x, y, "|")
    c.setFont("Helvetica", 9.5)
    c.drawString(pipe_x + 10, y, day_date)
    y -= 0.18 * inch

    c.setStrokeColor(INK)
    c.setLineWidth(0.55)
    c.line(ML, y, W - MR, y)
    y -= 0.055 * inch
    c.setLineWidth(2.2)
    c.line(ML, y, W - MR, y)

    masthead_top = H - MT
    masthead_bot = y
    logo_cy = (masthead_top + masthead_bot) / 2
    draw_lgv_logo(c, logo_cx, logo_cy, LOGO_R)
    y -= 0.2 * inch

    # Quote
    c.setFont("Helvetica-Oblique", 9.5)
    c.setFillColor(INK)
    for ln in wrap(c, DATA["operator_quote"], "Helvetica-Oblique", 9.5, CW * 0.88):
        c.drawString(ML, y, ln)
        y -= 0.145 * inch
    y -= 0.08 * inch

    # Weather
    y = section_rule(c, "WEATHER", y, W)
    c.setFont("Helvetica", 9.5)
    c.setFillColor(INK)
    c.drawString(ML, y, DATA["weather_home"])
    y -= 0.155 * inch
    if DATA["weather_travel"]:
        c.drawString(ML, y, DATA["weather_travel"])
        tw = c.stringWidth(DATA["weather_travel"], "Helvetica", 9.5)
        if DATA["travel_label"]:
            c.setFont("Helvetica-Bold", 8)
            c.drawString(ML + tw + 10, y, DATA["travel_label"])
        y -= 0.155 * inch
    y -= 0.08 * inch

    # Two-column: TODAY'S SCHEDULE (left) | THIS WEEK (right)
    COL_GAP = 0.22 * inch
    L_W = CW * 0.595
    R_W = CW - L_W - COL_GAP
    LX  = ML
    RX  = ML + L_W + COL_GAP
    col_top = y

    # --- Left: schedule with Pomodoro breaks injected ---
    ly = col_top
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(INK)
    c.drawString(LX, ly, "TODAY'S SCHEDULE")
    htw = c.stringWidth("TODAY'S SCHEDULE", "Helvetica-Bold", 9)
    c.setStrokeColor(INK)
    c.setLineWidth(0.5)
    c.line(LX + htw + 6, ly + 0.055 * inch, LX + L_W, ly + 0.055 * inch)
    ly -= 0.2 * inch

    expanded_schedule = inject_pomodoro_breaks(DATA["schedule"])

    for entry in expanded_schedule:
        time_str, title, tag, detail, is_task, granola = entry

        if is_task == "BREAK":
            # Render break row — small, italic, indented
            c.setFont("Helvetica-Oblique", 7.5)
            c.setFillColor(INK)
            c.drawString(LX + 0.44 * inch, ly, f"\u21b3 {title}  \u00b7  {detail}")
            ly -= 0.135 * inch
            continue

        c.setFont("Helvetica", 8)
        c.setFillColor(INK)
        c.drawString(LX, ly, time_str)
        indent = 0.44 * inch
        fn = "Helvetica" if is_task else "Helvetica-Bold"
        c.setFont(fn, 9.5)
        c.setFillColor(INK)

        if is_task:
            display   = title
            due_str   = "  \u00b7  due today" if "due today" in detail.lower() else ""
            max_w     = L_W - indent - 0.05 * inch
            while c.stringWidth(display, fn, 9.5) > max_w - 0.3 * inch and len(display) > 8:
                display = display[:-4] + "\u2026"
            c.drawString(LX + indent, ly, display)
            dw = c.stringWidth(display, fn, 9.5)
            if tag:
                c.setFont("Helvetica", 7.5)
                c.drawString(LX + indent + dw + 5, ly, tag)
                dw2 = dw + 5 + c.stringWidth(tag, "Helvetica", 7.5)
            else:
                dw2 = dw
            if due_str:
                c.setFont("Helvetica-Oblique", 7.5)
                c.drawString(LX + indent + dw2 + 4, ly, "\u00b7  due today")
            ly -= 0.165 * inch
        else:
            max_title_w = L_W - indent - 0.05 * inch
            display = title
            while c.stringWidth(display, fn, 9.5) > max_title_w - 0.25 * inch and len(display) > 8:
                display = display[:-4] + "\u2026"
            c.drawString(LX + indent, ly, display)
            if tag:
                dw = c.stringWidth(display, fn, 9.5)
                c.setFont("Helvetica", 7.5)
                if LX + indent + dw + 5 + c.stringWidth(tag, "Helvetica", 7.5) < LX + L_W:
                    c.drawString(LX + indent + dw + 5, ly, tag)
            ly -= 0.148 * inch
            c.setFont("Helvetica-Oblique", 8)
            c.drawString(LX + indent, ly, detail)
            ly -= 0.13 * inch
            ly -= 0.08 * inch

    # --- Right: This Week ---
    ry = col_top
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(INK)
    c.drawString(RX, ry, "THIS WEEK")
    htw2 = c.stringWidth("THIS WEEK", "Helvetica-Bold", 9)
    c.setStrokeColor(INK)
    c.setLineWidth(0.5)
    c.line(RX + htw2 + 6, ry + 0.055 * inch, RX + R_W, ry + 0.055 * inch)
    ry -= 0.2 * inch
    for day, detail in DATA["week_events"]:
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(INK)
        c.drawString(RX, ry, day)
        c.setFont("Helvetica", 9)
        c.drawString(RX + 0.36 * inch, ry, detail)
        ry -= 0.175 * inch

    # Column separator — scoped to row height
    sep_x   = LX + L_W + COL_GAP * 0.5
    sep_bot = min(ly, ry) - 0.04 * inch
    c.setStrokeColor(INK)
    c.setLineWidth(0.6)
    c.line(sep_x, sep_bot, sep_x, col_top + 0.08 * inch)
    y = min(ly, ry) - 0.06 * inch

    # Family & Home — birthdays only in right column
    y = section_rule(c, "FAMILY & HOME", y, W)
    FAM_GAP = 0.2 * inch
    FAM_LW  = CW * 0.56
    FAM_LX  = ML
    FAM_RX  = ML + FAM_LW + FAM_GAP

    ly_f = y
    ry_f = y
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(INK)
    c.drawString(FAM_RX, ry_f, "BIRTHDAYS THIS WEEK")
    ry_f -= 0.155 * inch
    for day, name in DATA["family_home"]:
        c.setFont("Helvetica-Bold", 8.5)
        c.setFillColor(INK)
        c.drawString(FAM_RX, ry_f, day)
        dw = c.stringWidth(day, "Helvetica-Bold", 8.5)
        c.setFont("Helvetica", 9.5)
        c.drawString(FAM_RX + max(dw + 8, 0.56 * inch), ry_f, name)
        ry_f -= 0.16 * inch

    c.setStrokeColor(INK)
    c.setLineWidth(0.5)
    sep_fx = FAM_LX + FAM_LW + FAM_GAP * 0.5
    c.line(sep_fx, min(ly_f, ry_f) - 0.02 * inch, sep_fx, y + 0.1 * inch)
    y = min(ly_f, ry_f) - 0.08 * inch

    # Urgent
    y = section_rule(c, "URGENT", y, W)
    for i, item in enumerate(DATA["urgent"], 1):
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(INK)
        c.drawString(ML, y, f"{i}.")
        c.setFont("Helvetica", 9.5)
        c.drawString(ML + 0.22 * inch, y, item)
        y -= 0.165 * inch
    y -= 0.1 * inch

    # Reading List — 2×2 grid
    y = section_rule(c, "READING LIST", y, W)
    GAP   = 0.18 * inch
    ACW   = (CW - GAP) / 2
    col1x = ML
    col2x = ML + ACW + GAP
    sep_ax = col1x + ACW + GAP * 0.5

    avail    = y - MB - 0.12 * inch
    row_h    = avail / 2
    row1_top = y
    row1_bot = y - row_h
    row2_top = row1_bot - 0.14 * inch
    row2_bot = row2_top - row_h

    draw_article_cell(c, DATA["articles"][0], col1x, row1_top, ACW)
    draw_article_cell(c, DATA["articles"][1], col2x, row1_top, ACW)
    c.setFillColor(OFF_WHITE)
    c.rect(ML, row1_bot - 0.06 * inch, CW, 0.1 * inch, fill=1, stroke=0)
    c.setStrokeColor(INK)
    c.setLineWidth(0.4)
    c.line(sep_ax, row1_bot + 0.02 * inch, sep_ax, row1_top - 0.05 * inch)
    c.setStrokeColor(INK)
    c.setLineWidth(0.6)
    c.line(ML, row1_bot, W - MR, row1_bot)

    draw_article_cell(c, DATA["articles"][2], col1x, row2_top, ACW)
    draw_article_cell(c, DATA["articles"][3], col2x, row2_top, ACW)
    c.setFillColor(OFF_WHITE)
    c.rect(ML, MB, CW, 0.16 * inch, fill=1, stroke=0)
    c.setStrokeColor(INK)
    c.setLineWidth(0.4)
    c.line(sep_ax, row2_bot + 0.02 * inch, sep_ax, row1_bot)

    # Footer
    fy = MB
    c.setStrokeColor(INK)
    c.setLineWidth(0.4)
    c.line(ML, fy + 0.14 * inch, W - MR, fy + 0.14 * inch)
    c.setFont("Helvetica", 6.5)
    c.setFillColor(INK)
    c.drawString(ML, fy, "DAILY BRIEF  \u00b7  Luciano Global Ventures Inc.  \u00b7  Confidential")
    c.drawRightString(W - MR, fy, "1 of 2")


# ---------------------------------------------------------------------------
# Page 2
# ---------------------------------------------------------------------------
def draw_page2(c):
    c.setFillColor(OFF_WHITE)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    y = H - MT

    c.setStrokeColor(INK)
    c.setLineWidth(2)
    c.line(ML, y, W - MR, y)
    y -= 0.16 * inch
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(INK)
    c.drawString(ML, y, "MEETING NOTES")
    c.setFont("Helvetica", 10)
    c.drawRightString(W - MR, y, DATA["date_str"])
    y -= 0.1 * inch
    c.setStrokeColor(INK)
    c.setLineWidth(0.6)
    c.line(ML, y, W - MR, y)
    y -= 0.22 * inch

    for m in DATA["meetings"]:
        bar_h = 0.245 * inch
        c.setFillColor(HexColor('#EBEBEA'))
        c.rect(ML, y - 0.015 * inch, CW, bar_h, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(INK)
        c.drawString(ML + 0.07 * inch, y + bar_h * 0.28, m["time"])
        c.drawString(ML + 0.75 * inch, y + bar_h * 0.28, m["title"])
        y -= (bar_h + 0.06 * inch)
        c.setFont("Helvetica-Oblique", 8.5)
        c.drawString(ML, y, "Team:  " + m["attendees"])
        y -= 0.2 * inch
        c.setFont("Helvetica-Oblique", 8.5)
        granola_note = m["granola"] if m["granola"] else "Granola notes will appear here when connected"
        c.drawString(ML, y, m["platform"] + "  \u00b7  " + granola_note)
        y -= 0.22 * inch
        for _ in range(m["lines"]):
            c.setStrokeColor(INK)
            c.setLineWidth(0.5)
            c.line(ML, y, W - MR, y)
            y -= 0.32 * inch
        y -= 0.14 * inch

    # TGVR writing block — hardcoded for today if TGVR draft is in schedule
    tgvr_on_schedule = any("[TGVR]" in str(s[2]) for s in DATA["schedule"])
    if tgvr_on_schedule:
        bar_h = 0.245 * inch
        c.setFillColor(HexColor('#EBEBEA'))
        c.rect(ML, y - 0.015 * inch, CW, bar_h, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(INK)
        c.drawString(ML + 0.07 * inch, y + bar_h * 0.28, "9:00am")
        c.drawString(ML + 0.75 * inch, y + bar_h * 0.28, "TGVR Issue No. 03 Draft \u2014 Writing Session")
        y -= (bar_h + 0.06 * inch)
        c.setFont("Helvetica-Oblique", 8.5)
        c.drawString(ML, y, "Blocks 1 & 2 of 3  \u00b7  30/30/30  \u00b7  Overdue from Mar 23  \u00b7  Block 3 scheduled Wed Mar 25 9am")
        y -= 0.2 * inch
        for _ in range(5):
            c.setStrokeColor(INK)
            c.setLineWidth(0.5)
            c.line(ML, y, W - MR, y)
            y -= 0.32 * inch
        y -= 0.1 * inch

    # End-of-day divider
    c.setStrokeColor(INK)
    c.setLineWidth(2)
    c.line(ML, y, W - MR, y)
    y -= 0.04 * inch
    c.setLineWidth(0.5)
    c.line(ML, y, W - MR, y)
    y -= 0.22 * inch

    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(INK)
    c.drawString(ML, y, "END OF DAY")
    c.setFont("Helvetica", 8.5)
    c.drawRightString(W - MR, y, "complete before sleep")
    y -= 0.08 * inch
    c.setStrokeColor(INK)
    c.setLineWidth(0.5)
    c.line(ML, y, W - MR, y)
    y -= 0.22 * inch

    H_COL = CW * 0.5 - 0.1 * inch
    LX2   = ML
    RX2   = ML + H_COL + 0.2 * inch

    ly2 = y
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(INK)
    c.drawString(LX2, ly2, "3 THINGS THAT MADE TODAY GREAT")
    ly2 -= 0.32 * inch
    for i in range(3):
        c.setFont("Helvetica", 9.5)
        c.drawString(LX2, ly2, f"{i+1}.")
        c.setStrokeColor(INK)
        c.setLineWidth(0.5)
        c.line(LX2 + 0.22 * inch, ly2, LX2 + H_COL, ly2)
        ly2 -= 0.32 * inch

    ry2 = y
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(INK)
    c.drawString(RX2, ry2, "3 THINGS THAT WOULD MAKE TOMORROW GREAT")
    ry2 -= 0.32 * inch
    for i in range(3):
        c.setFont("Helvetica", 9.5)
        c.drawString(RX2, ry2, f"{i+1}.")
        c.setStrokeColor(INK)
        c.setLineWidth(0.5)
        c.line(RX2 + 0.22 * inch, ry2, RX2 + H_COL, ry2)
        ry2 -= 0.32 * inch

    y = min(ly2, ry2) - 0.18 * inch
    c.setStrokeColor(INK)
    c.setLineWidth(0.4)
    c.line(ML, y + 0.06 * inch, W - MR, y + 0.06 * inch)
    y -= 0.06 * inch

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(INK)
    c.drawString(ML, y - 0.1 * inch, "TODAY'S NOTE")
    c.setFont("Helvetica", 7)
    c.drawRightString(W - MR, y - 0.1 * inch, "four lines  \u00b7  no prompts  \u00b7  just space")
    y -= 0.28 * inch
    for _ in range(4):
        c.setStrokeColor(INK)
        c.setLineWidth(0.5)
        c.line(ML, y, W - MR, y)
        y -= 0.32 * inch

    fy = MB
    c.setStrokeColor(INK)
    c.setLineWidth(0.4)
    c.line(ML, fy + 0.14 * inch, W - MR, fy + 0.14 * inch)
    c.setFont("Helvetica", 6.5)
    c.setFillColor(INK)
    c.drawString(ML, fy, "DAILY BRIEF  \u00b7  Luciano Global Ventures Inc.  \u00b7  Confidential")
    c.drawRightString(W - MR, fy, "2 of 2")


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def create():
    # Date-agnostic output path — derives filename from DATA["date_str"]
    ds    = DATA["date_str"].replace("/", ".")   # "24/03/26" → "24.03.26"
    parts = ds.split(".")
    if len(parts) == 3:
        filename = f"Daily Brief {parts[0]}.{parts[1]}.20{parts[2]}.pdf"
    else:
        filename = f"Daily Brief {ds}.pdf"
    out = os.path.join("/mnt/user-data/outputs", filename)
    c   = canvas.Canvas(out, pagesize=letter)
    c.setTitle(f"Daily Brief \u2014 {DATA['date_str']}")
    c.setAuthor("Mark Luciano Ainsworth \u2014 LGV")
    draw_page1(c)
    c.showPage()
    draw_page2(c)
    c.save()
    print(f"Done: {out}")

create()
