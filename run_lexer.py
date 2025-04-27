import sys
import os

# Asegurarse de que el directorio raíz esté en el path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.controllers.main_controller import generate_lexer, extend_dfa_with_match_prefix

# Extender el DFA con el método match_prefix (necesario para la simulación)
extend_dfa_with_match_prefix()

# Generar (o actualizar) el analizador léxico a partir de la especificación YALex
generate_lexer()

from thelexer import Lexer

def main():
    # Si no se pasa un archivo de entrada, usamos uno por defecto en 'inputs'
    if len(sys.argv) < 2:
        default_input_file = os.path.join("inputs", "entrada.txt")
        print(f"No se especificó archivo de entrada. Usando '{default_input_file}' por defecto.")
        input_file = default_input_file
    else:
        input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"Error: El archivo '{input_file}' no existe.")
        sys.exit(1)
    
    with open(input_file, "r", encoding="utf-8") as f:
        entrada = f.read()
    
    lexer = Lexer(entrada)
    tokens = lexer.get_tokens()
    
    print("Tokens reconocidos:")
    for token in tokens:
        print(token)

if __name__ == "__main__":
    main()
