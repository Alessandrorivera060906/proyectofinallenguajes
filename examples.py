from .grammar_parser import parse_grammar

def regular_example():
    text = "S -> aA | b\nA -> aS | b\n"
    return parse_grammar(text)

def cfg_example():
    text = "S -> aSb | ab\n"
    return parse_grammar(text)

def csg_example():
    text = "aS b -> a aS b | a b\n"
    return parse_grammar(text)

def type0_example():
    text = "AB -> BA\nS -> aA\n"
    return parse_grammar(text)
