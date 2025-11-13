from dataclasses import dataclass
from typing import Any, Tuple
import json

@dataclass
class Automaton:
    type: str
    raw: Any

def load_automaton_json(path: str) -> Automaton:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    t = str(data.get("type", "")).strip().upper()
    # Sinónimos tolerados
    synonyms = {
        "FINITE": "DFA",
        "FINITE_AUTOMATON": "DFA",
        "TURING": "TM",
        "TURINGMACHINE": "TM",
        "LINEARBOUNDED": "LBA",
        "LINEAR_BOUNDED_AUTOMATON": "LBA",
    }
    t = synonyms.get(t, t)
    return Automaton(type=t, raw=data)

def classify_automaton(a: Automaton) -> Tuple[str, int]:
    """
    Mapea tipo de autómata -> tipo de lenguaje (jerarquía de Chomsky)
    DFA/NFA -> 3, PDA -> 2, LBA -> 1, TM -> 0
    """
    if a.type in {"DFA", "NFA"}:
        return a.type, 3
    if a.type == "PDA":
        return a.type, 2
    if a.type == "LBA":
        return a.type, 1
    if a.type == "TM":
        return a.type, 0
    return (a.type or "UNKNOWN", 0)
