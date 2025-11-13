# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Dict, List, Set, Tuple, Optional
import re, os, time, json, io, importlib, sys

EPS = "e"
NONTERM_RE = re.compile(r"^[A-Z]$")

def _normalize_arrow(s: str) -> str:
    return (s.replace("→", "->").replace("⇒", "->").replace("⟶", "->").replace(":", "->"))

def _is_epsilon(tok: str) -> bool:
    return tok.strip() in ("", EPS, "ε")

def _lhs_is_single_nonterminal(lhs: str) -> bool:
    return len(lhs) == 1 and NONTERM_RE.match(lhs) is not None

class Grammar:
    def __init__(self, start: str = "S"):
        self.start = start
        self.rules: Dict[str, List[str]] = {}
    def add(self, left: str, prod: str) -> None:
        self.rules.setdefault(left, []).append(prod)
    def nonterminals(self) -> Set[str]:
        return set(self.rules.keys())

def parse_grammar(text: str, default_start: str = "S") -> Grammar:
    g = Grammar(start=default_start)
    for raw in text.splitlines():
        line = _normalize_arrow(raw.strip())
        if not line or line.startswith("#"): continue
        if "->" not in line: continue
        left, right = [p.strip() for p in line.split("->", 1)]
        if not left: continue
        alts = re.split(r"\||;", right)
        for a in alts:
            a = a.strip()
            g.add(left, "" if _is_epsilon(a) else a.replace(" ", ""))
    return g

def _is_regular_right_linear(g: Grammar) -> Tuple[bool, str]:
    for A, prods in g.rules.items():
        if not _lhs_is_single_nonterminal(A):
            return False, f"LHS '{A}' no es un no terminal simple."
        for p in prods:
            if p == "":
                continue
            if len(p) == 1:
                if not p.islower():
                    return False, f"Producción {A}->{p} no es terminal simple."
                continue
            if len(p) == 2 and p[0].islower() and p[1].isupper():
                continue
            return False, f"Producción {A}->{p} no cumple A->aB | a | ε."
    return True, "Todas las producciones son A->aB | a | ε."

def _is_context_free(g: Grammar) -> Tuple[bool, str]:
    for A in g.rules:
        if not _lhs_is_single_nonterminal(A):
            return False, f"LHS '{A}' invalida GLC (debe ser no terminal simple)."
    return True, "Todos los LHS son un solo no terminal (GLC)."

def _is_context_sensitive(g: Grammar) -> Tuple[bool, str]:
    for A, prods in g.rules.items():
        for p in prods:
            if len(A) == 0:
                return False, f"LHS vacío en {A}->{p}."
            if p != "" and len(A) > len(p):
                return False, f"Longitud decrece en {A}->{p}."
    return True, "No hay contracciones de longitud (|α|≤|β|)."

def _classify_dict(rules_text: str) -> Dict:
    g = parse_grammar(rules_text)
    ok3, why3 = _is_regular_right_linear(g)
    if ok3:
        return {"type_id": 3, "type_name": "Regular (Tipo 3)", "explanation": why3}
    ok2, why2 = _is_context_free(g)
    if ok2:
        return {"type_id": 2, "type_name": "Libre de Contexto (Tipo 2)", "explanation": why2}
    ok1, why1 = _is_context_sensitive(g)
    if ok1:
        return {"type_id": 1, "type_name": "Sensible al Contexto (Tipo 1)", "explanation": why1}
    return {"type_id": 0, "type_name": "Recursivamente Enumerable (Tipo 0)",
            "explanation": "No cumple restricciones de tipos 1–3."}

def classify_grammar_text(rules_text: str) -> Tuple[str, str]:
    res = _classify_dict(rules_text)
    return res["type_name"], res["explanation"]

def explain_grammar_steps(rules_text: str) -> List[str]:
    g = parse_grammar(rules_text)
    steps: List[str] = []
    lhs_bad = [A for A in g.rules if not _lhs_is_single_nonterminal(A)]
    if lhs_bad:
        steps.append(f"❌ LHS no simples: {', '.join(lhs_bad)} → no puede ser Tipo 2/3.")
    else:
        steps.append("✅ Todos los LHS son no terminales simples (candidato a Tipo 2/3).")
    ok3, why3 = _is_regular_right_linear(g); steps.append(("✅ " if ok3 else "ℹ️ ") + why3)
    ok2, why2 = _is_context_free(g);      steps.append(("✅ " if ok2 else "ℹ️ ") + why2)
    ok1, why1 = _is_context_sensitive(g); steps.append(("✅ " if ok1 else "ℹ️ ") + why1)
    final = _classify_dict(rules_text)["type_name"]; steps.append(f"➡️ Clasificación final: {final}")
    return steps

# ---------------- Regex → Gramática ----------------
def _insert_concat_ops(regex: str) -> str:
    out, prev = [], ""
    for c in regex:
        if c == " ": continue
        if prev and ((prev.isalnum() or prev in (")", "*")) and (c.isalnum() or c == "(")):
            out.append(".")
        out.append(c); prev = c
    return "".join(out)

def _to_postfix(regex: str) -> str:
    prec = {"*": 3, ".": 2, "|": 1}
    output, stack = [], []
    for c in regex:
        if c.isalnum(): output.append(c)
        elif c == "(": stack.append(c)
        elif c == ")":
            while stack and stack[-1] != "(": output.append(stack.pop())
            if stack and stack[-1] == "(": stack.pop()
        else:
            if c not in prec: raise ValueError(f"Operador no soportado: {c}")
            while stack and stack[-1] != "(" and prec.get(stack[-1], 0) >= prec[c]:
                output.append(stack.pop())
            stack.append(c)
    while stack: output.append(stack.pop())
    return "".join(output)

class _NFA:
    def __init__(self, start: int, accepts: Set[int], trans: Dict[Tuple[int, Optional[str]], Set[int]]):
        self.start = start; self.accepts = accepts; self.trans = trans

def _nfa_symbol(a: str, sid: int) -> _NFA:
    s, f = sid, sid+1
    return _NFA(s, {f}, {(s, a): {f}})

def _nfa_concat(n1: _NFA, n2: _NFA) -> _NFA:
    trans = {}
    for k,v in n1.trans.items(): trans.setdefault(k,set()).update(v)
    for k,v in n2.trans.items(): trans.setdefault(k,set()).update(v)
    for a in n1.accepts: trans.setdefault((a, None), set()).add(n2.start)
    return _NFA(n1.start, n2.accepts, trans)

def _nfa_union(n1: _NFA, n2: _NFA, sid: int) -> _NFA:
    s, f = sid, sid+1
    trans = {}
    for k,v in n1.trans.items(): trans.setdefault(k,set()).update(v)
    for k,v in n2.trans.items(): trans.setdefault(k,set()).update(v)
    trans.setdefault((s, None), set()).update({n1.start, n2.start})
    for a in n1.accepts: trans.setdefault((a, None), set()).add(f)
    for a in n2.accepts: trans.setdefault((a, None), set()).add(f)
    return _NFA(s, {f}, trans)

def _nfa_star(n: _NFA, sid: int) -> _NFA:
    s, f = sid, sid+1
    trans = {}
    for k,v in n.trans.items(): trans.setdefault(k,set()).update(v)
    trans.setdefault((s, None), set()).update({n.start, f})
    for a in n.accepts: trans.setdefault((a, None), set()).update({n.start, f})
    return _NFA(s, {f}, trans)

def _build_nfa(regex: str) -> _NFA:
    regex = _insert_concat_ops(regex)
    postfix = _to_postfix(regex)
    stack: List[_NFA] = []; next_id = 0
    for c in postfix:
        if c.isalnum(): stack.append(_nfa_symbol(c, next_id)); next_id += 2
        elif c == ".": b=stack.pop(); a=stack.pop(); stack.append(_nfa_concat(a,b))
        elif c == "|": b=stack.pop(); a=stack.pop(); stack.append(_nfa_union(a,b,next_id)); next_id += 2
        elif c == "*": a=stack.pop(); stack.append(_nfa_star(a,next_id)); next_id += 2
        else: raise ValueError(f"Token no soportado en postfix: {c}")
    if len(stack)!=1: raise ValueError("Regex inválida.")
    return stack[0]

def _epsilon_closure(state: int, trans: Dict[Tuple[int, Optional[str]], Set[int]]) -> Set[int]:
    stack, vis = [state], {state}
    while stack:
        s = stack.pop()
        for t in trans.get((s, None), set()):
            if t not in vis: vis.add(t); stack.append(t)
    return vis

def _grammar_to_text(G) -> str:
    lines=[]
    for A, prods in G.rules.items():
        alts=[]
        for p in prods: alts.append(EPS if p=="" else p)
        lines.append(f"{A} -> " + " | ".join(alts))
    return "\n".join(lines)

def regex_to_right_linear_grammar(regex: str) -> Tuple[bool, str]:
    try:
        nfa = _build_nfa(regex)
        states=set([nfa.start]+list(nfa.accepts))
        for (s,a),d in list(nfa.trans.items()): states.add(s); states |= set(d)
        order = sorted(states)
        name_of={}
        for i,s in enumerate(order): name_of[s] = "S" if s==nfa.start else f"A{i}"
        G = Grammar(start="S")
        closure={s:_epsilon_closure(s,nfa.trans) for s in order}
        for (s,a),dests in list(nfa.trans.items()):
            if a is None: continue
            for q in dests:
                for r in closure[q]:
                    G.add(name_of[s], f"{a}{name_of[r]}")
        for s in order:
            if any(r in nfa.accepts for r in closure[s]): G.add(name_of[s], "")
        return True, _grammar_to_text(G)
    except Exception as e:
        return False, f"Error: {e}"

# ---------------- PNG de gramática (FIX DE IMPORT) ----------------
def _load_visualizer():
    """
    Carga robusta del módulo visualizer:
    1) paquete absoluto 'chomsky_classifier_ai.visualizer'
    2) módulo local 'visualizer' si se ejecuta suelto
    """
    try:
        return importlib.import_module("chomsky_classifier_ai.visualizer")
    except Exception:
        try:
            return importlib.import_module("visualizer")
        except Exception as e:
            raise RuntimeError(f"No pude importar visualizer: {e}")

def generate_grammar_png(rules_text: str, out_dir: str = "output") -> str:
    viz = _load_visualizer()
    os.makedirs(out_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    out_path = os.path.join(out_dir, f"grammar_{ts}.png")
    viz.build_grammar_graph_png(rules_text, out_path)
    if not os.path.exists(out_path):
        raise RuntimeError("El visualizador no creó el PNG.")
    return out_path

def classify_automaton_json(jtxt: str) -> Tuple[int, str]:
    try:
        data = json.loads(jtxt)
    except Exception as e:
        return 0, f"JSON inválido: {e}"
    t = str(data.get("type", "")).strip().upper()
    mapping = {"DFA": 3, "NFA": 3, "PDA": 2, "LBA": 1, "TM": 0, "TURING": 0}
    if t not in mapping:
        return 0, f"Tipo desconocido '{t}'. Usa DFA, NFA, PDA, LBA o TM."
    tipo = mapping[t]
    expl = {
        3: "AFD/AFN reconocen lenguajes regulares (Tipo 3).",
        2: "Un AP reconoce GLC (Tipo 2).",
        1: "Un LBA reconoce lenguajes sensibles al contexto (Tipo 1).",
        0: "Una TM reconoce lenguajes recursivamente enumerables (Tipo 0).",
    }[tipo]
    return tipo, expl

def generate_pdf_report(rules_text: str) -> Tuple[bool, bytes | str]:
    try:
        from .report import build_pdf_bytes as _build_pdf
        return True, _build_pdf(rules_text)
    except Exception:
        pass
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        c.setTitle("Chomsky Classifier - Reporte")
        y = 760
        c.setFont("Helvetica-Bold", 14); c.drawString(72, y, "Chomsky Classifier - Reporte"); y -= 28
        c.setFont("Helvetica", 12); c.drawString(72, y, "Gramática:"); y -= 18
        for line in rules_text.splitlines():
            c.drawString(84, y, line); y -= 16
            if y < 72: c.showPage(); y = 760; c.setFont("Helvetica", 12)
        c.showPage(); c.save()
        pdf = buf.getvalue(); buf.close()
        return True, pdf
    except Exception as e:
        return False, f"No pude generar PDF (instala 'reportlab'): {e}"

def _generate_strings(g: Grammar, max_len: int = 5) -> Set[str]:
    results: Set[str] = set()
    stack: List[Tuple[str, int]] = [(g.start, 0)]
    seen = set(stack)
    while stack:
        sent, depth = stack.pop()
        if depth > max_len: continue
        if not any(ch.isupper() for ch in sent):
            if len(sent) <= max_len: results.add(sent)
            continue
        for i, ch in enumerate(sent):
            if ch.isupper():
                A = ch; left, right = sent[:i], sent[i+1:]
                for p in g.rules.get(A, [""]):
                    new = left + p + right
                    key = (new, depth+1)
                    if len(new) <= max_len and key not in seen:
                        seen.add(key); stack.append(key)
                break
    return results

def compare_grammars_up_to(g1_text: str, g2_text: str, n: int = 6) -> Tuple[float, str]:
    G1, G2 = parse_grammar(g1_text), parse_grammar(g2_text)
    L1, L2 = _generate_strings(G1, n), _generate_strings(G2, n)
    union = L1 | L2; inter = L1 & L2
    sim = (len(inter) / len(union)) if union else 1.0
    notes = (f"|L1∩L2|={len(inter)}, |L1∪L2|={len(union)}\n"
             f"L1-L2: {sorted(L1 - L2)[:20]}\n"
             f"L2-L1: {sorted(L2 - L1)[:20]}")
    return sim, notes

def generate_quiz_question(kind: str = "Aleatoria") -> Dict:
    bank = {
        "Regular": ["S->aA | b\nA->aA | b | e", "S->aS | b | e"],
        "Libre de contexto": ["S->aSb | ab", "S->SS | a"],
        "Sensibles al contexto": ["AB->BA\nA->a", "aB->Ba\nB->b"],
        "Tipo 0": ["S->SSS\nSS->a", "AB->e\nS->AB"],
    }
    mapping_title = {
        "Aleatoria": None, "Regular (3)": "Regular", "Libre de contexto (2)": "Libre de contexto",
        "Sensibles al contexto (1)": "Sensibles al contexto", "Tipo 0": "Tipo 0",
    }
    import random
    bucket = mapping_title.get(kind, None) or random.choice(list(bank.keys()))
    rules = random.choice(bank[bucket])
    answer_num = {"Regular": "3", "Libre de contexto": "2", "Sensibles al contexto": "1", "Tipo 0": "0"}[bucket]
    return {"grammar": rules, "answer": answer_num, "explain": f"Esta gramática es {bucket} (Tipo {answer_num})."}
