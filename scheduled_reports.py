"""
Calendar of high-impact financial reports and events.
Returns what's upcoming this week or was just released.
"""
from datetime import date, timedelta

TODAY = date.today()


# ── FOMC 2026 ──────────────────────────────────────────────────────────────
FOMC_2026 = [
    date(2026, 1, 28), date(2026, 1, 29),
    date(2026, 3, 18), date(2026, 3, 19),
    date(2026, 5, 6),  date(2026, 5, 7),
    date(2026, 6, 17), date(2026, 6, 18),
    date(2026, 7, 28), date(2026, 7, 29),
    date(2026, 9, 15), date(2026, 9, 16),
    date(2026, 10, 27), date(2026, 10, 28),
    date(2026, 12, 15), date(2026, 12, 16),
]

# ── ECB 2026 ───────────────────────────────────────────────────────────────
ECB_2026 = [
    date(2026, 1, 30), date(2026, 3, 5),
    date(2026, 4, 16), date(2026, 6, 4),
    date(2026, 7, 23), date(2026, 9, 10),
    date(2026, 10, 29), date(2026, 12, 3),
]

# ── NFP (Non-Farm Payrolls) 2026 — first Friday of each month ──────────────
NFP_2026 = [
    date(2026, 1, 9),  date(2026, 2, 6),  date(2026, 3, 6),
    date(2026, 4, 3),  date(2026, 5, 1),  date(2026, 6, 5),
    date(2026, 7, 3),  date(2026, 8, 7),  date(2026, 9, 4),
    date(2026, 10, 2), date(2026, 11, 6), date(2026, 12, 4),
]

# ── CPI EE.UU. 2026 (approx mid-month) ────────────────────────────────────
CPI_2026 = [
    date(2026, 1, 14), date(2026, 2, 12), date(2026, 3, 11),
    date(2026, 4, 10), date(2026, 5, 13), date(2026, 6, 11),
    date(2026, 7, 15), date(2026, 8, 12), date(2026, 9, 11),
    date(2026, 10, 14), date(2026, 11, 13), date(2026, 12, 10),
]

# ── PIB / GDP EE.UU. (advance, quarterly) ─────────────────────────────────
GDP_US_2026 = [
    date(2026, 1, 29),  # Q4 2025 advance
    date(2026, 4, 30),  # Q1 2026 advance
    date(2026, 7, 30),  # Q2 2026 advance
    date(2026, 10, 29), # Q3 2026 advance
]

# ── Earnings seasons (peak weeks) ─────────────────────────────────────────
EARNINGS_SEASONS_2026 = [
    {"name": "Earnings Q4 2025", "start": date(2026, 1, 13), "end": date(2026, 2, 14)},
    {"name": "Earnings Q1 2026", "start": date(2026, 4, 13), "end": date(2026, 5, 15)},
    {"name": "Earnings Q2 2026", "start": date(2026, 7, 13), "end": date(2026, 8, 14)},
    {"name": "Earnings Q3 2026", "start": date(2026, 10, 12), "end": date(2026, 11, 13)},
]

# ── Informes de grandes bancos (research institucional clave) ──────────────
BANK_REPORTS_2026 = [
    # JPMorgan Guide to the Markets — trimestral
    {"name": "JPMorgan Guide to the Markets Q1", "date": date(2026, 1, 15), "type": "quarterly"},
    {"name": "JPMorgan Guide to the Markets Q2", "date": date(2026, 4, 15), "type": "quarterly"},
    {"name": "JPMorgan Guide to the Markets Q3", "date": date(2026, 7, 15), "type": "quarterly"},
    {"name": "JPMorgan Guide to the Markets Q4", "date": date(2026, 10, 15), "type": "quarterly"},
    # Goldman Sachs Outlook anual
    {"name": "Goldman Sachs 2026 Outlook", "date": date(2026, 1, 10), "type": "annual"},
    # BIS Quarterly Review
    {"name": "BIS Quarterly Review", "date": date(2026, 3, 10), "type": "quarterly"},
    {"name": "BIS Quarterly Review", "date": date(2026, 6, 9), "type": "quarterly"},
    {"name": "BIS Quarterly Review", "date": date(2026, 9, 8), "type": "quarterly"},
    {"name": "BIS Quarterly Review", "date": date(2026, 12, 8), "type": "quarterly"},
    # IMF World Economic Outlook — abril y octubre
    {"name": "IMF World Economic Outlook", "date": date(2026, 4, 20), "type": "semi-annual"},
    {"name": "IMF World Economic Outlook Update", "date": date(2026, 7, 22), "type": "semi-annual"},
    {"name": "IMF World Economic Outlook", "date": date(2026, 10, 19), "type": "semi-annual"},
    # Fed Beige Book — 8 veces al año, ~2 semanas antes del FOMC
    {"name": "Fed Beige Book", "date": date(2026, 1, 14), "type": "monthly"},
    {"name": "Fed Beige Book", "date": date(2026, 3, 4), "type": "monthly"},
    {"name": "Fed Beige Book", "date": date(2026, 4, 22), "type": "monthly"},
    {"name": "Fed Beige Book", "date": date(2026, 6, 3), "type": "monthly"},
    {"name": "Fed Beige Book", "date": date(2026, 7, 15), "type": "monthly"},
    {"name": "Fed Beige Book", "date": date(2026, 9, 2), "type": "monthly"},
    {"name": "Fed Beige Book", "date": date(2026, 10, 14), "type": "monthly"},
    {"name": "Fed Beige Book", "date": date(2026, 12, 2), "type": "monthly"},
]


def get_upcoming_events(days_ahead: int = 7, days_behind: int = 2) -> list:
    """Return events happening within [days_behind, days_ahead] of today."""
    window_start = TODAY - timedelta(days=days_behind)
    window_end   = TODAY + timedelta(days=days_ahead)
    events = []

    def _add(label, d, category):
        if window_start <= d <= window_end:
            diff = (d - TODAY).days
            if diff < 0:
                timing = f"hace {abs(diff)} día{'s' if abs(diff) > 1 else ''}"
            elif diff == 0:
                timing = "HOY"
            elif diff == 1:
                timing = "mañana"
            else:
                timing = f"en {diff} días"
            events.append({"label": label, "date": str(d), "timing": timing, "category": category})

    # FOMC — flag the decision day (second day)
    fomc_decisions = FOMC_2026[1::2]
    for d in fomc_decisions:
        _add("FOMC — Decisión de tipos Fed", d, "FOMC")

    for d in ECB_2026:
        _add("ECB — Decisión de tipos BCE", d, "ECB")

    for d in NFP_2026:
        _add("NFP — Empleo no agrícola EE.UU.", d, "Macro")

    for d in CPI_2026:
        _add("CPI — Inflación EE.UU.", d, "Macro")

    for d in GDP_US_2026:
        _add("GDP — PIB EE.UU. (avance)", d, "Macro")

    for s in EARNINGS_SEASONS_2026:
        if s["start"] <= TODAY <= s["end"]:
            events.append({
                "label": f"⚡ EARNINGS SEASON ACTIVA: {s['name']}",
                "date": f"{s['start']} → {s['end']}",
                "timing": "en curso",
                "category": "Earnings"
            })

    for r in BANK_REPORTS_2026:
        _add(r["name"], r["date"], "Research")

    events.sort(key=lambda x: x["date"])
    return events


def format_calendar_block() -> str:
    events = get_upcoming_events()
    if not events:
        return ""
    lines = ["── EVENTOS Y PUBLICACIONES CLAVE (próximos 7 días) ──────"]
    for e in events:
        lines.append(f"  {e['timing'].upper():12} │ [{e['category']}] {e['label']}")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    print(format_calendar_block() or "Sin eventos relevantes esta semana.")
