import random
from .examples import regular_example, cfg_example, csg_example, type0_example
from .classifier import classify_grammar

def random_quiz():
    makers = [("Tipo 3 (Regular)", regular_example), ("Tipo 2 (GLC)", cfg_example), ("Tipo 1 (CSG)", csg_example), ("Tipo 0 (RE)", type0_example)]
    name, maker = random.choice(makers)
    g = maker()
    t, _ = classify_grammar(g)
    return g, t, name
