from typing import List, Tuple, Optional
try:
    from graphviz import Digraph
except Exception:
    Digraph = None

from .grammar_parser import Grammar, productions_expanded, rhs_tokens
from .automata_parser import DFA as DFAStruct

def render_grammar(g: Grammar, path: str) -> Optional[str]:
    if Digraph is None:
        return None
    dot = Digraph(comment="Grammar", format="png")
    dot.attr(rankdir='LR')
    for nt in g.nonterminals:
        dot.node(nt, shape="circle")
    for lhs, alts in productions_expanded(g):
        for alt in alts:
            toks = rhs_tokens(alt)
            if len(toks) == 1 and toks[0] == 'ε':
                dot.node(f"{lhs}_end", label="ε", shape="doublecircle")
                dot.edge(lhs, f"{lhs}_end", label="ε")
            elif len(toks) == 1:
                dot.edge(lhs, lhs, label=toks[0])
            elif len(toks) == 2:
                dot.edge(lhs, toks[1], label=toks[0])
            else:
                dot.edge(lhs, lhs, label=''.join(toks))
    outfile = dot.render(path, cleanup=True)
    return outfile

def render_dfa(dfa: DFAStruct, path: str) -> Optional[str]:
    if Digraph is None:
        return None
    dot = Digraph(comment="DFA", format="png")
    dot.attr(rankdir='LR')
    for s in dfa.states:
        shape = "doublecircle" if s in dfa.accepts else "circle"
        dot.node(s, shape=shape)
    dot.node("start", shape="point")
    dot.edge("start", dfa.start)
    for (s, a), t in dfa.transitions.items():
        dot.edge(s, t, label=a)
    outfile = dot.render(path, cleanup=True)
    return outfile
