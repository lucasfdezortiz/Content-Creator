import sys
import json
import argparse
import subprocess
import os
from datetime import datetime, timedelta

from config import CACHE_FILE, CACHE_TTL_HOURS, FOCUS_KEYWORDS
from scheduled_reports import format_calendar_block

try:
    from chart_generator import generate_chart_for_text
    USE_LOCAL_CHARTS = True
except ImportError:
    from chart_urls import pick_chart_for_text as generate_chart_for_text
    USE_LOCAL_CHARTS = False


def load_content(focus: str = None) -> dict:
    stale = True
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            fetched_at = datetime.fromisoformat(data.get("fetched_at", "2000-01-01"))
            if datetime.now() - fetched_at < timedelta(hours=CACHE_TTL_HOURS):
                stale = False
        except Exception:
            pass

    if stale:
        args = ["python", os.path.join(os.path.dirname(__file__), "fetch_content.py")]
        if focus:
            args += ["--focus", focus]
        subprocess.run(args, check=True)

    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def build_context_block(items: list) -> str:
    lines = []
    for i, item in enumerate(items, 1):
        source     = item.get("source", "")
        title      = item.get("title", "")
        url        = item.get("url", "")
        summary    = item.get("summary", "")
        score      = item.get("relevance_score", 0)
        reddit     = item.get("reddit_score", 0)
        is_research = item.get("is_research", False)

        tag = " ★ RESEARCH" if is_research else ""
        lines.append(f"[{i}] {source}{tag} | Score: {score}" + (f" | Reddit: {reddit:,}" if reddit > 0 else ""))
        lines.append(f"    {title}")
        if summary:
            lines.append(f"    {summary[:250]}")
        if url:
            lines.append(f"    {url}")
        lines.append("")
    return "\n".join(lines)


def main(focus: str = None):
    data    = load_content(focus=focus)
    items   = data.get("items", [])
    fetched = data.get("fetched_at", "")[:16].replace("T", " ")
    count   = data.get("count", len(items))
    sources = len(set(i.get("source", "") for i in items))

    focus_label = f" | Focus: {focus.upper()}" if focus else ""

    print("=" * 65)
    print(f"  SUBSTACK CONTENT ASSISTANT — LF GLOBAL CAPITAL")
    print(f"  Fecha: {fetched}{focus_label}")
    print(f"  {count} noticias de {sources} fuentes")
    print("=" * 65)
    print()
    print("--- NOTICIAS FILTRADAS ---")
    print()
    print(build_context_block(items))
    print()
    # Pick charts based on top news items
    note1_chart, note1_label = generate_chart_for_text(" ".join(
        i.get("title", "") for i in items[:2]))
    note2_chart, note2_label = generate_chart_for_text(" ".join(
        i.get("title", "") for i in items[2:5]))
    thread_chart, thread_label = generate_chart_for_text(items[0].get("title", "") if items else "")

    calendar_block = format_calendar_block()
    if calendar_block:
        print("=" * 65)
        print(calendar_block)

    chart_mode = "LOCAL — http://localhost:8765/" if USE_LOCAL_CHARTS else "Yahoo Finance / FRED"
    print("=" * 65)
    print(f"  GRÁFICAS ({chart_mode})")
    print("=" * 65)
    print(f"\nNOTE 1  → {note1_label}")
    print(f"         {note1_chart}")
    print(f"\nNOTE 2  → {note2_label}")
    print(f"         {note2_chart}")
    print(f"\nTHREAD  → {thread_label}")
    print(f"         {thread_chart}")
    print()

    print("=" * 65)
    print("  INSTRUCCIONES PARA CLAUDE")
    print("=" * 65)
    print("""
Con las noticias y eventos anteriores, genera contenido para
el Substack LF GLOBAL CAPITAL. Solo usa datos del contexto.

VOZ Y TONO — MUY IMPORTANTE:
• Informativo y directo. Lucas comparte lo que está pasando,
  no da lecciones ni explica conceptos básicos a nadie.
• Primera persona natural: "vi esto esta mañana", "me parece
  llamativo que...", "lo que no aparece en el titular es..."
• No concluyas ni des moralejas. Presenta el dato, añade
  contexto, deja que el lector saque sus conclusiones.
• Nada de "lo que debemos aprender" ni "esto nos enseña que".
• Tono de alguien que comparte una noticia interesante que
  encontró, no de profesor explicando un concepto.

────────────────────────────────────────────────────────────────
 1. DOS NOTES (listas para publicar)
────────────────────────────────────────────────────────────────
• Elige los 2 temas más relevantes o llamativos del contexto
• Longitud: 100-150 palabras cada una
• Estructura sugerida (no rígida):
    - Abre con el dato o hecho concreto que llama la atención
    - Añade contexto: por qué importa ahora, qué lo rodea
    - Una línea de tu reacción o perspectiva personal, sin pontificar
    - Opcional: pregunta abierta al lector (no obligatoria)
• Si hay ★ RESEARCH en el contexto, priorízalo como fuente
• Formato:

    [TEXTO — 100-150 palabras]
    📊 Gráfica: [fuente + serie/ticker exacto]
    🔗 Fuente: [nombre + URL]

────────────────────────────────────────────────────────────────
 2. TRES IDEAS DE POST LARGO
────────────────────────────────────────────────────────────────
• Para cada idea:

    TÍTULO: [SEO, directo, basado en el dato o noticia concreta]
    POR QUÉ AHORA: [qué noticia o informe del contexto lo dispara]
    OUTLINE:
      1. El dato o hecho que abre el post
      2. Contexto: qué más está pasando alrededor
      3. Qué dicen los datos / fuentes institucionales (si las hay)
      4. Qué ve Lucas en esto que no está en el titular
    GRÁFICA CLAVE: [fuente + símbolo]
    FUENTE: [URL]

────────────────────────────────────────────────────────────────
 3. HILO DE TWITTER/X (2-3 tweets)
────────────────────────────────────────────────────────────────
• Elige la noticia con más gancho informativo del contexto
• Formato:

    🧵 Tweet 1: [dato concreto o hecho que para el scroll — sin intro]
    Tweet 2: [más contexto o dato complementario]
    Tweet 3: [lo que ves tú en esto o pregunta abierta — opcional]

• Sin hashtags. Máx 280 caracteres por tweet.
• Tono: compartir algo interesante que encontraste, no anunciar nada.
• Gráfica para tweet 1 si hay una que apoye el dato.

Genera en español. Empieza directamente con las Notes.
""")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--focus", default=None, choices=list(FOCUS_KEYWORDS.keys()))
    args = parser.parse_args()
    main(focus=args.focus)
