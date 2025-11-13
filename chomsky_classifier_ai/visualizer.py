# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Dict, List, Set, Tuple
import os

def _parse_rules(text: str) -> Dict[str, List[str]]:
    # igual que en extras, pero local para evitar import circular
    def norm(line: str) -> str:
        return (line.replace("→", "->")
                    .replace("⇒", "->")
                    .replace("⟶", "->")
                    .replace(":", "->"))
    rules: Dict[str, List[str]] = {}
    for raw in text.splitlines():
        line = norm(raw.strip())
        if not line or line.startswith("#") or "->" not in line:
            continue
        left, right = [p.strip() for p in line.split("->", 1)]
        alts = [a.strip() for a in __import__("re").split(r"\||;", right)]
        for a in alts:
            a = "" if a in ("", "e", "ε") else a.replace(" ", "")
            rules.setdefault(left, []).append(a)
    return rules

def _build_graphviz_png(rules_text: str, out_path: str) -> None:
    from graphviz import Digraph  # puede no estar instalado
    rules = _parse_rules(rules_text)
    dot = Digraph("Grammar", format="png")
    dot.attr(rankdir="LR", bgcolor="white")
    dot.attr("node", shape="circle")

    # nodos
    nts = list(rules.keys())
    for A in nts:
        dot.node(A)
    dot.node("ACCEPT", shape="doublecircle")

    # aristas
    for A, prods in rules.items():
        for p in prods:
            if p == "":
                dot.edge(A, "ACCEPT", label="ε")
            elif p[-1:].isupper():
                B = p[-1]
                lbl = p[:-1] or "ε"
                dot.edge(A, B, label=lbl)
            else:
                dot.edge(A, "ACCEPT", label=p)

    # graphviz necesita path sin extensión
    root, _ = os.path.splitext(out_path)
    dot.render(filename=root, cleanup=True)

def _fallback_pillow_png(rules_text: str, out_path: str) -> None:
    from PIL import Image, ImageDraw, ImageFont
    lines = ["Gramática (diagrama simplificado)", ""] + rules_text.splitlines()
    width = 1200
    line_h = 32
    pad = 30
    height = pad*2 + line_h*len(lines)

    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
        font_b = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
        font_b = font
    y = pad
    draw.text((pad, y), lines[0], fill=(40,40,40), font=font_b); y += line_h*2//3 + 10
    for line in lines[1:]:
        draw.text((pad, y), line, fill=(60,60,60), font=font); y += line_h
    img.save(out_path, "PNG")

def build_grammar_graph_png(rules_text: str, out_path: str) -> None:
    """
    Intenta con Graphviz; si no existe, usa Pillow como fallback.
    """
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    try:
        _build_graphviz_png(rules_text, out_path)
    except Exception:
        _fallback_pillow_png(rules_text, out_path)
