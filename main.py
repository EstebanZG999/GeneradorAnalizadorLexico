# main.py

from controllers.main_controller import run_app, test_yalex_parser

if __name__ == "__main__":
    test_yalex_parser("inputs/lexer.yal")

    #run_app()
