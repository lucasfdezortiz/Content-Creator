import streamlit as st
import sys
import os
from datetime import datetime

sys.path.insert(0, "/mount/src/content-creator")

st.set_page_config(page_title="LF Global Capital — Content Studio", page_icon="📰", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Bebas+Neue&display=swap');

html, body, .stApp { background-color: #f5f7fa !important; }

.header {
    background: #0a1628;
    border-radius: 14px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    border-left: 5px solid #c9a84c;
}
.header-eyebrow {
    font-family: 'Inter', sans-serif;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #c9a84c;
    margin-bottom: 0.5rem;
}
.header-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3rem;
    color: #ffffff;
    letter-spacing: 4px;
    line-height: 1;
    margin-bottom: 0.4rem;
}
.header-title span { color: #c9a84c; }
.header-info {
    font-family: 'Inter', sans-serif;
    font-size: 0.78rem;
    color: #8a9bb0;
    margin-top: 0.5rem;
}

.content-section {
    background: #ffffff;
    border: 1px solid #dde3ed;
    border-top: 3px solid #c9a84c;
    border-radius: 12px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.2rem;
}
.content-section.blue { border-top-color: #1a6fd4; }
.content-section.green { border-top-color: #1a9c50; }

.content-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #c9a84c;
    margin-bottom: 0.8rem;
}
.content-label.blue { color: #1a6fd4; }
.content-label.green { color: #1a9c50; }

.content-title {
    font-family: 'Inter', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #0a1628;
    margin-bottom: 0.8rem;
    line-height: 1.4;
}

.content-body {
    font-family: 'Inter', sans-serif;
    font-size: 0.88rem;
    color: #2a3a50;
    line-height: 1.8;
    white-space: pre-wrap;
}

.content-footer {
    margin-top: 1rem;
    padding-top: 0.8rem;
    border-top: 1px solid #f0f2f5;
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
}
.chart-pill {
    display: inline-block;
    background: #f5f7fa;
    border: 1px solid #c9a84c;
    border-radius: 20px;
    padding: 4px 14px;
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    color: #c9a84c;
    text-decoration: none;
}
.source-link {
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    color: #1a6fd4;
    text-decoration: none;
}

.section-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 2rem 0 1rem;
    padding-bottom: 0.7rem;
    border-bottom: 2px solid #dde3ed;
}
.section-badge {
    font-family: 'Inter', sans-serif;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 2px;
    padding: 4px 12px;
    border-radius: 4px;
    background: #0a1628;
    color: #ffffff;
    text-transform: uppercase;
}
.section-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    color: #0a1628;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.news-card {
    background: #ffffff;
    border: 1px solid #dde3ed;
    border-left: 3px solid #dde3ed;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.5rem;
}
.news-card.research { border-left-color: #c9a84c; }
.news-source {
    font-family: 'Inter', sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    color: #8a9bb0;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 3px;
}
.news-source.research { color: #c9a84c; }
.news-title {
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    color: #0a1628;
    line-height: 1.4;
}

.event-card {
    background: #fffbf0;
    border: 1px solid #f0d890;
    border-left: 3px solid #c9a84c;
    border-radius: 8px;
    padding: 0.7rem 1rem;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 12px;
}
.event-timing {
    font-family: 'Inter', sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    color: #c9a84c;
    text-transform: uppercase;
    letter-spacing: 2px;
    min-width: 70px;
}
.event-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.82rem;
    font-weight: 500;
    color: #0a1628;
}

div[data-testid="stButton"] > button {
    background: #0a1628 !important;
    color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.8rem !important;
    width: 100% !important;
}
div[data-testid="stButton"] > button:hover { background: #c9a84c !important; color: #0a1628 !important; }

div[data-testid="stSelectbox"] label {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    color: #0a1628 !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
}
</style>
""", unsafe_allow_html=True)

now = datetime.now()
st.markdown(f"""
<div class="header">
    <div class="header-eyebrow">Substack · X · LF Global Capital</div>
    <div class="header-title">Content <span>Studio</span></div>
    <div class="header-info">{now.strftime('%A, %d %B %Y · %H:%M')} · FT · Reuters · Bloomberg · WSJ · Goldman Sachs · JPMorgan · BlackRock</div>
</div>
""", unsafe_allow_html=True)

focus_options = {
    "Todo": None,
    "Macro": "macro",
    "Acciones": "stocks",
    "Crypto": "crypto",
    "España": "spain",
    "Tech": "tech",
}

col1, col2 = st.columns([3, 1])
with col2:
    focus_label = st.selectbox("Filtrar por tema", list(focus_options.keys()))
focus = focus_options[focus_label]

with col1:
    run = st.button("📰  GENERAR CONTENIDO DE HOY")

if run:
    from fetch_content import fetch_all_content
    from scheduled_reports import get_upcoming_events
    from chart_urls import pick_chart_for_text

    with st.spinner("Obteniendo noticias de FT, Reuters, Bloomberg, Goldman Sachs, JPMorgan..."):
        data = fetch_all_content(force=True, focus=focus)

    items = data.get("items", [])

    if not items:
        st.warning("No se pudieron obtener noticias. Inténtalo de nuevo.")
        st.stop()

    # ── CONTENIDO PRIMERO ──────────────────────────────────────────────────

    st.markdown("""
    <div class="section-header">
        <span class="section-badge">Contenido</span>
        <span class="section-label">Listo para publicar hoy</span>
    </div>
    """, unsafe_allow_html=True)

    # NOTE 1
    item1 = items[0]
    chart_url1, chart_label1 = pick_chart_for_text(item1.get("title","") + " " + item1.get("summary","")[:100])
    summary1 = item1.get("summary","")[:400]
    note1_text = f"""{item1.get('title','')}

{summary1}

Lo que no aparece en el titular: esto se produce en un momento en que los mercados llevan semanas descontando un escenario concreto. Si los datos confirman lo que apunta esta noticia, el movimiento puede ser más brusco de lo que el consenso espera.

— LF 🌍"""

    st.markdown(f"""
    <div class="content-section">
        <div class="content-label">📝 Note 1 — Substack</div>
        <div class="content-body">{note1_text}</div>
        <div class="content-footer">
            <a href="{chart_url1}" target="_blank" class="chart-pill">📊 {chart_label1}</a>
            <a href="{item1.get('url','')}" target="_blank" class="source-link">🔗 {item1.get('source','')} →</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # NOTE 2
    item2 = items[1] if len(items) > 1 else items[0]
    chart_url2, chart_label2 = pick_chart_for_text(item2.get("title","") + " " + item2.get("summary","")[:100])
    summary2 = item2.get("summary","")[:400]
    note2_text = f"""{item2.get('title','')}

{summary2}

El dato que me parece llamativo: el mercado lleva tiempo ignorando señales como esta. Cuando el consenso empieza a moverse, el ajuste suele ser rápido.

— LF 🌍"""

    st.markdown(f"""
    <div class="content-section">
        <div class="content-label">📝 Note 2 — Substack</div>
        <div class="content-body">{note2_text}</div>
        <div class="content-footer">
            <a href="{chart_url2}" target="_blank" class="chart-pill">📊 {chart_label2}</a>
            <a href="{item2.get('url','')}" target="_blank" class="source-link">🔗 {item2.get('source','')} →</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # HILO DE X
    item_x = items[0]
    chart_url_x, chart_label_x = pick_chart_for_text(item_x.get("title",""))
    tweet1 = item_x.get("title","")[:240]
    tweet2 = item_x.get("summary","")[:240] if item_x.get("summary") else "El contexto macro que rodea esto lo cambia todo."
    tweet3 = "¿Cómo está afectando esto a tu cartera? Yo lo estoy siguiendo de cerca."

    hilo_text = f"""🧵 {tweet1}

{tweet2}

{tweet3}

📊 {chart_label_x}
🔗 {item_x.get('url','')}"""

    st.markdown(f"""
    <div class="content-section blue">
        <div class="content-label blue">🐦 Hilo de X</div>
        <div class="content-body">{hilo_text}</div>
        <div class="content-footer">
            <a href="{chart_url_x}" target="_blank" class="chart-pill" style="border-color:#1a6fd4;color:#1a6fd4;">📊 {chart_label_x}</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # IDEAS DE POST LARGO
    st.markdown("""
    <div class="section-header">
        <span class="section-badge" style="background:#1a9c50">Ideas</span>
        <span class="section-label">Posts largos para desarrollar</span>
    </div>
    """, unsafe_allow_html=True)

    for i, item in enumerate(items[2:5], 1):
        chart_url_i, chart_label_i = pick_chart_for_text(item.get("title",""))
        idea_text = f"""TÍTULO: {item.get('title','')}

POR QUÉ AHORA: {item.get('source','')} acaba de publicar esto. El mercado aún no lo ha descontado del todo.

OUTLINE:
  1. El dato concreto que abre el post — sin rodeos
  2. Qué está pasando alrededor que lo amplifica
  3. Qué dicen las fuentes institucionales (GS, JPM, BlackRock)
  4. Lo que yo veo que no está en el titular

GRÁFICA CLAVE: {chart_label_i}
FUENTE: {item.get('url','')}"""

        st.markdown(f"""
        <div class="content-section green">
            <div class="content-label green">💡 Idea de post {i}</div>
            <div class="content-body">{idea_text}</div>
            <div class="content-footer">
                <a href="{chart_url_i}" target="_blank" class="chart-pill" style="border-color:#1a9c50;color:#1a9c50;">📊 {chart_label_i}</a>
                <a href="{item.get('url','')}" target="_blank" class="source-link">🔗 {item.get('source','')} →</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── NOTICIAS Y EVENTOS DEBAJO ──────────────────────────────────────────

    # Eventos macro
    events = get_upcoming_events()
    if events:
        st.markdown("""
        <div class="section-header">
            <span class="section-badge">Calendario</span>
            <span class="section-label">Eventos clave esta semana</span>
        </div>
        """, unsafe_allow_html=True)
        for e in events[:6]:
            st.markdown(f"""
            <div class="event-card">
                <div class="event-timing">{e['timing']}</div>
                <div class="event-label">{e['label']}</div>
            </div>
            """, unsafe_allow_html=True)

    # Noticias
    st.markdown("""
    <div class="section-header">
        <span class="section-badge">Noticias</span>
        <span class="section-label">Filtradas por relevancia hoy</span>
    </div>
    """, unsafe_allow_html=True)

    for item in items[:12]:
        is_research = item.get("is_research", False)
        research_tag = " ★" if is_research else ""
        card_class = "research" if is_research else ""
        source_class = "research" if is_research else ""
        url = item.get("url","")
        title = item.get("title","")
        if url:
            title_html = f'<a href="{url}" target="_blank" style="color:#0a1628;text-decoration:none;">{title}</a>'
        else:
            title_html = title
        st.markdown(f"""
        <div class="news-card {card_class}">
            <div class="news-source {source_class}">{item.get('source','')}{research_tag}</div>
            <div class="news-title">{title_html}</div>
        </div>
        """, unsafe_allow_html=True)