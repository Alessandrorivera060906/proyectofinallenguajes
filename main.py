import argparse, os
from .grammar_parser import parse_grammar, Grammar
from .classifier import classify_grammar
from .visualizer import render_grammar
from .report import generate_report
from .automata_parser import parse_automaton, classify_automaton_type
from .regex_automata import nfa_from_regex, dfa_from_nfa, regular_grammar_from_dfa

def cmd_classify_grammar(args):
    text = open(args.file, "r", encoding="utf-8").read()
    g = parse_grammar(text)
    t, steps = classify_grammar(g)
    print(f"Tipo detectado: {t}")
    for s in steps:
        print("-", s)
    if args.diagram:
        path = render_grammar(g, args.diagram)
        if path:
            print("Diagrama guardado en:", path)
        else:
            print("Instala 'graphviz' para generar diagramas.")
    if args.report:
        out = generate_report(args.report, "Reporte Chomsky Classifier AI", text, t, steps, args.diagram if args.diagram else None)
        print("Reporte PDF:", out)

def cmd_classify_automaton(args):
    text = open(args.file, "r", encoding="utf-8").read()
    a_type, obj = parse_automaton(text)
    t = classify_automaton_type(a_type)
    print(f"Automáta tipo {a_type} -> Lenguaje Tipo {t}")

def cmd_regex_convert(args):
    regex = args.regex
    nfa = nfa_from_regex(regex)
    dfa = dfa_from_nfa(nfa)
    start, prods = regular_grammar_from_dfa(dfa)
    print("Gramática regular equivalente:")
    # Agrupar por LHS
    by_lhs = {}
    for lhs, rhs in prods:
        by_lhs.setdefault(lhs, []).append(rhs)
    for lhs, rhss in by_lhs.items():
        print(lhs + " -> " + " | ".join(rhss))
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(f"# Gramática generada desde regex: {regex}\n")
            for lhs, rhss in by_lhs.items():
                f.write(lhs + " -> " + " | ".join(rhss) + "\n")
        print("Guardado en", args.out)

def build_parser():
    p = argparse.ArgumentParser(prog="chomsky-ai", description="Chomsky Classifier AI (CLI)")
    sub = p.add_subparsers()

    p1 = sub.add_parser("classify-grammar", help="Clasificar una gramática desde archivo .txt")
    p1.add_argument("file", help="Ruta al archivo con reglas")
    p1.add_argument("--diagram", help="Ruta base para guardar diagrama (sin extensión)", default=None)
    p1.add_argument("--report", help="Ruta del PDF a generar", default=None)
    p1.set_defaults(func=cmd_classify_grammar)

    p2 = sub.add_parser("classify-automaton", help="Clasificar autómata (JSON)")
    p2.add_argument("file")
    p2.set_defaults(func=cmd_classify_automaton)

    p3 = sub.add_parser("regex-to-grammar", help="Convertir regex a gramática regular")
    p3.add_argument("regex")
    p3.add_argument("--out", help="Guardar gramática en archivo", default=None)
    p3.set_defaults(func=cmd_regex_convert)

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
