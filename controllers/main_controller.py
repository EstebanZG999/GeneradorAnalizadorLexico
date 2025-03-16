# controllers/main_controller.py

from models.regex_parser import RegexParser
from models.syntax_tree import SyntaxTree
from models.dfa import DFA
from models.mindfa import minimize_dfa
from views.cli_view import (
    ask_for_regex,
    ask_for_num_strings,
    ask_for_string,
    show_dfa_info,
    show_simulation_result,
    show_message
)

def run_app():
    # 1) Solicitar regex al usuario
    user_regex = ask_for_regex()
    
    # 2) Parsear regex -> notación postfija
    parser = RegexParser(user_regex)
    postfix = parser.parse()

    # 3) Construir árbol sintáctico
    syntax_tree = SyntaxTree(postfix)

    # 4) Mostar árbol sintáctico
    syntax_tree.render("syntax_tree")

    # 4) Construir DFA usando algoritmo directo
    dfa = DFA(syntax_tree)

    # 5) Minimizar el DFA
    min_dfa = minimize_dfa(dfa)

    # 6) Mostrar DFA original por consola
    show_message("\n=== DFA original ===")
    show_dfa_info(dfa)

    # 7) Mostrar DFA mínimo por consola
    show_message("\n=== DFA mínimo ===")
    show_dfa_info(min_dfa)

    # 8) Graficar ambos 
    dfa.render_dfa("original_dfa")
    min_dfa.render_dfa("min_dfa")

    # 9) Pedir cadenas de prueba
    n = ask_for_num_strings()
    for i in range(n):
        s = ask_for_string(i)

        # Interpretamos '$' como la cadena vacía
        if s == "$":
            s = ""

        # Simular en el DFA 
        accepted = dfa.simulate(s)
        show_simulation_result(
            "$" if s == "" else s,
            accepted
        )

    show_message("Fin de la ejecución.")
