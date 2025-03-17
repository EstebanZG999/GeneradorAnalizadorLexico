# controllers/main_controller.py

from models.regex_parser import RegexParser
from models.syntax_tree import SyntaxTree
from models.dfa import DFA
from models.yalex_parser import YALexParser
from models.mindfa import minimize_dfa
from views.cli_view import (
    ask_for_regex,
    ask_for_num_strings,
    ask_for_string,
    show_dfa_info,
    show_simulation_result,
    show_message
)


def test_yalex_parser(input_file):
    # Instancia el parser con el archivo .yal
    parser = YALexParser(input_file)
    # Llama al método parse() para extraer header, definiciones, reglas y trailer
    parser.parse()

    # Imprime los resultados para verificar la extracción
    print("=== Header ===")
    print(parser.header_code)
    print("\n=== Definiciones ===")
    for ident, regex in parser.definitions.items():
        print(f"{ident} = {regex}")
    print("\n=== Regla y Acciones ===")
    print(f"Entrypoint: {parser.entrypoint}")
    for i, (regex, action) in enumerate(parser.rules, start=1):
        # Expande las definiciones para ver la expresión regular completa
        expanded_regex = parser.expand_definitions(regex)
        print(f"Regla {i}:")
        print(f"  Regex original: {regex}")
        print(f"  Regex expandida: {expanded_regex}")
        print(f"  Acción: {action}")
    print("\n=== Trailer ===")
    print(parser.trailer_code)

if __name__ == "__main__":
    # Ruta relativa al archivo de entrada (por ejemplo, "inputs/example.yal")
    input_file = "inputs/example.yal"
    test_yalex_parser(input_file)


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
