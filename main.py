# main.py

from controllers.main_controller import run_app, test_full_pipeline

if __name__ == "__main__":
    test_full_pipeline("inputs/lexer.yal")

    # run_app()
