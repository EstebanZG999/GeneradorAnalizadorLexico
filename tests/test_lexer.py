import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from controllers.main_controller import extend_dfa_with_match_prefix
extend_dfa_with_match_prefix()

from thelexer import Lexer

def main():
    entrada = """10 + 2
    5 - 3
    8 * 4"""
    lexer = Lexer(entrada)
    tokens = lexer.get_tokens()
    print(tokens)

if __name__ == "__main__":
    main()
