RSS_SOURCES = {
    "FT":              "https://www.ft.com/rss/home",
    "FT Mercados":     "https://www.ft.com/markets?format=rss",
    "FT Alphaville":   "https://www.ft.com/alphaville?format=rss",
    "MarketWatch":     "https://feeds.marketwatch.com/marketwatch/topstories/",
    "Yahoo Finance":   "https://finance.yahoo.com/rss/topfinstories",
    "Reuters":         "https://feeds.reuters.com/reuters/businessNews",
    "Bloomberg":       "https://feeds.bloomberg.com/markets/news.rss",
    "WSJ Markets":     "https://feeds.wsj.com/wsj/xml/rss/3_7014.xml",
    "Seeking Alpha":   "https://seekingalpha.com/market_currents.xml",
    "El Economista":   "https://www.eleconomista.es/rss/rss-mercados.php",
    "Barrons":         "https://www.barrons.com/xml/rss/3_7566.xml",
}

# Public research/insights pages from major institutions
RESEARCH_SOURCES = {
    "Goldman Sachs":   "https://www.goldmansachs.com/intelligence/",
    "JPMorgan":        "https://www.jpmorgan.com/insights",
    "Morgan Stanley":  "https://www.morganstanley.com/ideas",
    "BlackRock":       "https://www.blackrock.com/us/individual/insights/blackrock-investment-institute",
    "PIMCO":           "https://www.pimco.com/en-us/resources/blog",
    "BofA Research":   "https://business.bofa.com/en-us/content/market-insights.html",
}

REDDIT_SUBREDDITS = ["investing", "stocks", "wallstreetbets", "SecurityAnalysis"]

REDDIT_MIN_SCORE = 100  # filter low-engagement posts

KEYWORDS_HIGH = [
    "fed", "bce", "ecb", "cpi", "inflation", "inflación", "ipc",
    "earnings", "resultados", "rates", "tipos", "oil", "petróleo",
    "ibex", "spain", "españa", "tariff", "arancel",
    "recession", "recesión", "employment", "empleo", "gdp", "pib",
    "bank", "banco", "interest", "interés",
    "ipo", "buyback", "recompra", "dividend", "dividendo",
    "default", "quiebra", "bankruptcy",
]
KEYWORDS_MED = [
    "nasdaq", "sp500", "s&p", "dow", "goldman", "jpmorgan",
    "powell", "lagarde", "nvidia", "apple", "microsoft", "amazon",
    "euro", "dollar", "dólar", "china", "trump", "war", "guerra",
    "semiconductor", "ai", "ia", "tech",
    "hedge fund", "buffett", "ackman", "cathie", "short seller",
    "deuda", "spread", "munger",
]

FOCUS_KEYWORDS = {
    "macro":  ["fed", "bce", "cpi", "gdp", "pib", "rates", "tipos", "inflation", "inflación", "powell", "lagarde"],
    "stocks": ["earnings", "eps", "guidance", "resultados", "revenue", "ipo", "buyback", "dividend"],
    "crypto": ["bitcoin", "btc", "ethereum", "crypto", "blockchain", "defi", "binance", "coinbase"],
    "spain":  ["ibex", "spain", "españa", "santander", "bbva", "expansion", "bono", "arancel"],
    "tech":   ["nvidia", "ai", "semiconductor", "chip", "microsoft", "apple", "meta", "google", "openai"],
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}

REDDIT_HEADERS = {
    "User-Agent": "LFGlobalCapital-SubstackBot/1.0 (by LucasFO)"
}

DATA_DIR   = "/Users/lucasfdezortiz/substack-assistant/data"
CACHE_FILE = "/Users/lucasfdezortiz/substack-assistant/data/latest_ideas.json"

CACHE_TTL_HOURS = 6
TOP_ITEMS = 18          # slightly more to accommodate research items
RESEARCH_BOOST = 5     # extra relevance score for institutional research
