# controllers/main_controller.py

import os
import textwrap
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

def extend_dfa_with_match_prefix():
    """
    Agrega a la clase DFA el método match_prefix, que recorre el input
    carácter a carácter y retorna la longitud del mayor prefijo aceptado.
    """
    def match_prefix(self, input_str):
        current_state = self.initial_state
        last_accept_pos = -1
        pos = 0
        for ch in input_str:
            if ch in self.transitions.get(current_state, {}):
                current_state = self.transitions[current_state][ch]
                pos += 1
                if current_state in self.accepting_states:
                    last_accept_pos = pos
            else:
                break
        if last_accept_pos != -1:
            return last_accept_pos
        return 0
    setattr(DFA, "match_prefix", match_prefix)

def test_full_pipeline(input_file):
    """
    Función para procesar un archivo YALex y mostrar, para cada regla,
    el procesamiento: desde la expresión regular original hasta el DFA generado.
    """
    # Instanciar y parsear el archivo YALex
    parser = YALexParser(input_file)
    parser.parse()

    # Para cada regla extraída
    for idx, (regex_str, action_code) in enumerate(parser.rules, start=1):
        print(f"\n=== Procesando Regla {idx} ===")
        print("Regex original:", regex_str)
        
        # Limpieza: elimina '|' y espacios iniciales
        regex_str_clean = regex_str.lstrip("| ").strip()
        print("Regex limpia:", regex_str_clean)
        
        # Si está vacía, la saltamos
        if not regex_str_clean:
            print("Regla vacía. Se omite.")
            continue

        # Expandir definiciones
        expanded_regex = parser.expand_definitions(regex_str_clean)
        print("Regex expandida:", expanded_regex)
        
        # Convertir a notación postfix
        r_parser = RegexParser(expanded_regex)
        postfix = r_parser.parse()
        print("Postfix:", [str(token) for token in postfix])
        
        # Construir el árbol de sintaxis
        syntax_tree = SyntaxTree(postfix)
        # (Opcional: puedes graficar el árbol)
        # syntax_tree.render(f"imagenes/syntax_tree/tree_regla_{idx}")
        
        # Generar el DFA
        dfa = DFA(syntax_tree)
        print("Estados del DFA:")
        for state_set, state_id in dfa.states.items():
            print(f"  Estado {state_id}: {set(state_set)}")
        print("Transiciones:")
        for state_id, trans in dfa.transitions.items():
            for symbol, target in trans.items():
                print(f"  δ({state_id}, '{symbol}') = {target}")
        
        print("Acción asociada:", action_code)

def run_app():
    """
    Función interactiva para probar una expresión regular:
      - Solicita una regex
      - Procesa la entrada (conversión a postfix, árbol, DFA y DFA minimizado)
      - Muestra por consola y genera imágenes de los autómatas
      - Permite ingresar cadenas de prueba para simular el DFA
    """
    # 1) Solicitar regex al usuario
    user_regex = ask_for_regex()
    
    # 2) Parsear regex -> notación postfija
    parser = RegexParser(user_regex)
    postfix = parser.parse()

    # 3) Construir árbol sintáctico
    syntax_tree = SyntaxTree(postfix)

    # 4) Mostrar árbol sintáctico
    syntax_tree.render("syntax_tree")

    # 5) Construir DFA usando algoritmo directo
    dfa = DFA(syntax_tree)

    # 6) Minimizar el DFA
    min_dfa = minimize_dfa(dfa)

    # 7) Mostrar DFA original por consola
    show_message("\n=== DFA original ===")
    show_dfa_info(dfa)

    # 8) Mostrar DFA mínimo por consola
    show_message("\n=== DFA mínimo ===")
    show_dfa_info(min_dfa)

    # 9) Graficar ambos autómatas
    dfa.render_dfa("original_dfa")
    min_dfa.render_dfa("min_dfa")

    # 10) Pedir cadenas de prueba
    n = ask_for_num_strings()
    for i in range(n):
        s = ask_for_string(i)
        # Interpretamos '$' como la cadena vacía
        if s == "$":
            s = ""
        accepted = dfa.simulate(s)
        show_simulation_result("$" if s == "" else s, accepted)

    show_message("Fin de la ejecución.")

def generate_lexer():
    """
    Genera el archivo 'thelexer.py' a partir de la especificación YALex.
    Combina el header, la generación de DFAs para cada regla con su acción asociada y el trailer.
    """
    spec_filename = "inputs/lexer.yal"
    yalex_parser = YALexParser(spec_filename)
    yalex_parser.parse()
    print("Header extraído:")
    print(yalex_parser.header_code)
    print("\nDefiniciones encontradas:")
    for ident, definition in yalex_parser.definitions.items():
        print(f"  {ident} = {definition}")
    print("\nReglas encontradas:")
    
    rules = []
    for idx, (regex_str, action_code) in enumerate(yalex_parser.rules):
        # Limpieza de la regex: eliminar '|' inicial y espacios
        regex_str_clean = regex_str.lstrip("| ").strip()
        if not regex_str_clean:
            continue
        expanded_regex = yalex_parser.expand_definitions(regex_str_clean)
        added_marker = False
        # Si no se encuentra el marcador terminal, se agrega de forma implícita.
        if '#' not in expanded_regex:
            expanded_regex = expanded_regex + '#'
            added_marker = True
        print(f"Regla {idx+1} expandida: {expanded_regex}")
        # Construir el DFA para la regla
        r_parser = RegexParser(expanded_regex)
        r_parser.tokenize()
        postfix = r_parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        # (Opcional: generar imágenes para verificar)
        syntax_tree.render(f"syntax_tree_rule_{idx+1}")
        dfa.render_dfa(f"dfa_rule_{idx+1}")
        rules.append({
            'regex': expanded_regex,
            'action': action_code,
            'dfa': dfa,
            'order': idx,
            'added_marker': added_marker
        })
    
    output_filename = "thelexer.py"
    with open(output_filename, "w", encoding="utf-8") as f:
        # Escribir header (el código extraído del archivo YALex)
        f.write("# Código generado automáticamente por YALex\n")
        # header = "\n".join(line.lstrip() for line in yalex_parser.header_code.splitlines())
        # f.write(header + "\n\n")

        # Definir la clase Lexer
        f.write("class Lexer:\n")
        f.write("    def __init__(self, input_text):\n")
        f.write("        self.input_text = input_text\n")
        f.write("        self.pos = 0\n")
        f.write("\n")
        f.write("    def get_tokens(self):\n")
        f.write("        tokens = []\n")
        f.write("        text = self.input_text\n")
        f.write("        pos = 0\n")
        f.write("        while pos < len(text):\n")
        f.write("            longest_match = 0\n")
        f.write("            selected_rule = None\n")
        f.write("            for rule in self.rules:\n")
        f.write("                match_length = rule['dfa'].match_prefix(text[pos:])\n")
        f.write("                if match_length > longest_match:\n")
        f.write("                    longest_match = match_length\n")
        f.write("                    selected_rule = rule\n")
        f.write("            if longest_match == 0:\n")
        f.write("                print(f'Error léxico en posición {pos}: símbolo no reconocido: {text[pos]}')\n")
        f.write("                pos += 1\n")
        f.write("            else:\n")
        f.write("                lexeme = text[pos:pos+longest_match]\n")
        # Si el lexema termina en '#' (marcador agregado), se quita esa última posición
        f.write("                if lexeme.endswith('#'):\n")
        f.write("                    lexeme = lexeme[:-1]\n")
        f.write("                local_env = {'lexeme': lexeme, 'text': text}\n")
        f.write("                action_code = selected_rule['action'].replace('return', 'token =')\n")
        f.write("                exec(action_code, {}, local_env)\n")
        f.write("                token = local_env.get('token', lexeme)\n")
        f.write("                tokens.append(token)\n")
        f.write("                pos += longest_match\n")
        f.write("        return tokens\n")
        f.write("\n")
        # Propiedad rules que reconstruye las reglas al momento de usar el lexer
        f.write("    @property\n")
        f.write("    def rules(self):\n")
        f.write("        rules = []\n")
        # Para cada regla, se genera el código que recrea el DFA (con la misma expresión expandida)
        for rule in rules:
            f.write("        from models.regex_parser import RegexParser\n")
            f.write("        from models.syntax_tree import SyntaxTree\n")
            f.write("        from models.dfa import DFA\n")
            f.write(f"        # Regla: {rule['regex']}\n")
            f.write(f"        parser = RegexParser(r'''{rule['regex']}''')\n")
            f.write("        parser.tokenize()\n")
            f.write("        postfix = parser.to_postfix()\n")
            f.write("        syntax_tree = SyntaxTree(postfix)\n")
            f.write("        dfa = DFA(syntax_tree)\n")
            f.write(f"        rules.append({{'regex': r'''{rule['regex']}''', 'action': r'''{rule['action']}''', 'dfa': dfa}})\n")
        f.write("        return rules\n")
        f.write("\n")
        
        # Escribir trailer (el código extraído del archivo YALex, si existe)
        # trailer = "\n".join(line.lstrip() for line in yalex_parser.trailer_code.splitlines())
        # f.write(trailer + "\n")
    
    print(f"\nAnalizador léxico generado y guardado en: {output_filename}")

if __name__ == "__main__":
    extend_dfa_with_match_prefix()
    # test_full_pipeline("inputs/lexer.yal")
    
    # Ejecutar la generación del archivo final del analizador léxico
    generate_lexer()
    
    # run_app()