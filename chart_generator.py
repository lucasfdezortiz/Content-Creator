"""
Generates local HTML chart files using TradingView Lightweight Charts (MIT).
Data sources: yfinance, FRED CSV API, World Bank API.
Charts saved to data/charts/YYYY-MM-DD/{name}.html
Served via local HTTP server on port 8765.

ACCURACY RULES:
- Chart titles state exactly what the series is (series ID, units)
- CPI index level ≠ inflation rate; both are available as separate charts
- Dual-axis charts use separate price scales to avoid scale mismatch
"""
import os
import json
import requests
from datetime import date, datetime, timedelta
from pathlib import Path

try:
    import yfinance as yf
    HAS_YF = True
except ImportError:
    HAS_YF = False

CHARTS_DIR = Path("/Users/lucasfdezortiz/substack-assistant/data/charts")
TODAY_STR  = date.today().isoformat()
FRED_CSV   = "https://fred.stlouisfed.org/graph/fredgraph.csv"


# ── HTML template ──────────────────────────────────────────────────────────────
_HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: #131722; font-family: -apple-system, BlinkMacSystemFont, 'Trebuchet MS', sans-serif; }}
  #header {{
    padding: 14px 20px 8px;
    color: #D1D4DC;
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 0.3px;
  }}
  #subheader {{
    padding: 0 20px 12px;
    color: #787B86;
    font-size: 11px;
  }}
  #chart {{ width: 100%; height: 500px; }}
  #footer {{
    padding: 8px 20px;
    color: #3d4154;
    font-size: 10px;
    text-align: right;
  }}
  .legend {{ padding: 0 20px 6px; font-size: 11px; }}
  .legend span {{ margin-right: 16px; }}
  .green {{ color: #26a69a; }}
  .red {{ color: #ef5350; }}
  .blue {{ color: #2196F3; }}
  .orange {{ color: #FF9800; }}
  .purple {{ color: #9C27B0; }}
</style>
</head>
<body>
<div id="header">{title}</div>
<div id="subheader">{subtitle}</div>
{legend}
<div id="chart"></div>
<div id="footer">{source}</div>
<script src="https://unpkg.com/lightweight-charts@4.1.1/dist/lightweight-charts.standalone.production.js"></script>
<script>
const chart = LightweightCharts.createChart(document.getElementById('chart'), {{
  width:  document.getElementById('chart').offsetWidth,
  height: 500,
  layout: {{
    background: {{ color: '#131722' }},
    textColor:  '#D1D4DC',
  }},
  grid: {{
    vertLines: {{ color: '#1e2230' }},
    horzLines: {{ color: '#1e2230' }},
  }},
  crosshair: {{ mode: LightweightCharts.CrosshairMode.Normal }},
  rightPriceScale: {{ borderColor: '#2a2e39', textColor: '#787B86' }},
  leftPriceScale:  {{ visible: false, borderColor: '#2a2e39', textColor: '#787B86' }},
  timeScale: {{
    borderColor: '#2a2e39',
    timeVisible: true,
    secondsVisible: false,
    fixLeftEdge: true,
    fixRightEdge: true,
  }},
}});

{series_code}

chart.timeScale().fitContent();
window.addEventListener('resize', () => {{
  chart.applyOptions({{ width: document.getElementById('chart').offsetWidth }});
}});
</script>
</body>
</html>"""

# ── Series templates ───────────────────────────────────────────────────────────
_CANDLE = """
const s = chart.addCandlestickSeries({{
  upColor: '#26a69a', downColor: '#ef5350',
  borderUpColor: '#26a69a', borderDownColor: '#ef5350',
  wickUpColor: '#26a69a', wickDownColor: '#ef5350',
}});
s.setData({data});
"""

_AREA = """
const s = chart.addAreaSeries({{
  lineColor: '{color}', topColor: '{color_alpha}',
  bottomColor: '#13172200', lineWidth: 2,
}});
s.setData({data});
"""

# Dual-axis: left scale for series A, right scale for series B
_DUAL_AXIS = """
chart.applyOptions({{ leftPriceScale: {{ visible: true }} }});
const sA = chart.addLineSeries({{
  color: '{colorA}', lineWidth: 2,
  priceScaleId: 'left',
  title: '{labelA}',
}});
sA.setData({dataA});
const sB = chart.addLineSeries({{
  color: '{colorB}', lineWidth: 2,
  priceScaleId: 'right',
  title: '{labelB}',
}});
sB.setData({dataB});
"""

_LINE_OVERLAY = """
const sA = chart.addLineSeries({{ color: '{colorA}', lineWidth: 2, title: '{labelA}' }});
sA.setData({dataA});
const sB = chart.addLineSeries({{ color: '{colorB}', lineWidth: 2, title: '{labelB}' }});
sB.setData({dataB});
"""


# ── Data helpers ───────────────────────────────────────────────────────────────
def _output_dir() -> Path:
    d = CHARTS_DIR / TODAY_STR
    d.mkdir(parents=True, exist_ok=True)
    return d


def _file_url(path: Path) -> str:
    return f"file://{path}"


def _local_url(name: str) -> str:
    return f"http://localhost:8765/{TODAY_STR}/{name}.html"


def _yf_candle(ticker: str, period: str = "1y") -> list:
    if not HAS_YF:
        return []
    try:
        df = yf.Ticker(ticker).history(period=period, interval="1d", auto_adjust=True)
        if df.empty:
            return []
        return [
            {
                "time":  int(ts.timestamp()),
                "open":  round(float(r["Open"]),  4),
                "high":  round(float(r["High"]),  4),
                "low":   round(float(r["Low"]),   4),
                "close": round(float(r["Close"]), 4),
            }
            for ts, r in df.iterrows()
        ]
    except Exception:
        return []


def _yf_area(ticker: str, period: str = "2y") -> list:
    if not HAS_YF:
        return []
    try:
        df = yf.Ticker(ticker).history(period=period, interval="1d", auto_adjust=True)
        if df.empty:
            return []
        return [
            {"time": int(ts.timestamp()), "value": round(float(r["Close"]), 4)}
            for ts, r in df.iterrows()
        ]
    except Exception:
        return []


def _fred(series_id: str, start: str = "2018-01-01") -> list:
    try:
        r = requests.get(FRED_CSV, params={"id": series_id, "cosd": start}, timeout=15)
        r.raise_for_status()
        rows = []
        for line in r.text.strip().splitlines()[1:]:
            parts = line.split(",")
            if len(parts) < 2 or parts[1].strip() in (".", ""):
                continue
            try:
                dt  = datetime.strptime(parts[0].strip(), "%Y-%m-%d")
                val = float(parts[1].strip())
                rows.append({"time": int(dt.timestamp()), "value": round(val, 4)})
            except ValueError:
                continue
        return rows
    except Exception:
        return []


def _fred_yoy(series_id: str, start: str = "2015-01-01") -> list:
    """Return YoY % change from a monthly FRED series (requires ≥13 months)."""
    raw = _fred(series_id, start=start)
    if len(raw) < 13:
        return []
    result = []
    for i in range(12, len(raw)):
        prev = raw[i - 12]["value"]
        curr = raw[i]["value"]
        if prev and prev != 0:
            yoy = round((curr - prev) / abs(prev) * 100, 2)
            result.append({"time": raw[i]["time"], "value": yoy})
    return result


def _worldbank(indicator: str, country: str = "US") -> list:
    try:
        url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"
        r = requests.get(url, params={"format": "json", "per_page": 100, "mrv": 30}, timeout=15)
        r.raise_for_status()
        payload = r.json()
        if len(payload) < 2 or not payload[1]:
            return []
        rows = []
        for entry in payload[1]:
            year = entry.get("date")
            val  = entry.get("value")
            if val is None or not year:
                continue
            try:
                rows.append({
                    "time":  int(datetime(int(year), 7, 1).timestamp()),
                    "value": round(float(val), 4),
                })
            except ValueError:
                continue
        return sorted(rows, key=lambda x: x["time"])
    except Exception:
        return []


# ── HTML builders ──────────────────────────────────────────────────────────────
def _save(name: str, title: str, subtitle: str, source: str,
          series_code: str, legend: str = "") -> str:
    html = _HTML_TEMPLATE.format(
        title=title, subtitle=subtitle, source=source,
        series_code=series_code, legend=legend,
    )
    path = _output_dir() / f"{name}.html"
    path.write_text(html, encoding="utf-8")
    return _local_url(name)


def _candle(name: str, title: str, subtitle: str, source: str, data: list) -> str:
    return _save(name, title, subtitle, source, _CANDLE.format(data=json.dumps(data)))


def _area(name: str, title: str, subtitle: str, source: str,
          data: list, color: str, color_alpha: str) -> str:
    code = _AREA.format(data=json.dumps(data), color=color, color_alpha=color_alpha)
    return _save(name, title, subtitle, source, code)


def _dual_axis(name: str, title: str, subtitle: str, source: str,
               dataA: list, labelA: str, colorA: str,
               dataB: list, labelB: str, colorB: str) -> str:
    code = _DUAL_AXIS.format(
        dataA=json.dumps(dataA), labelA=labelA, colorA=colorA,
        dataB=json.dumps(dataB), labelB=labelB, colorB=colorB,
    )
    legend = (
        f'<div class="legend">'
        f'<span style="color:{colorA}">▬ {labelA} (eje izq.)</span>'
        f'<span style="color:{colorB}">▬ {labelB} (eje der.)</span>'
        f'</div>'
    )
    return _save(name, title, subtitle, source, code, legend)


def _line_overlay(name: str, title: str, subtitle: str, source: str,
                  dataA: list, labelA: str, colorA: str,
                  dataB: list, labelB: str, colorB: str) -> str:
    code = _LINE_OVERLAY.format(
        dataA=json.dumps(dataA), labelA=labelA, colorA=colorA,
        dataB=json.dumps(dataB), labelB=labelB, colorB=colorB,
    )
    legend = (
        f'<div class="legend">'
        f'<span style="color:{colorA}">▬ {labelA}</span>'
        f'<span style="color:{colorB}">▬ {labelB}</span>'
        f'</div>'
    )
    return _save(name, title, subtitle, source, code, legend)


# ── Chart generators (each returns a localhost URL) ───────────────────────────

def chart_sp500() -> str:
    return _candle("sp500", "S&P 500 (^GSPC)", "Precio diario · últimos 12 meses",
                   "Yahoo Finance — OHLCV ajustado", _yf_candle("^GSPC", "1y"))

def chart_nasdaq() -> str:
    return _candle("nasdaq", "Nasdaq Composite (^IXIC)", "Precio diario · últimos 12 meses",
                   "Yahoo Finance — OHLCV ajustado", _yf_candle("^IXIC", "1y"))

def chart_ibex() -> str:
    return _candle("ibex35", "IBEX 35 (^IBEX)", "Precio diario · últimos 12 meses",
                   "Yahoo Finance — OHLCV ajustado", _yf_candle("^IBEX", "1y"))

def chart_vix() -> str:
    return _area("vix", "VIX — CBOE Volatility Index (^VIX)",
                 "Nivel de cierre diario · últimos 2 años",
                 "Yahoo Finance / CBOE",
                 _yf_area("^VIX", "2y"), "#ef5350", "#ef535033")

def chart_gold() -> str:
    return _candle("gold", "Oro — Futuros Continuos (GC=F)",
                   "Precio OHLCV diario · últimos 12 meses · USD/oz troy",
                   "Yahoo Finance — CME Gold Futures", _yf_candle("GC=F", "1y"))

def chart_silver() -> str:
    return _candle("silver", "Plata — Futuros Continuos (SI=F)",
                   "Precio OHLCV diario · últimos 12 meses · USD/oz troy",
                   "Yahoo Finance — CME Silver Futures", _yf_candle("SI=F", "1y"))

def chart_oil() -> str:
    return _candle("oil", "WTI Crude Oil — Futuros Continuos (CL=F)",
                   "Precio OHLCV diario · últimos 12 meses · USD/barril",
                   "Yahoo Finance — NYMEX WTI Futures", _yf_candle("CL=F", "1y"))

def chart_dxy() -> str:
    return _candle("dxy", "US Dollar Index (DX-Y.NYB)",
                   "Precio diario · últimos 12 meses · índice (base 100 = 1973)",
                   "Yahoo Finance / ICE", _yf_candle("DX-Y.NYB", "1y"))

def chart_bitcoin() -> str:
    return _candle("bitcoin", "Bitcoin / USD (BTC-USD)",
                   "Precio OHLCV diario · últimos 12 meses",
                   "Yahoo Finance — datos de mercado spot", _yf_candle("BTC-USD", "1y"))

def chart_nvidia() -> str:
    return _candle("nvda", "Nvidia Corporation (NVDA — Nasdaq)",
                   "Precio OHLCV diario · últimos 12 meses · USD",
                   "Yahoo Finance — precio ajustado por splits", _yf_candle("NVDA", "1y"))

def chart_eurusd() -> str:
    return _candle("eurusd", "EUR/USD — Tipo de Cambio",
                   "Precio diario · últimos 12 meses",
                   "Yahoo Finance — forex spot", _yf_candle("EURUSD=X", "1y"))

def chart_treasury_10y() -> str:
    data = _fred("DGS10", start="2020-01-01")
    return _area("treasury_10y",
                 "US Treasury 10Y — Rendimiento Constante (DGS10)",
                 "Tasa diaria en % · FRED desde ene-2020 · fuente: H.15 Fed",
                 "FRED — Federal Reserve / U.S. Treasury",
                 data, "#2196F3", "#2196F333")

def chart_fed_funds() -> str:
    data = _fred("FEDFUNDS", start="2015-01-01")
    return _area("fed_funds",
                 "Fed Funds Rate Efectiva (FEDFUNDS)",
                 "Tasa mensual en % · FRED desde ene-2015 · publicada por NY Fed",
                 "FRED — Federal Reserve Bank of New York",
                 data, "#9C27B0", "#9C27B033")

def chart_cpi_level() -> str:
    data = _fred("CPIAUCSL", start="2018-01-01")
    return _area("cpi_level",
                 "CPI — Índice de Precios al Consumidor, nivel (CPIAUCSL)",
                 "Nivel mensual · base 1982-84=100 · todos los bienes urbanos · FRED",
                 "FRED — U.S. Bureau of Labor Statistics",
                 data, "#FF9800", "#FF980033")

def chart_cpi_yoy() -> str:
    data = _fred_yoy("CPIAUCSL", start="2015-01-01")
    return _area("cpi_yoy",
                 "Inflación EE.UU. — CPI Variación Anual, % (CPIAUCSL YoY)",
                 "Variación % interanual mensual · calculado sobre CPIAUCSL · FRED",
                 "FRED — U.S. Bureau of Labor Statistics (cálculo YoY propio)",
                 data, "#FF9800", "#FF980033")

def chart_unemployment_vs_temp() -> str:
    data_unemp = _fred("UNRATE", start="2000-01-01")
    data_temp  = _fred("TEMPHELPS", start="2000-01-01")
    return _dual_axis(
        "unemployment_temp",
        "Tasa de Desempleo vs. Empleo Temporal EE.UU.",
        "UNRATE en % (eje izq.) · TEMPHELPS miles de empleados (eje der.) · FRED desde 2000",
        "FRED — U.S. Bureau of Labor Statistics",
        data_unemp, "UNRATE (%)", "#26a69a",
        data_temp,  "Temp Help (miles)", "#ef5350",
    )

def chart_yield_curve() -> str:
    data_2y  = _fred("DGS2",  start="2018-01-01")
    data_10y = _fred("DGS10", start="2018-01-01")
    return _line_overlay(
        "yield_curve",
        "Curva de Tipos EE.UU. — Treasury 2Y vs. 10Y",
        "Rendimiento constante en % · FRED desde ene-2018 · fuente: H.15 Fed",
        "FRED — Federal Reserve / U.S. Treasury",
        data_2y,  "DGS2 — 2Y (%)",  "#26a69a",
        data_10y, "DGS10 — 10Y (%)", "#2196F3",
    )

def chart_lira_usd() -> str:
    data = _fred("DEXTHUS", start="2020-01-01")
    return _area("usdtry",
                 "USD/TRY — Tipo de Cambio Dólar / Lira Turca (DEXTHUS)",
                 "Liras turcas por 1 USD · datos diarios · FRED desde ene-2020",
                 "FRED — Federal Reserve / H.10 Foreign Exchange Rates",
                 data, "#ef5350", "#ef535033")

def chart_us_gdp_growth() -> str:
    data = _worldbank("NY.GDP.MKTP.KD.ZG", "US")
    return _area("us_gdp_growth",
                 "EE.UU. — Crecimiento Real del PIB Anual (%)",
                 "Variación % anual · PIB a precios constantes · World Bank",
                 "World Bank Open Data — NY.GDP.MKTP.KD.ZG",
                 data, "#26a69a", "#26a69a33")

def chart_china_gdp_growth() -> str:
    data = _worldbank("NY.GDP.MKTP.KD.ZG", "CN")
    return _area("china_gdp_growth",
                 "China — Crecimiento Real del PIB Anual (%)",
                 "Variación % anual · PIB a precios constantes · World Bank",
                 "World Bank Open Data — NY.GDP.MKTP.KD.ZG (China)",
                 data, "#FF9800", "#FF980033")

def chart_us_debt_gdp() -> str:
    data = _worldbank("GC.DOD.TOTL.GD.ZS", "US")
    return _area("us_debt_gdp",
                 "EE.UU. — Deuda Pública Central (% del PIB)",
                 "% del PIB anual · incluye deuda del gobierno federal · World Bank",
                 "World Bank Open Data — GC.DOD.TOTL.GD.ZS",
                 data, "#ef5350", "#ef535033")


# ── Registry ───────────────────────────────────────────────────────────────────
# keyword → (generator_fn, display_label)
CHART_REGISTRY: dict[str, tuple] = {
    "sp500":        (chart_sp500,              "S&P 500"),
    "s&p":          (chart_sp500,              "S&P 500"),
    "spx":          (chart_sp500,              "S&P 500"),
    "sell signal":  (chart_sp500,              "S&P 500"),
    "nasdaq":       (chart_nasdaq,             "Nasdaq Composite"),
    "tech":         (chart_nasdaq,             "Nasdaq Composite"),
    "tecnología":   (chart_nasdaq,             "Nasdaq Composite"),
    "ibex":         (chart_ibex,               "IBEX 35"),
    "españa":       (chart_ibex,               "IBEX 35"),
    "spain":        (chart_ibex,               "IBEX 35"),
    "santander":    (chart_ibex,               "IBEX 35"),
    "bbva":         (chart_ibex,               "IBEX 35"),
    "vix":          (chart_vix,                "VIX Volatility Index"),
    "volatility":   (chart_vix,                "VIX Volatility Index"),
    "volatilidad":  (chart_vix,                "VIX Volatility Index"),
    "fear":         (chart_vix,                "VIX Volatility Index"),
    "gold":         (chart_gold,               "Oro Futuros (GC=F)"),
    "oro":          (chart_gold,               "Oro Futuros (GC=F)"),
    "silver":       (chart_silver,             "Plata Futuros (SI=F)"),
    "plata":        (chart_silver,             "Plata Futuros (SI=F)"),
    "metal":        (chart_gold,               "Oro Futuros (GC=F)"),
    "oil":          (chart_oil,                "WTI Crude Oil (CL=F)"),
    "petróleo":     (chart_oil,                "WTI Crude Oil (CL=F)"),
    "crude":        (chart_oil,                "WTI Crude Oil (CL=F)"),
    "wti":          (chart_oil,                "WTI Crude Oil (CL=F)"),
    "brent":        (chart_oil,                "WTI Crude Oil (CL=F)"),
    "opec":         (chart_oil,                "WTI Crude Oil (CL=F)"),
    "hormuz":       (chart_oil,                "WTI Crude Oil (CL=F)"),
    "dxy":          (chart_dxy,                "US Dollar Index (DXY)"),
    "dollar":       (chart_dxy,                "US Dollar Index (DXY)"),
    "dólar":        (chart_dxy,                "US Dollar Index (DXY)"),
    "usd index":    (chart_dxy,                "US Dollar Index (DXY)"),
    "bitcoin":      (chart_bitcoin,            "Bitcoin / USD"),
    "btc":          (chart_bitcoin,            "Bitcoin / USD"),
    "crypto":       (chart_bitcoin,            "Bitcoin / USD"),
    "ethereum":     (chart_bitcoin,            "Bitcoin / USD"),
    "nvidia":       (chart_nvidia,             "Nvidia NVDA"),
    "nvda":         (chart_nvidia,             "Nvidia NVDA"),
    "euro":         (chart_eurusd,             "EUR/USD"),
    "eurusd":       (chart_eurusd,             "EUR/USD"),
    "treasury":     (chart_treasury_10y,       "Treasury 10Y Yield"),
    "yield":        (chart_treasury_10y,       "Treasury 10Y Yield"),
    "bono":         (chart_treasury_10y,       "Treasury 10Y Yield"),
    "bond":         (chart_treasury_10y,       "Treasury 10Y Yield"),
    "warsh":        (chart_treasury_10y,       "Treasury 10Y Yield"),
    "fed":          (chart_fed_funds,          "Fed Funds Rate"),
    "powell":       (chart_fed_funds,          "Fed Funds Rate"),
    "rates":        (chart_fed_funds,          "Fed Funds Rate"),
    "tipos":        (chart_fed_funds,          "Fed Funds Rate"),
    "inflation":    (chart_cpi_yoy,            "Inflación EE.UU. CPI YoY%"),
    "inflación":    (chart_cpi_yoy,            "Inflación EE.UU. CPI YoY%"),
    "cpi":          (chart_cpi_yoy,            "Inflación EE.UU. CPI YoY%"),
    "ipc":          (chart_cpi_yoy,            "Inflación EE.UU. CPI YoY%"),
    "price":        (chart_cpi_yoy,            "Inflación EE.UU. CPI YoY%"),
    "precios":      (chart_cpi_yoy,            "Inflación EE.UU. CPI YoY%"),
    "unemployment": (chart_unemployment_vs_temp, "Desempleo vs Empleo Temporal"),
    "desempleo":    (chart_unemployment_vs_temp, "Desempleo vs Empleo Temporal"),
    "empleo":       (chart_unemployment_vs_temp, "Desempleo vs Empleo Temporal"),
    "labor":        (chart_unemployment_vs_temp, "Desempleo vs Empleo Temporal"),
    "paro":         (chart_unemployment_vs_temp, "Desempleo vs Empleo Temporal"),
    "recession":    (chart_unemployment_vs_temp, "Desempleo vs Empleo Temporal"),
    "recesión":     (chart_unemployment_vs_temp, "Desempleo vs Empleo Temporal"),
    "temp help":    (chart_unemployment_vs_temp, "Desempleo vs Empleo Temporal"),
    "yield curve":  (chart_yield_curve,        "Curva Tipos 2Y vs 10Y"),
    "curva":        (chart_yield_curve,        "Curva Tipos 2Y vs 10Y"),
    "lira":         (chart_lira_usd,           "USD/TRY Lira Turca"),
    "turkey":       (chart_lira_usd,           "USD/TRY Lira Turca"),
    "turquía":      (chart_lira_usd,           "USD/TRY Lira Turca"),
    "emerging":     (chart_lira_usd,           "USD/TRY Lira Turca"),
    "gdp":          (chart_us_gdp_growth,      "PIB EE.UU. Crecimiento %"),
    "pib":          (chart_us_gdp_growth,      "PIB EE.UU. Crecimiento %"),
    "china":        (chart_china_gdp_growth,   "PIB China Crecimiento %"),
    "deuda":        (chart_us_debt_gdp,        "Deuda Pública EE.UU. % PIB"),
    "debt":         (chart_us_debt_gdp,        "Deuda Pública EE.UU. % PIB"),
}


def generate_chart_for_text(text: str) -> tuple[str, str]:
    """Return (localhost_url, label) for the best matching chart. Generates HTML if needed."""
    text_lower = text.lower()
    best_fn    = None
    best_count = 0
    best_label = "S&P 500"

    for keyword, (fn, label) in CHART_REGISTRY.items():
        if keyword in text_lower:
            count = text_lower.count(keyword)
            if count > best_count:
                best_count = count
                best_fn    = fn
                best_label = label

    fn = best_fn or chart_sp500
    try:
        url = fn()
        return url, best_label
    except Exception as e:
        print(f"  [chart] Error generando '{best_label}': {e}")
        return "", best_label


def generate_all_default_charts() -> dict[str, str]:
    """Pre-generate the most commonly needed charts. Returns {name: url}."""
    charts = {}
    generators = [
        ("sp500",         chart_sp500),
        ("nasdaq",        chart_nasdaq),
        ("vix",           chart_vix),
        ("gold",          chart_gold),
        ("oil",           chart_oil),
        ("dxy",           chart_dxy),
        ("bitcoin",       chart_bitcoin),
        ("treasury_10y",  chart_treasury_10y),
        ("cpi_yoy",       chart_cpi_yoy),
        ("fed_funds",     chart_fed_funds),
        ("yield_curve",   chart_yield_curve),
        ("unemployment",  chart_unemployment_vs_temp),
        ("ibex35",        chart_ibex),
    ]
    for name, fn in generators:
        try:
            url = fn()
            charts[name] = url
        except Exception as e:
            print(f"  [chart] Error {name}: {e}")
    return charts


if __name__ == "__main__":
    import sys
    topics = sys.argv[1:] or ["sp500", "inflation", "oil", "bitcoin", "yield curve", "unemployment"]
    print(f"Generating {len(topics)} charts...\n")
    for topic in topics:
        url, label = generate_chart_for_text(topic)
        print(f"  {label:<45} {url}")
    print("\nDone.")
