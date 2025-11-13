from typing import List, Tuple
from .grammar_parser import Grammar, productions_expanded, rhs_tokens, occurs_on_rhs
from .utils import EPSILON, is_nonterminal

def _is_regular_rule(lhs: str, alt: str) -> Tuple[bool, str]:
    toks = rhs_tokens(alt)
    if toks == [EPSILON] or alt == "":
        return True, "Permite ε en gramática regular (si no introduce ambigüedad)."
    if len(toks) == 1 and not is_nonterminal(toks[0]):
        return True, "A -> a"
    if len(toks) == 2 and (not is_nonterminal(toks[0])) and is_nonterminal(toks[1]):
        return True, "A -> aB"
    return False, f"No es de la forma regular (A -> aB | a). RHS='{alt}'"

def classify_grammar(g: Grammar) -> Tuple[int, List[str]]:
    steps: List[str] = []
    expanded = productions_expanded(g)

    # CFG (tipo 2): LHS un único no terminal
    is_cfg = True
    for lhs, alts in expanded:
        lhs_syms = lhs.split()
        if not (len(lhs_syms) == 1 and is_nonterminal(lhs_syms[0])):
            is_cfg = False
            steps.append(f"Violación CFG: LHS '{lhs}' no es un único no terminal.")
            break

    # Regular (tipo 3)
    is_regular = is_cfg
    if is_cfg:
        for lhs, alts in expanded:
            for alt in alts:
                ok, why = _is_regular_rule(lhs, alt.strip())
                if not ok:
                    is_regular = False
                    steps.append(f"Violación Regular: {why} en {lhs} -> {alt}")
                    break
            if not is_regular:
                break
        if is_regular:
            steps.append("Todas las producciones cumplen A -> aB | a | ε.")
            return 3, steps

    if is_cfg:
        steps.append("Todas las producciones tienen un único no terminal en el LHS (CFG).")
        return 2, steps

    # CSG (tipo 1)
    is_csg = True
    s_in_rhs = occurs_on_rhs(g, g.start)
    for lhs, alts in expanded:
        for alt in alts:
            lhs_len = len(lhs.split())
            rhs_len = len(rhs_tokens(alt))
            if rhs_len == 1 and alt.strip() == EPSILON:
                if lhs != g.start or s_in_rhs:
                    is_csg = False
                    steps.append("Violación CSG: Producción vacía no permitida salvo S->ε y S no en RHS.")
                    break
            if lhs_len > rhs_len:
                is_csg = False
                steps.append(f"Violación CSG: |{lhs}|={lhs_len} > |{alt}|={rhs_len}.")
                break
        if not is_csg: break

    if is_csg:
        steps.append("Todas las producciones cumplen |α| ≤ |β| y no hay ε indebido.")
        return 1, steps

    steps.append("No cumple restricciones de tipos 3, 2 ni 1.")
    return 0, steps
