# Conversión regex -> gramática regular (lineal derecha)
# Soporta: |  ( )  *  y concatenación implícita. Los símbolos terminales son caracteres alfanuméricos.
from typing import Dict, Set, List, Tuple

def _is_symbol(ch: str) -> bool:
    return ch.isalnum()  # letras y dígitos como terminales

def _add_concat(regex: str) -> str:
    """Inserta operador explícito de concatenación '.' cuando corresponde."""
    out = []
    for i, ch in enumerate(regex):
        out.append(ch)
        if i + 1 >= len(regex):
            continue
        a = ch
        b = regex[i + 1]
        if (a == ')' or _is_symbol(a) or a == '*') and (_is_symbol(b) or b == '('):
            out.append('.')
    return ''.join(out)

def _to_postfix(regex: str) -> str:
    prec = {'*': 3, '.': 2, '|': 1}
    out = []
    stack: List[str] = []
    for ch in _add_concat(regex):
        if _is_symbol(ch):
            out.append(ch)
        elif ch == '(':
            stack.append(ch)
        elif ch == ')':
            while stack and stack[-1] != '(':
                out.append(stack.pop())
            if stack and stack[-1] == '(':
                stack.pop()
        elif ch in prec:
            if ch == '*':
                # cierre de Kleene es posfijo
                while stack and prec.get(stack[-1], 0) > prec[ch]:
                    out.append(stack.pop())
                out.append(ch)
            else:
                while stack and stack[-1] != '(' and prec.get(stack[-1], 0) >= prec[ch]:
                    out.append(stack.pop())
                stack.append(ch)
    while stack:
        out.append(stack.pop())
    return ''.join(out)

# NFA vía Thompson
class _NFA:
    def __init__(self):
        self.next_id = 0
        self.start = self._new()
        self.accept = self._new()
        self.trans: Dict[Tuple[int, str], Set[int]] = {}

    def _new(self) -> int:
        i = self.next_id
        self.next_id += 1
        return i

def _thompson_from_postfix(post: str) -> Tuple[int, int, Dict[Tuple[int, str], Set[int]]]:
    def new_state() -> int:
        nonlocal nid
        i = nid
        nid += 1
        return i

    nid = 0
    stack = []
    trans: Dict[Tuple[int, str], Set[int]] = {}

    def add_edge(u: int, sym: str, v: int):
        trans.setdefault((u, sym), set()).add(v)

    for ch in post:
        if _is_symbol(ch):
            s = new_state(); t = new_state()
            add_edge(s, ch, t)
            stack.append((s, t))
        elif ch == '.':  # concat
            s2, t2 = stack.pop()
            s1, t1 = stack.pop()
            add_edge(t1, 'ε', s2)
            stack.append((s1, t2))
        elif ch == '|':  # unión
            s2, t2 = stack.pop()
            s1, t1 = stack.pop()
            s = new_state(); t = new_state()
            add_edge(s, 'ε', s1); add_edge(s, 'ε', s2)
            add_edge(t1, 'ε', t); add_edge(t2, 'ε', t)
            stack.append((s, t))
        elif ch == '*':  # Kleene
            s1, t1 = stack.pop()
            s = new_state(); t = new_state()
            add_edge(s, 'ε', s1); add_edge(s, 'ε', t)
            add_edge(t1, 'ε', s1); add_edge(t1, 'ε', t)
            stack.append((s, t))
        else:
            raise ValueError(f"Símbolo de regex no soportado: {ch}")
    assert len(stack) == 1, "Regex inválida"
    return (*stack[0], trans)

def _nfa_to_right_linear_grammar(s: int, t: int, trans: Dict[Tuple[int, str], Set[int]]) -> str:
    # No terminal para cada estado: A0, A1, ...
    states = set([s, t])
    for (u, _), dests in list(trans.items()):
        states.add(u); states |= dests
    mapping = {st: f"A{idx}" for idx, st in enumerate(sorted(states))}

    lines: List[str] = []
    # Producciones por transiciones
    for (u, sym), dests in trans.items():
        for v in dests:
            if sym == 'ε':
                # ε transición -> producción epsilon
                lines.append(f"{mapping[u]} -> ε")
            else:
                lines.append(f"{mapping[u]} -> {sym}{mapping[v]}")
    # Estado de aceptación produce ε
    lines.append(f"{mapping[t]} -> ε")
    # start es el del estado s (primera producción la ponemos arriba)
    lines.sort()
    start = mapping[s]
    return "\n".join([f"{start} -> {start.split('->')[0]}"][:0] + lines)

def regex_to_grammar(regex: str) -> str:
    post = _to_postfix(regex)
    s, t, trans = _thompson_from_postfix(post)
    return _nfa_to_right_linear_grammar(s, t, trans)
