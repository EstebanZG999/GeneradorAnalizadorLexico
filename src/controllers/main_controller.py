# src/controllers/main_controller.py

import os
import re
import contextlib, io
import textwrap
from src.models.regex_parser import RegexParser
from src.models.syntax_tree import SyntaxTree
from src.models.dfa import DFA
from src.models.yalex_parser import YALexParser
from src.models.mindfa import minimize_dfa
from src.runtime.views.cli_view import (
    ask_for_regex,
    ask_for_num_strings,
    ask_for_string,
    show_dfa_info,
    show_simulation_result,
    show_message
)


def generate_global_dfa():
    """
    Genera un DFA global a partir de la especificación en 'inputs/lexer.yal',
    asignando un marcador único a cada regla y combinándolas en una única expresión regular.
    """
    spec_filename = "inputs/lexer.yal"
    yalex_parser = YALexParser(spec_filename)
    yalex_parser.parse()
    
    global_rules = []
    marker_to_rule = {}
    
    for i, (regex_str, action_code) in enumerate(yalex_parser.rules):
        # Limpieza de la regex: remover '|' inicial y espacios
        regex_clean = regex_str.lstrip("| ").strip()
        if not regex_clean:
            continue
        
        # Expandir definiciones
        expanded_regex = yalex_parser.expand_definitions(regex_clean)
        # Elimina saltos de línea y espacios extra de la expresión expandida
        expanded_regex = expanded_regex.replace("\n", "").strip()
        # Remover el marcador terminal '#' si existe
        if expanded_regex.endswith('#'):
            expanded_regex = expanded_regex[:-1]
        
        # Asignar un marcador único para esta regla
        marker = chr(128 + i)
        marker_to_rule[marker] = {'order': i, 'action': action_code}
        
        # Concatena el marcador único al final de la expresión
        token_regex = f"{expanded_regex}{marker}"
        # Asegurarse de limpiar la cadena final
        token_regex = token_regex.replace("\n", "").strip()
        global_rules.append(token_regex)

    
    # Combina todas las expresiones en una única expresión global con alternancia
    global_regex = "|".join(f"({r})" for r in global_rules)
    print("Expresión global generada:", global_regex)
    
    
    # Remueve cualquier salto de línea que pueda quedar en la expresión global —> Comentado para no romper literales \n, \t dentro de []
    # global_regex = global_regex.replace("\n", "").replace("\r", "").strip()
    print("Expresión global generada (repr):", repr(global_regex))
    
    # Procesar la expresión global: tokenizar, convertir a postfix, construir árbol y DFA
    r_parser = RegexParser(global_regex)
    r_parser.tokenize()
    postfix = r_parser.to_postfix()
    syntax_tree = SyntaxTree(postfix)
    global_dfa = DFA(syntax_tree)
    
    # Asigna el mapeo de marcadores al DFA
    global_dfa.marker_to_rule = marker_to_rule
    # Crea una estructura para mapear cada ID de estado a su conjunto de posiciones
    global_dfa.state_sets = {state_id: state_set for state_set, state_id in global_dfa.states.items()}
    
    # Genera la imagen del DFA global en la carpeta 'imagenes' con Graphviz
    global_dfa.render_dfa("global_dfa")
    
    return global_dfa


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
    # print("\nReglas encontradas:")
    
    rules = []
    for idx, (regex_str, action_code) in enumerate(yalex_parser.rules, start=1):
        # Limpieza de la regex: eliminar '|' inicial y espacios
        regex_str_clean = regex_str.lstrip("| ").strip()
        if not regex_str_clean:
            continue
        # 1) Expandir definiciones
        expanded_regex = yalex_parser.expand_definitions(regex_str_clean)
        # 2) Si la regla es exactamente un literal entre comillas,
        #    tratamos el salto de línea '\n' como un escape especial
        if (expanded_regex.startswith("'") and expanded_regex.endswith("'")) \
        or (expanded_regex.startswith('"') and expanded_regex.endswith('"')):
            lit = expanded_regex[1:-1]
            if lit == r"\n":
                # queremos un único backslash-n para que el parser lo convierta a '\n'
                escaped = r"\n"
            else:
                escaped = re.escape(lit)
            expanded_regex = escaped
        else:
            # Para literales incrustados, escapamos cada uno
            expanded_regex = re.sub(
                r'"([^"]*)"',
                lambda m: re.escape(m.group(1)),
                expanded_regex
            )
            expanded_regex = re.sub(
                r"'([^']*)'",
                lambda m: re.escape(m.group(1)),
                expanded_regex
            )
        # 3) Quitar saltos de línea (sin tocar espacios)
        expanded_regex = expanded_regex.replace("\n", "")
        # 4) Añadir centinela '#' al final
        expanded_regex_for_tree = expanded_regex + '#'
        '''
        # ——— DEPURACIÓN ———
        print(f"[DEBUG] Regla {idx}: expresión a tokenizar → {expanded_regex_for_tree!r}")
        r_parser = RegexParser(expanded_regex_for_tree)
        try:
            r_parser.tokenize()
        except ValueError as e:
            print(f"¡Error parseando la expresión expandida en la regla {idx}!")
            print(f"   expanded_regex_for_tree = {expanded_regex_for_tree!r}")
            # Re-lanzamos el mismo error para que se vea el stack trace
            raise
        # ——— fin depuración ———
        '''
        added_marker = False
        with contextlib.redirect_stdout(io.StringIO()):
            print(f"Regla {idx+1} expandida: {expanded_regex}")
        # Construir el DFA para la regla
        r_parser = RegexParser(expanded_regex_for_tree)
        r_parser.tokenize()
        postfix = r_parser.to_postfix()
        # (Debug opcional, envuelto en --verbose)
        """
        print(f"\n--- DEBUG Regla {idx+1} ---")
        print(" regex raw:     ", repr(expanded_regex))
        print(" tokens:        ", [str(t) for t in r_parser.tokens])
        print(" postfix:       ", [str(t) for t in postfix])
        """
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        with contextlib.redirect_stdout(io.StringIO()):
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
        f.write("import re\n")
        header = "\n".join(line.lstrip() for line in yalex_parser.header_code.splitlines())
        if header:
            f.write(header + "\n\n")

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
        # ——— Reconocimiento rápido de números científicos ———
        f.write("            m = re.match(r'\\d+\\.\\d+(?:[eE][+-]?\\d+)?', text[pos:])\n")
        f.write("            if m:\n")
        f.write("                lexeme = m.group(0)\n")
        f.write("                tokens.append((NUMBER, lexeme))\n")
        f.write("                print(f'⟶ Token: {NUMBER!r}, lexema: {lexeme!r}')\n")
        f.write("                pos += len(lexeme)\n")
        f.write("                continue\n")
        # 1) Intentar, por cada regla, empatar el mayor prefijo
        f.write("            longest_match = 0\n")
        f.write("            selected_rule = None\n")
        f.write("            for rule in self.rules:\n")
        f.write("                ml = rule['dfa'].match_prefix(text[pos:])\n")
        f.write("                if ml > longest_match:\n")
        f.write("                    longest_match = ml\n")
        f.write("                    selected_rule = rule\n")
        f.write("            if longest_match > 1:\n")
        f.write("                lexeme = text[pos:pos+longest_match]\n")
        f.write("                action_code = selected_rule['action']\n")
        f.write("                local_env = {'lexeme': lexeme, 'text': text}\n")
        f.write("                exec(action_code.replace('return', 'token ='), globals(), local_env)\n")
        f.write("                tok = local_env.get('token')\n")
        f.write("                if tok is not None:\n")
        f.write("                    tokens.append((tok, lexeme))\n")
        f.write("                    print(f'⟶ Token: {tok!r}, lexema: {lexeme!r}')\n")
        f.write("                pos += longest_match\n")
        f.write("                continue\n")
        # 2) Si no fue un token largo, símbolos puntuales
        f.write("            ch = text[pos]\n")
        f.write("            mapped = PUNCTUATIONS.get(ch)\n")
        f.write("            if mapped is not None:\n")
        f.write("                tokens.append((mapped, ch))\n")
        f.write("                print(f'⟶ Token: {mapped!r}, lexema: {ch!r}')\n")
        f.write("                pos += 1\n")
        f.write("                continue\n")
        # 3) Si el DFA sólo empata 1 carácter (ej. un dígito suelto)
        f.write("            if longest_match == 1:\n")
        f.write("                lexeme = text[pos]\n")
        f.write("                action_code = selected_rule['action']\n")
        f.write("                local_env = {'lexeme': lexeme, 'text': text}\n")
        f.write("                exec(action_code.replace('return', 'token ='), globals(), local_env)\n")
        f.write("                tok = local_env.get('token')\n")
        f.write("                # Solo guardamos si no es None\n")
        f.write("                if tok is not None:\n")
        f.write("                    tokens.append((tok, lexeme))\n")
        f.write("                    print(f'⟶ Token: {tok!r}, lexema: {lexeme!r}')\n")
        f.write("                pos += 1\n")
        f.write("                continue\n")
        # 4) Falló todo: error léxico
        f.write("            print(f'Error léxico en posición {pos}: símbolo no reconocido: {text[pos]}')\n")
        f.write("            pos += 1\n")
        f.write("        return tokens\n")
        f.write("\n")
        # Propiedad rules que reconstruye las reglas al momento de usar el lexer
        f.write("    @property\n")
        f.write("    def rules(self):\n")
        f.write("        rules = []\n")
        # Para cada regla, se genera el código que recrea el DFA (con la misma expresión expandida)
        for rule in rules:
            f.write("        from src.models.regex_parser import RegexParser\n")
            f.write("        from src.models.syntax_tree import SyntaxTree\n")
            f.write("        from src.models.dfa import DFA\n")
            f.write(f"        # Regla: {rule['regex']}\n")
            f.write(f"        parser = RegexParser({rule['regex']!r} + '#')\n")
            f.write("        parser.tokenize()\n")
            f.write("        postfix = parser.to_postfix()\n")
            f.write("        syntax_tree = SyntaxTree(postfix)\n")
            f.write("        dfa = DFA(syntax_tree)\n")
            f.write(f"        rules.append({{'regex': {rule['regex']!r}, 'action': {rule['action']!r}, 'dfa': dfa}})\n")
        f.write("        return rules\n")
        f.write("\n")
        
        # Escribir trailer (el código extraído del archivo YALex, si existe)
        # trailer = "\n".join(line.lstrip() for line in yalex_parser.trailer_code.splitlines())
        # f.write(trailer + "\n")
    
    print(f"\nAnalizador léxico generado y guardado en: {output_filename}")

if __name__ == "__main__":
    #extend_dfa_with_match_prefix()
    # test_full_pipeline("inputs/lexer.yal")
    
    # Ejecutar la generación del archivo final del analizador léxico
    generate_lexer()
    
    # run_app()