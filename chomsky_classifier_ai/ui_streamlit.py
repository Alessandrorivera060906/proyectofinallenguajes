# -------------------------------
# Chomsky Classifier AI - UI ✨
# Layout ancho + tabs + tarjetas + gradientes
# -------------------------------
from __future__ import annotations
import io
import json
from pathlib import Path

import streamlit as st

# Funciones públicas expuestas por extras.py
from extras import (
    classify_grammar_text,
    explain_grammar_steps,
    regex_to_right_linear_grammar,
    classify_automaton_json,
    generate_pdf_report,
    generate_quiz_question,
    compare_grammars_up_to,
    generate_grammar_png,  # <- genera PNG y devuelve la ruta
)

# ---------- Config básica ----------
st.set_page_config(
    page_title="Chomsky Classifier AI",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- CSS ----------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

.hero {
  padding: 22px 28px; border-radius: 18px;
  background: linear-gradient(135deg, rgba(124,58,237,.20), rgba(236,72,153,.20));
  border: 1px solid rgba(255,255,255,.25);
  box-shadow: 0 10px 30px rgba(0,0,0,.25);
}
.hero-sub { margin-top:6px; opacity:.9; font-size:.98rem; }

.glass {
  border-radius: 16px; background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.18); backdrop-filter: blur(10px);
  padding: 18px 18px 8px; margin-bottom: 14px;
}

.stButton > button {
  background: linear-gradient(135deg,#7C3AED 0%,#EC4899 100%);
  color:#fff; border:0; border-radius:12px; padding:10px 18px; font-weight:600;
  box-shadow:0 6px 18px rgba(124,58,237,.35);
}
.stButton > button:hover { transform: translateY(-1px); box-shadow:0 10px 22px rgba(124,58,237,.45); }

textarea, .stTextInput > div > div > input { border-radius: 12px !important; }

.stTabs [data-baseweb="tab-list"] { gap:6px; }
.stTabs [data-baseweb="tab"] {
  height:44px; background:rgba(255,255,255,.05);
  border-radius:12px; padding:6px 14px; border:1px solid rgba(255,255,255,.15);
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, rgba(124,58,237,.35), rgba(236,72,153,.35));
  color:#fff; border:1px solid rgba(255,255,255,.35);
}

.kpi { border-radius:14px; padding:16px; border:1px dashed rgba(255,255,255,.25); background:rgba(124,58,237,.10); }
.badge { display:inline-block; padding:4px 10px; border-radius:999px; font-size:.80rem; font-weight:600; color:#fff;
         background: linear-gradient(135deg,#22c55e,#16a34a); }
.badge-warn { background: linear-gradient(135deg,#f59e0b,#eab308); }
.badge-info { background: linear-gradient(135deg,#06b6d4,#0ea5e9); }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------- Encabezado ----------
with st.container():
    st.markdown(
        """
        <div class="hero">
          <h1 style="margin-bottom:6px;">Chomsky Classifier AI</h1>
          <div class="hero-sub">Clasifica gramáticas y autómatas, explica el porqué, genera reportes y practica con el modo tutor.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
st.write("")

# ---------- Tabs ----------
tab_grammar, tab_automata, tab_regex, tab_report, tab_explain, tab_quiz, tab_compare = st.tabs(
    ["Gramática", "Autómata", "Regex → Gramática", "Reporte PDF", "Modo explicativo", "Quiz", "Comparar"]
)

# =======================================================
# TAB 1 - Gramática
# =======================================================
with tab_grammar:
    st.markdown("#### Clasificar una gramática")
    colL, colR = st.columns([2, 1])

    with colL:
        default_g = "S -> aA | b\nA -> bA | b | e"
        gtxt = st.text_area("Reglas", height=240, value=default_g, key="gram_rules")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Clasificar", key="btn_classify_grammar"):
                kind, reason = classify_grammar_text(gtxt)
                st.markdown(f"**Tipo detectado:** <span class='badge'>{kind}</span>", unsafe_allow_html=True)
                st.markdown("**Justificación**")
                st.info(reason or "Sin explicación disponible.")

        with c2:
            if st.button("Generar diagrama (PNG)", key="btn_diag_grammar"):
                try:
                    # Genera el PNG y lo mostramos + botón de descarga
                    png_path = generate_grammar_png(gtxt, out_dir="output")
                    with open(png_path, "rb") as f:
                        png_bytes = f.read()

                    st.image(png_bytes, caption=f"Vista previa: {Path(png_path).name}",
                             use_container_width=True)   # <- SIN use_column_width
                    st.download_button("Descargar PNG", data=png_bytes, file_name=Path(png_path).name,
                                       mime="image/png", key="dl_png_grammar")
                except Exception as e:
                    st.error(f"No se pudo generar el diagrama: {e}")

    with colR:
        st.markdown("##### Indicadores")
        st.markdown(
            """
            <div class="kpi">
             • Revisa que cada producción cumpla la forma del tipo detectado.<br/>
             • Usa <code>e</code> o <code>ε</code> para epsilon.<br/>
             • Alternativas: <code>|</code> o <code>;</code><br/>
            </div>
            """, unsafe_allow_html=True
        )

# =======================================================
# TAB 2 - Autómata
# =======================================================
with tab_automata:
    st.markdown("#### Clasificar un autómata")
    default_json = {
        "type": "DFA",
        "states": ["q0", "q1"],
        "alphabet": ["a", "b"],
        "start": "q0",
        "accepts": ["q1"],
        "transitions": {"q0": {"a": "q0", "b": "q1"}, "q1": {"a": "q1", "b": "q1"}}
    }
    jtxt = st.text_area("JSON del autómata", height=260, value=json.dumps(default_json, indent=2), key="auto_json")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Clasificar autómata", key="btn_classify_auto"):
            kind, reason = classify_automaton_json(jtxt)
            st.markdown(f"**Resultado:** <span class='badge-info'>Reconoce lenguaje tipo {kind}</span>",
                        unsafe_allow_html=True)
            st.markdown("**Justificación**")
            st.info(reason or "Sin explicación disponible.")
    with c2:
        st.caption("Puedes pegar un DFA/NFA/AP/MT en JSON. El visualizador (si está disponible) puede generar un grafo.")

# =======================================================
# TAB 3 - Regex → Gramática
# =======================================================
with tab_regex:
    st.markdown("#### Regex → Gramática lineal derecha")
    rx = st.text_input("Expresión regular", "(a|b)*abb", key="rx_input")
    if st.button("Convertir", key="btn_convert_rx"):
        ok, text_or_err = regex_to_right_linear_grammar(rx)
        if ok:
            st.success("Conversión realizada.")
            st.code(text_or_err, language="text")
            st.download_button("Descargar gramatica.txt", text_or_err.encode("utf-8"),
                               file_name="gramatica.txt", mime="text/plain", key="dl_grammar_rx")
        else:
            st.error(text_or_err)

# =======================================================
# TAB 4 - Reporte PDF
# =======================================================
with tab_report:
    st.markdown("#### Generar reporte PDF")
    rules_for_pdf = st.text_area("Reglas", height=220, value="S -> aA | b\nA -> bA | b | e", key="report_rules")
    if st.button("Generar PDF", key="btn_pdf"):
        ok, result = generate_pdf_report(rules_for_pdf)
        if not ok:
            st.error(result)
        else:
            st.success("Reporte listo.")
            st.download_button("Descargar reporte.pdf", data=result, file_name="reporte.pdf",
                               mime="application/pdf", key="dl_pdf")

# =======================================================
# TAB 5 - Modo explicativo
# =======================================================
with tab_explain:
    st.markdown("#### Explicación paso a paso")
    eg = st.text_area("Reglas", height=220, value="S -> aA | b\nA -> bA | b | e", key="explain_rules")
    if st.button("Analizar", key="btn_explain"):
        steps = explain_grammar_steps(eg)
        if not steps:
            st.warning("No se generó explicación.")
        else:
            for i, s in enumerate(steps, 1):
                with st.expander(f"Paso {i}"):
                    st.write(s)

# =======================================================
# TAB 6 - Quiz
# =======================================================
with tab_quiz:
    st.markdown("#### Tutor interactivo")
    kind = st.selectbox("Tipo objetivo",
                        ["Aleatoria", "Regular (3)", "Libre de contexto (2)", "Sensibles al contexto (1)", "Tipo 0"],
                        index=0, key="quiz_kind")
    if st.button("Generar nueva", key="btn_quiz_new"):
        st.session_state["quiz_q"] = generate_quiz_question(kind)
        st.session_state["quiz_user"] = None

    q = st.session_state.get("quiz_q")
    if q:
        st.markdown("**Gramática a clasificar**")
        st.code(q["grammar"], language="text")
        user = st.selectbox("Tu respuesta", ["Tipo 3", "Tipo 2", "Tipo 1", "Tipo 0"], key="quiz_user_select")
        if st.button("Verificar", key="btn_quiz_check"):
            correct = "Tipo " + q["answer"]
            if user == correct:
                st.success(f"¡Correcto! {correct}")
            else:
                st.error(f"No. Correcto: {correct}")
            if q.get("explain"):
                st.info(q["explain"])
    else:
        st.info("Haz clic en **Generar nueva** para iniciar.")

# =======================================================
# TAB 7 - Comparar
# =======================================================
with tab_compare:
    st.markdown("#### Comparar dos gramáticas (heurístico)")
    c1, c2 = st.columns(2)
    with c1:
        g1 = st.text_area("Gramática 1", height=200, value="S -> aS b | ab", key="cmp_g1")
    with c2:
        g2 = st.text_area("Gramática 2", height=200, value="S -> aA; A -> Sb | b", key="cmp_g2")

    n = 6
    if st.button("Comparar", key="btn_compare"):
        sim, notes = compare_grammars_up_to(g1, g2, n)
        st.markdown(f"**Similitud aproximada:** <span class='badge-warn'>{int(sim*100)}%</span>",
                    unsafe_allow_html=True)
        if notes:
            with st.expander("Notas"):
                st.write(notes)
