from dataclasses import dataclass
from typing import List, Tuple, Set
from .utils import split_alternatives, normalize_arrow, deduce_symbols, strip_comments, EPSILON, tokenize_rhs, is_nonterminal

@dataclass
class Grammar:
    start: str
    productions: List[Tuple[str, str]]  # (lhs, rhs) con posibles alternativas separadas por |

    @property
    def nonterminals(self) -> Set[str]:
        NT, _ = deduce_symbols(self.productions)
        return NT

    @property
    def terminals(self) -> Set[str]:
        _, T = deduce_symbols(self.productions)
        return T

def parse_grammar(text: str) -> Grammar:
    """Parsea reglas tipo:
    S -> aA | b
    A -> bA | b | ε
    """
    clean = strip_comments(text).strip()
    if not clean:
        raise ValueError("Empty grammar text")
    prods: List[Tuple[str, str]] = []
    start_symbol = None
    for line in clean.splitlines():
        line = line.strip()
        if not line:
            continue
        line = normalize_arrow(line)
        if "->" not in line:
            raise ValueError(f"Bad production (no ->): {line}")
        lhs, rhs = [p.strip() for p in line.split("->", 1)]
        if start_symbol is None:
            start_symbol = lhs.split()[0]
        prods.append((lhs, rhs))
    if start_symbol is None:
        raise ValueError("No productions found")
    return Grammar(start=start_symbol, productions=prods)

def productions_expanded(g: Grammar) -> List[Tuple[str, List[str]]]:
    out = []
    for lhs, rhs in g.productions:
        alts = split_alternatives(rhs)
        out.append((lhs, alts))
    return out

def rhs_tokens(rhs: str) -> List[str]:
    return tokenize_rhs(rhs)

def occurs_on_rhs(g: Grammar, sym: str) -> bool:
    for _, rhs in g.productions:
        for alt in split_alternatives(rhs):
            if sym in rhs_tokens(alt):
                return True
    return False
