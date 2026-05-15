"""
Maps news topics to chart URLs.
- Macro data  → FRED fullscreen (official, clean, no ads)
- Price data  → Yahoo Finance (dark theme, no ads, confirmed working)
"""

# Yahoo Finance base — clean dark chart, fullscreen-ready
YF = "https://finance.yahoo.com/chart/"

# topic keywords → (chart_url, chart_label, source_type)
# source_type: "fred" → click Fullscreen button | "yahoo" → zoom crop
TOPIC_CHART_MAP = [
    (
        ["fed", "warsh", "powell", "bond", "treasury", "rates", "tipos", "yield", "bono"],
        "https://fred.stlouisfed.org/graph/?id=DGS10&cosd=2023-01-01",
        "Treasury 10Y Yield (FRED)", "fred"
    ),
    (
        ["inflation", "inflación", "cpi", "ipc", "price", "precios"],
        "https://fred.stlouisfed.org/graph/?id=CPIAUCSL&cosd=2020-01-01",
        "Inflación EE.UU. CPI (FRED)", "fred"
    ),
    (
        ["unemployment", "desempleo", "empleo", "temp help", "temphelps", "labor", "paro", "recession"],
        "https://fred.stlouisfed.org/graph/?id=TEMPHELPS,UNRATE&cosd=2000-01-01",
        "Empleo Temporal vs Desempleo EE.UU. (FRED)", "fred"
    ),
    (
        ["dollar", "dólar", "dxy", "usd index"],
        f"{YF}DX-Y.NYB/",
        "Índice Dólar DXY (Yahoo Finance)", "yahoo"
    ),
    (
        ["gold", "oro", "silver", "plata", "metal"],
        f"{YF}GC%3DF/",
        "Oro spot (Yahoo Finance)", "yahoo"
    ),
    (
        ["oil", "petróleo", "crude", "wti", "brent", "hormuz", "uae", "opec"],
        f"{YF}CL%3DF/",
        "WTI Crude Oil (Yahoo Finance)", "yahoo"
    ),
    (
        ["nvidia", "nvda"],
        f"{YF}NVDA/",
        "Nvidia NVDA (Yahoo Finance)", "yahoo"
    ),
    (
        ["sp500", "s&p", "spx", "sell signal"],
        f"{YF}%5EGSPC/",
        "S&P 500 (Yahoo Finance)", "yahoo"
    ),
    (
        ["nasdaq", "tech", "tecnología"],
        f"{YF}%5EIXIC/",
        "Nasdaq Composite (Yahoo Finance)", "yahoo"
    ),
    (
        ["bitcoin", "btc", "crypto", "ethereum"],
        f"{YF}BTC-USD/",
        "Bitcoin USD (Yahoo Finance)", "yahoo"
    ),
    (
        ["ibex", "spain", "españa", "santander", "bbva"],
        f"{YF}%5EIBEX/",
        "IBEX 35 (Yahoo Finance)", "yahoo"
    ),
    (
        ["turkey", "turquía", "lira", "emerging"],
        "https://fred.stlouisfed.org/graph/?id=DEXTHUS&cosd=2020-01-01",
        "USD/TRY Lira Turca (FRED)", "fred"
    ),
    (
        ["vix", "volatility", "volatilidad", "fear"],
        f"{YF}%5EVIX/",
        "VIX Volatility Index (Yahoo Finance)", "yahoo"
    ),
]


def pick_chart_for_text(text: str) -> tuple:
    """Return (url, label) for the best matching chart given a text snippet."""
    text_lower = text.lower()
    best_match = None
    best_count = 0
    for keywords, url, label, *_ in TOPIC_CHART_MAP:
        count = sum(1 for k in keywords if k in text_lower)
        if count > best_count:
            best_count = count
            best_match = (url, label)
    if not best_match:
        best_match = (f"{YF}%5EGSPC/", "S&P 500 (Yahoo Finance)")
    return best_match
