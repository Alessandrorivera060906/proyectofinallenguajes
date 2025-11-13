from dataclasses import dataclass
from typing import Dict, Set, Tuple, List, Optional
from collections import defaultdict, deque

EPS = None  # epsilon interno

@dataclass
class NFA:
    start: int
    accepts: Set[int]
    trans: Dict[Tuple[int, Optional[str]], Set[int]]  # (state, symbol|None) -> set(states)

@dataclass
class DFA:
    start: int
    accepts: Set[int]
    trans: Dict[Tuple[int, str], int]
    alphabet: Set[str]

def _precedence(op: str) -> int:
    return {'*':3,'+':3,'?':3,'.':2,'|':1}.get(op, 0)

def _is_symbol(c: str) -> bool:
    return c not in {'|','*','+','?','(',')'}

def _to_postfix(regex: str) -> str:
    """Convierte regex (concatenación implícita) a postfijo con shunting-yard."""
    output: List[str] = []
    ops: List[str] = []
    prev: Optional[str] = None
    for c in regex:
        if c.isspace():
            continue
        if _is_symbol(c) or c == '(':
            if prev and (_is_symbol(prev) or prev in {')','*','+','?'}):
                while ops and _precedence(ops[-1]) >= _precedence('.'):
                    output.append(ops.pop())
                ops.append('.')
            if c == '(':
                ops.append(c)
            else:
                output.append(c)
        elif c == ')':
            while ops and ops[-1] != '(':
                output.append(ops.pop())
            if not ops:
                raise ValueError("Paréntesis desbalanceados")
            ops.pop()
        elif c in {'|','*','+','?'}:
            if c in {'*','+','?'}:
                output.append(c)
            else:
                while ops and _precedence(ops[-1]) >= _precedence(c):
                    output.append(ops.pop())
                ops.append(c)
        else:
            raise ValueError(f"Carácter inválido en regex: {c}")
        prev = c
    while ops:
        op = ops.pop()
        if op in {'(',')'}:
            raise ValueError("Paréntesis desbalanceados")
        output.append(op)
    return ''.join(output)

_counter = [0]
def _new_state() -> int:
    _counter[0] += 1
    return _counter[0]

def _nfa_single(c: str) -> NFA:
    s = _new_state(); f = _new_state()
    trans: Dict[Tuple[int, Optional[str]], Set[int]] = defaultdict(set)
    trans[(s, c)].add(f)
    return NFA(start=s, accepts={f}, trans=trans)

def _append_trans(dst: Dict[Tuple[int, Optional[str]], Set[int]], src: Dict[Tuple[int, Optional[str]], Set[int]]):
    for k, vs in src.items():
        for v in vs:
            dst[k].add(v)

def _thompson(postfix: str) -> NFA:
    stack: List[NFA] = []
    for token in postfix:
        if token not in {'|','.','*','+','?'}:
            stack.append(_nfa_single(token))
            continue
        if token == '.':
            n2 = stack.pop()
            n1 = stack.pop()
            trans = defaultdict(set)
            _append_trans(trans, n1.trans)
            _append_trans(trans, n2.trans)
            for a in n1.accepts:
                trans[(a, EPS)].add(n2.start)
            stack.append(NFA(start=n1.start, accepts=set(n2.accepts), trans=trans))
        elif token == '|':
            n2 = stack.pop()
            n1 = stack.pop()
            s = _new_state(); f = _new_state()
            trans = defaultdict(set)
            _append_trans(trans, n1.trans)
            _append_trans(trans, n2.trans)
            trans[(s, EPS)].update({n1.start, n2.start})
            for a in n1.accepts:
                trans[(a, EPS)].add(f)
            for a in n2.accepts:
                trans[(a, EPS)].add(f)
            stack.append(NFA(start=s, accepts={f}, trans=trans))
        elif token == '*':
            n1 = stack.pop()
            s = _new_state(); f = _new_state()
            trans = defaultdict(set)
            _append_trans(trans, n1.trans)
            trans[(s, EPS)].update({n1.start, f})
            for a in n1.accepts:
                trans[(a, EPS)].update({n1.start, f})
            stack.append(NFA(start=s, accepts={f}, trans=trans))
        elif token == '+':
            n1 = stack.pop()
            s = _new_state(); f = _new_state()
            trans = defaultdict(set)
            _append_trans(trans, n1.trans)
            trans[(s, EPS)].add(n1.start)
            for a in n1.accepts:
                trans[(a, EPS)].update({n1.start, f})
            stack.append(NFA(start=s, accepts={f}, trans=trans))
        elif token == '?':
            n1 = stack.pop()
            s = _new_state(); f = _new_state()
            trans = defaultdict(set)
            _append_trans(trans, n1.trans)
            trans[(s, EPS)].update({n1.start, f})
            for a in n1.accepts:
                trans[(a, EPS)].add(f)
            stack.append(NFA(start=s, accepts={f}, trans=trans))
    if not stack:
        raise ValueError("Expresión vacía")
    if len(stack) != 1:
        raise ValueError("Regex mal formada")
    return stack[0]

def _eps_closure(nfa: NFA, S: Set[int]) -> Set[int]:
    res = set(S)
    stack = list(S)
    while stack:
        q = stack.pop()
        for dst in nfa.trans.get((q, EPS), set()):
            if dst not in res:
                res.add(dst)
                stack.append(dst)
    return res

def _move(nfa: NFA, S: Set[int], sym: str) -> Set[int]:
    R = set()
    for q in S:
        for dst in nfa.trans.get((q, sym), set()):
            R.add(dst)
    return R

def nfa_from_regex(regex: str) -> NFA:
    pf = _to_postfix(regex)
    return _thompson(pf)

def dfa_from_nfa(nfa: NFA) -> DFA:
    alphabet = set(sym for (_, sym) in nfa.trans.keys() if sym is not EPS)
    start_set = frozenset(_eps_closure(nfa, {nfa.start}))
    idx = {start_set: 0}
    queue = deque([start_set])
    trans: Dict[Tuple[int, str], int] = {}
    accepts: Set[int] = set()
    while queue:
        S = queue.popleft()
        s_idx = idx[S]
        if any(q in nfa.accepts for q in S):
            accepts.add(s_idx)
        for a in alphabet:
            U = _eps_closure(nfa, _move(nfa, set(S), a))
            F = frozenset(U)
            if F not in idx:
                idx[F] = len(idx)
                queue.append(F)
            trans[(s_idx, a)] = idx[F]
    return DFA(start=0, accepts=accepts, trans=trans, alphabet=set(alphabet))

def regular_grammar_from_dfa(dfa: DFA):
    # Gramática lineal derecha A_i -> a A_j | ε
    states = set([dfa.start]) | set(s for (s,_) in dfa.trans.keys()) | set(dfa.trans.values()) | set(dfa.accepts)
    name = {s: f"A{s}" for s in states}
    start = name[dfa.start]
    prods = []
    for (s, a), t in dfa.trans.items():
        prods.append((name[s], f"{a}{name[t]}"))
    for q in dfa.accepts:
        prods.append((name[q], 'ε'))
    return start, prods
