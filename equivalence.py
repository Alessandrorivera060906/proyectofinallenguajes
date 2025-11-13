from typing import Set, List, Tuple
from collections import deque
from .grammar_parser import Grammar

def derive_strings(g: Grammar, max_len: int = 5, max_steps: int = 2000) -> Set[str]:
    """Heurística: deriva cadenas hasta longitud max_len (BFS)."""
    derived: Set[str] = set()
    queue = deque()
    queue.append([g.start])
    steps = 0
    while queue and steps < max_steps:
        sentential = queue.popleft()
        steps += 1
        if all((tok.islower() or not tok.isalpha()) for tok in sentential):
            s = ''.join(tok for tok in sentential if tok != 'ε')
            if len(s) <= max_len:
                derived.add(s)
            continue
        for i, tok in enumerate(sentential):
            if tok.isupper() or (tok.startswith('<') and tok.endswith('>')):
                lhs = tok
                for p_lhs, rhs in g.productions:
                    if p_lhs.split()[0] == lhs:
                        for alt in rhs.split('|'):
                            alt_toks = [t for t in alt.strip() if t]
                            new_sent = sentential[:i] + alt_toks + sentential[i+1:]
                            if len(''.join([x for x in new_sent if x != 'ε'])) <= max_len:
                                queue.append(new_sent)
                break
    return derived

def are_grammars_equivalent(g1: Grammar, g2: Grammar, max_len: int = 5):
    s1 = derive_strings(g1, max_len)
    s2 = derive_strings(g2, max_len)
    return s1 == s2, s1 - s2, s2 - s1
