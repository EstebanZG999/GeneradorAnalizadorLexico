# tests/test_dfa.py

from models.mock_syntax_tree import build_mock_tree_for_ab_star_hash
from models.dfa import build_dfa

def test_build_dfa_mock():
    # 1. Obtener el árbol mock
    syntax_tree = build_mock_tree_for_ab_star_hash()

    # 2. Construir el AFD
    dfa = build_dfa(syntax_tree)
    
    # 3. (Opcional) Revisar transiciones
    print("=== Estados generados ===")
    for state, edges in dfa.transitions.items():
        print(f"  Desde {state}:")
        for symbol, next_state in edges.items():
            print(f"    Con '{symbol}' => {next_state}")

    # 4. Probar la simulación de algunas cadenas:
    for cadena in ["", "a", "b", "ab", "aba", "abb", "aaaabbbb"]:
        result = dfa.simulate(cadena)
        print(f"Cadena '{cadena}': {'ACEPTADA' if result else 'RECHAZADA'}")
