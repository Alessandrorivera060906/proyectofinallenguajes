import argparse
from .grammar_parser import parse_grammar
from .classifier import classify_grammar

# Opcionales (no fallar si faltan)
try:
    from .visualizer import render_grammar
except Exception:
    render_grammar = None
try:
    from .report import generate_report
except Exception:
    generate_report = None

# Nuevos imports
from .automata_parser import load_automaton_json, classify_automaton
from .regex_automata import regex_to_grammar

def cmd_classify_grammar(args):
    text = open(args.file, "r", encoding="utf-8").read()
    g = parse_grammar(text)
    t, steps = classify_grammar(g)
    print(f"Tipo detectado: {t}")
    for s in steps:
        print("-", s)
    diagram_png = None
    if args.diagram and render_grammar:
        diagram_png = (render_grammar(g, args.diagram) or None)
        print("Diagrama guardado en:", diagram_png if diagram_png else "No disponible.")
    if args.report and generate_report:
        out = generate_report(args.report, "Reporte Chomsky Classifier AI", text, t, steps, diagram_png)
        print("Reporte PDF:", out)

def cmd_classify_automaton(args):
    a = load_automaton_json(args.file)
    atype, ltype = classify_automaton(a)
    print(f"Autómata tipo {atype} -> Lenguaje Tipo {ltype}")

def cmd_regex_to_grammar(args):
    gram = regex_to_grammar(args.regex)
    print("Gramática lineal derecha equivalente:\n")
    print(gram)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(gram)
        print("\nGuardado en:", args.out)

def build_parser():
    p = argparse.ArgumentParser(prog="chomsky-ai", description="Chomsky Classifier AI (CLI)")
    sub = p.add_subparsers()

    p1 = sub.add_parser("classify-grammar", help="Clasificar una gramática desde archivo .txt")
    p1.add_argument("file", help="Ruta al archivo con reglas")
    p1.add_argument("--diagram", help="Ruta base para guardar diagrama (sin extensión)", default=None)
    p1.add_argument("--report", help="Ruta del PDF a generar", default=None)
    p1.set_defaults(func=cmd_classify_grammar)

    p2 = sub.add_parser("classify-automaton", help="Clasificar autómata (JSON con campo 'type')")
    p2.add_argument("file", help="Ruta al archivo .json")
    p2.set_defaults(func=cmd_classify_automaton)

    p3 = sub.add_parser("regex-to-grammar", help="Convertir una regex a gramática lineal derecha")
    p3.add_argument("regex", help="Expresión regular entre comillas")
    p3.add_argument("--out", help="Ruta para guardar la gramática", default=None)
    p3.set_defaults(func=cmd_regex_to_grammar)

    return p

def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
