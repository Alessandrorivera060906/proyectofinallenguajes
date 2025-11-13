import streamlit as st
from chomsky_classifier_ai.grammar_parser import parse_grammar
from chomsky_classifier_ai.classifier import classify_grammar
from chomsky_classifier_ai.visualizer import render_grammar
from chomsky_classifier_ai.report import generate_report
from chomsky_classifier_ai.automata_parser import parse_automaton, classify_automaton_type
from chomsky_classifier_ai.regex_automata import nfa_from_regex, dfa_from_nfa, regular_grammar_from_dfa

st.set_page_config(page_title="Chomsky Classifier AI", layout="wide")
st.title("Chomsky Classifier AI")

tabs = st.tabs(["Gramática", "Autómata", "Regex ⇄ Gramática", "Reporte PDF"])

with tabs[0]:
    st.subheader("Clasificar Gramática")
    default = "S -> aA | b\nA -> bA | b"
    text = st.text_area("Producciones (una por línea)", default, height=200)
    if st.button("Clasificar", key="gbtn"):
        try:
            g = parse_grammar(text)
            t, steps = classify_grammar(g)
            st.success(f"Tipo detectado: {t}")
            for s in steps:
                st.write("•", s)
            if st.button("Generar diagrama"):
                out = render_grammar(g, "output/grammar")
                if out:
                    st.image(out, caption="Diagrama")
                else:
                    st.warning("Instala 'graphviz' para generar diagramas.")
        except Exception as e:
            st.error(str(e))

with tabs[1]:
    st.subheader("Clasificar Autómata (JSON)")
    sample = '{"type":"DFA","states":["q0","q1"],"alphabet":["a","b"],"start":"q0","accepts":["q1"],"transitions":{"q0":{"a":"q1","b":"q0"},"q1":{"a":"q1","b":"q0"}}}'
    text = st.text_area("JSON del autómata", sample, height=180, key="auto")
    if st.button("Clasificar", key="abtn"):
        try:
            a_type, obj = parse_automaton(text)
            t = classify_automaton_type(a_type)
            st.success(f"Automáta {a_type} ⇒ Lenguaje Tipo {t}")
        except Exception as e:
            st.error(str(e))

with tabs[2]:
    st.subheader("Regex → DFA → Gramática Regular")
    regex = st.text_input("Expresión regular", "(a|b)*abb")
    if st.button("Convertir", key="rbtn"):
        try:
            nfa = nfa_from_regex(regex)
            dfa = dfa_from_nfa(nfa)
            start, prods = regular_grammar_from_dfa(dfa)
            by_lhs = {}
            for lhs, rhs in prods:
                by_lhs.setdefault(lhs, []).append(rhs)
            out_lines = [f"{lhs} -> " + " | ".join(rhss) for lhs, rhss in by_lhs.items()]
            st.code("\n".join(out_lines), language="text")
        except Exception as e:
            st.error(str(e))

with tabs[3]:
    st.subheader("Generar Reporte PDF")
    text = st.text_area("Pega aquí la gramática para el reporte.", height=140, key="rep")
    if st.button("Generar PDF"):
        try:
            g = parse_grammar(text)
            t, steps = classify_grammar(g)
            path = generate_report("output/reporte.pdf", "Reporte Chomsky Classifier AI", text, t, steps, diagram_path=None)
            st.success("Reporte generado: output/reporte.pdf")
            with open(path, "rb") as f:
                st.download_button("Descargar reporte.pdf", f, file_name="reporte.pdf")
        except Exception as e:
            st.error(str(e))
