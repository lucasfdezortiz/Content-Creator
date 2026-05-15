import streamlit as st
import sys
import json
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

.metrics {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-bottom: 1.8rem;
}
.metric {
    background: #ffffff;
    border: 1px solid #dde3ed;
    border-top: 3px solid #c9a84c;
    border-radius: 10px;
    padding: 1.2rem;
    text-align: center;
}
.metric-val {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.4rem;
    color: #0a1628;
    line-height: 1;
}
.metric-lbl {
    font-family: 'Inter', sans-serif;
    font-size: 0.65rem;
    font-weight: 600;
    color: #8a9bb0;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 6px;
}

.news-card {
    background: #ffffff;
    border: 1px solid #dde3ed;
    border-left: 4px solid #c9a84c;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
}
.news-source {
    font-family: 'Inter', sans-serif;
    font-size: 0.68rem;
    font-weight: 700;
    color: #c9a84c;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 4px;
}
.news-title {
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    color: #0a1628;
    margin-bottom: 4px;
    line-height: 1.4;
}
.news-summary {
    font-family: 'Inter', sans-serif;
    font-size: 0.78rem;
    color: #5a6a80;
    line-height: 1.5;
}
.news-score {
    font-family: 'Inter', sans-serif;
    font-size: 0.65rem;
    color: #a0b0c0;
    margin-top: 6px;
}

.section-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 1.8rem 0 1rem;
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

.content-box {
    background: #ffffff;
    border: 1px solid #dde3ed;
    border-radius: 10px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    white-space: pre-wrap;
    font-family: 'Inter', sans-serif;
    font-size: 0.88rem;
    color: #0a1628;
    line-height: 1.8;
}

.chart-pill {
    display: inline-block;
    background: #f0f4f8;
    border: 1px solid #c9a84c;
    border-radius: 20px;
    padding: 4px 14px;
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    color: #c9a84c;
    margin: 4px 4px 0 0;
    text-decoration: none;
}

.event-card {
    background: #fffbf0;
    border: 1px solid #f0d890;
    border-left: 4px solid #c9a84c;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.5rem;
    font-family: 'Inter', sans-serif;
}
.event-timing {
    font-size: 0.68rem;
    font-weight: 700;
    color: #c9a84c;
    text-transform: uppercase;
    letter-spacing: 2px;
}
.event-label {
    font-size: 0.82rem;
    font-weight: 600;
    color: #0a1628;
    margin-top: 2px;
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
    font-size: 0.78rem !important;
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
    <div class="header-info">{now.strftime('%A, %d %B %Y · %H:%M')} · Fuentes: FT, Reuters, Bloomberg, WSJ, Goldman Sachs, JPMorgan</div>
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

    with st.spinner("Obteniendo noticias de FT, Reuters, Bloomberg, WSJ, Goldman Sachs..."):
        data = fetch_all_content(force=True, focus=focus)

    items = data.get("items", [])
    sources = len(set(i.get("source", "") for i in items))

    st.markdown(f"""
    <div class="metrics">
        <div class="metric">
            <div class="metric-val">{len(items)}</div>
            <div class="metric-lbl">Noticias filtradas</div>
        </div>
        <div class="metric">
            <div class="metric-val">{sources}</div>
            <div class="metric-lbl">Fuentes</div>
        </div>
        <div class="metric">
            <div class="metric-val">{now.strftime('%H:%M')}</div>
            <div class="metric-lbl">Actualizado</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Eventos macro
    events = get_upcoming_events()
    if events:
        st.markdown("""
        <div class="section-header">
            <span class="section-badge">Calendario</span>
            <span class="section-label">Eventos clave esta semana</span>
        </div>
        """, unsafe_allow_html=True)
        for e in events[:5]:
            st.markdown(f"""
            <div class="event-card">
                <div class="event-timing">{e['timing']}</div>
                <div class="event-label">{e['label']}</div>
            </div>
            """, unsafe_allow_html=True)

    # Noticias filtradas
    st.markdown("""
    <div class="section-header">
        <span class="section-badge">Noticias</span>
        <span class="section-label">Filtradas por relevancia</span>
    </div>
    """, unsafe_allow_html=True)

    for item in items[:10]:
        research_tag = " ★ RESEARCH" if item.get("is_research") else ""
        summary = item.get("summary", "")[:200]
        url = item.get("url", "")
        link = f'<a href="{url}" target="_blank" style="font-size:0.68rem;color:#1a6fd4;">Ver fuente →</a>' if url else ""
        st.markdown(f"""
        <div class="news-card">
            <div class="news-source">{item.get('source','')}{research_tag}</div>
            <div class="news-title">{item.get('title','')}</div>
            {'<div class="news-summary">' + summary + '</div>' if summary else ''}
            <div class="news-score">Score: {item.get('relevance_score', 0)} &nbsp;·&nbsp; {link}</div>
        </div>
        """, unsafe_allow_html=True)

    # Gráficas sugeridas
    st.markdown("""
    <div class="section-header">
        <span class="section-badge">Gráficas</span>
        <span class="section-label">Sugeridas según las noticias de hoy</span>
    </div>
    """, unsafe_allow_html=True)

    seen_charts = set()
    charts_html = ""
    for item in items[:8]:
        text = item.get("title", "") + " " + item.get("summary", "")[:100]
        url, label = pick_chart_for_text(text)
        if label not in seen_charts:
            seen_charts.add(label)
            charts_html += f'<a href="{url}" target="_blank" class="chart-pill">📊 {label}</a>'

    st.markdown(f'<div style="margin-bottom:1rem">{charts_html}</div>', unsafe_allow_html=True)

    # Ideas de contenido
    st.markdown("""
    <div class="section-header">
        <span class="section-badge">Contenido</span>
        <span class="section-label">Ideas generadas para hoy</span>
    </div>
    """, unsafe_allow_html=True)

    # Notes para Substack
    st.markdown("**📝 Notes para Substack**")
    for i, item in enumerate(items[:2], 1):
        chart_url, chart_label = pick_chart_for_text(item.get("title", ""))
        note = f"""Note {i} — {item.get('source', '')}

{item.get('title', '')}

{item.get('summary', '')[:300] if item.get('summary') else 'Ver fuente para más detalle.'}

📊 Gráfica sugerida: {chart_label}
🔗 Fuente: {item.get('url', '')}"""
        st.markdown(f'<div class="content-box">{note}</div>', unsafe_allow_html=True)

    # Ideas de post largo
    st.markdown("**📄 Ideas de post largo**")
    for i, item in enumerate(items[2:5], 1):
        chart_url, chart_label = pick_chart_for_text(item.get("title", ""))
        idea = f"""Idea {i}

TÍTULO: {item.get('title', '')}
POR QUÉ AHORA: Noticia destacada en {item.get('source', '')}

OUTLINE:
  1. El dato o hecho que abre el post
  2. Contexto: qué más está pasando alrededor
  3. Qué dicen los datos / fuentes institucionales
  4. Tu perspectiva como inversor

GRÁFICA CLAVE: {chart_label}
FUENTE: {item.get('url', '')}"""
        st.markdown(f'<div class="content-box">{idea}</div>', unsafe_allow_html=True)

    # Hilo de X
    st.markdown("**🐦 Hilo de X**")
    if items:
        top = items[0]
        chart_url, chart_label = pick_chart_for_text(top.get("title", ""))
        hilo = f"""🧵 Tweet 1: {top.get('title', '')[:240]}

Tweet 2: {top.get('summary', '')[:240] if top.get('summary') else 'Más contexto próximamente.'}

Tweet 3: ¿Qué opinas? ¿Cómo afecta esto a tu cartera?

📊 Gráfica: {chart_label}
🔗 {top.get('url', '')}"""
        st.markdown(f'<div class="content-box">{hilo}</div>', unsafe_allow_html=True)