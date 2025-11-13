from typing import List, Tuple, Set, Dict

EPSILON = "ε"

def split_alternatives(rhs: str) -> List[str]:
    parts = []
    buff = []
    bal = 0
    for ch in rhs:
        if ch == '(':
            bal += 1
        elif ch == ')':
            bal -= 1
        if ch == '|' and bal == 0:
            parts.append(''.join(buff).strip())
            buff = []
        else:
            buff.append(ch)
    if buff:
        parts.append(''.join(buff).strip())
    return parts

def is_nonterminal(sym: str) -> bool:
    if not sym:
        return False
    if sym.startswith('<') and sym.endswith('>'):
        return True
    return sym.isalpha() and sym[0].isupper()

def tokenize_rhs(rhs: str) -> List[str]:
    tokens = []
    i = 0
    while i < len(rhs):
        ch = rhs[i]
        if ch.isspace():
            i += 1; continue
        if ch == 'ε':
            tokens.append('ε'); i += 1; continue
        if ch == '<':
            j = rhs.find('>', i+1)
            if j == -1:
                tokens.append(rhs[i]); i += 1
            else:
                tokens.append(rhs[i:j+1]); i = j+1
            continue
        if ch.isalpha():
            tokens.append(ch); i += 1; continue
        tokens.append(ch); i += 1
    expanded = []
    for t in tokens:
        if len(t) == 1 and t.isalpha() and t.isupper():
            expanded.append(t)
        elif len(t) == 1 and t.isalpha() and t.islower():
            expanded.append(t)
        elif t.startswith('<') and t.endswith('>'):
            expanded.append(t)
        elif t == 'ε':
            expanded.append(t)
        else:
            for c in t: expanded.append(c)
    return expanded

def deduce_symbols(productions: List[Tuple[str, str]]) -> Tuple[Set[str], Set[str]]:
    NT: Set[str] = set(); T: Set[str] = set()
    for lhs, rhs in productions:
        for s in lhs.split():
            if is_nonterminal(s) or (len(s) == 1 and s.isupper()):
                NT.add(s)
        for alt in split_alternatives(rhs):
            toks = tokenize_rhs(alt)
            for t in toks:
                if t == 'ε': continue
                if is_nonterminal(t) or (len(t) == 1 and t.isupper()):
                    NT.add(t)
                else:
                    T.add(t)
    return NT, T

def normalize_arrow(line: str) -> str:
    return line.replace("→", "->").replace("⇒", "->").replace(":=", "->")

def strip_comments(text: str) -> str:
    lines = []
    for ln in text.splitlines():
        idx = ln.find("#"); idx2 = ln.find("//"); cut = len(ln)
        if idx != -1: cut = min(cut, idx)
        if idx2 != -1: cut = min(cut, idx2)
        lines.append(ln[:cut])
    return "\n".join(lines)
