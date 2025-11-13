import json
from dataclasses import dataclass
from typing import Dict, Set, Tuple, List, Optional

@dataclass
class DFA:
    states: Set[str]
    alphabet: Set[str]
    start: str
    accepts: Set[str]
    transitions: Dict[Tuple[str, str], str]

def parse_automaton(text: str):
    """Parsea JSON de autómata. 'type' ∈ {'DFA','NFA','PDA','TM','LBA'}."""
    data = json.loads(text)
    a_type = data.get("type","").upper()
    if a_type == "DFA":
        states = set(data["states"])
        alphabet = set(data["alphabet"])
        start = data["start"]
        accepts = set(data["accepts"])
        trans = {}
        for s, edges in data["transitions"].items():
            for sym, dst in edges.items():
                trans[(s, sym)] = dst
        return ("DFA", DFA(states, alphabet, start, accepts, trans))
    # Para otros tipos, devolvemos solo el tipo
    return (a_type, data)

def classify_automaton_type(a_type: str) -> int:
    """Mapea el tipo de autómata a la jerarquía de Chomsky."""
    a_type = a_type.upper()
    if a_type in ("DFA", "NFA", "REGEX"):
        return 3
    if a_type in ("PDA", "AP"):
        return 2
    if a_type in ("LBA",):
        return 1
    if a_type in ("TM","TURING","MT"):
        return 0
    return 0
