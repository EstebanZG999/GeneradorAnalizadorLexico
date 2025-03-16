# mindfa.py

from .dfa import DFA
import graphviz

def minimize_dfa(dfa: DFA) -> DFA:
    """
    Minimiza el DFA usando el algoritmo de Hopcroft.
    Devuelve una NUEVA instancia de DFA que represente el autómata mínimo.
    """

    # 1) Recolectar la info necesaria
    # --------------------------------
    all_states = set(dfa.states.values())  # conjunto de IDs de estados (ej. {0, 1, 2, ...})
    alphabet = dfa.alphabet
    accepting_states = dfa.accepting_states
    initial_state = dfa.initial_state

    # 2) Crear la partición inicial: A = estados de aceptación, B = el resto
    # ---------------------------------------------------------------------
    A = accepting_states
    B = all_states - A
    # P (partición) y W (conjunto de bloques a refinar)
    P = [A, B] if B else [A]  # si B está vacío, no lo metemos
    W = [A, B] if B else [A]

    # 3) Algoritmo de Hopcroft: refinamiento de bloques
    # -------------------------------------------------
    # P = Pila de bloques (particiones), W = cola de bloques a procesar
    while W:
        R = W.pop()  # Toma un bloque a refinar
        for symbol in alphabet:
            # X = todos los estados que tienen transición con `symbol` a un estado de R
            X = set()
            # Para cada estado en todo el autómata
            for state in all_states:
                # Determina el posible destino
                destino = dfa.transitions.get(state, {}).get(symbol, None)
                if destino in R:
                    X.add(state)

            # Para cada bloque Y en P, vamos a ver la intersección con X
            new_P = []
            for Y in P:
                # Intersección y diferencia
                intersection = Y.intersection(X)
                difference = Y - X
                if intersection and difference:
                    # Se parte Y en intersection y difference
                    new_P.append(intersection)
                    new_P.append(difference)
                    # Ajustar W
                    if Y in W:
                        # Reemplaza Y en W por los dos sub-bloques
                        W.remove(Y)
                        W.append(intersection)
                        W.append(difference)
                    else:
                        # Añade el sub-bloque más pequeño
                        if len(intersection) <= len(difference):
                            W.append(intersection)
                        else:
                            W.append(difference)
                else:
                    # Si no hay partición, queda igual
                    new_P.append(Y)
            P = new_P

    # 4) Construir el DFA mínimo a partir de la partición final P
    # -----------------------------------------------------------
    # Ahora, cada bloque en P es un estado "colapsado" en el DFA mínimo.

    # Asignar un ID nuevo a cada bloque
    min_state_map = {}  # asigna "representante" -> "nuevo estado ID"
    new_states_list = []
    new_id = 0

    for block in P:
        # Escogemos un representante (podría ser min(block) o simplemente sacamos uno)
        rep = min(block)  # escogemos el menor ID como "representante"
        for st in block:
            min_state_map[st] = new_id
        new_states_list.append(block)
        new_id += 1

    # Estados de aceptación en el DFA mínimo
    new_accepting_states = set()
    for block in P:
        # Si al menos un estado del bloque era de aceptación, todo el bloque lo es
        rep = min(block)
        if block & accepting_states:  # intersección no vacía
            new_accepting_states.add(min_state_map[rep])

    # Nuevo estado inicial
    new_initial_state = min_state_map[initial_state]

    # Construir nuevas transiciones
    new_transitions = {}
    for block in P:
        rep = min(block)  # ID representativo
        rep_new_state = min_state_map[rep]
        new_transitions[rep_new_state] = {}
        # Tomamos las transiciones del representative
        for symbol in alphabet:
            old_target = dfa.transitions[rep].get(symbol, None)
            if old_target is not None:
                new_target = min_state_map[old_target]
                new_transitions[rep_new_state][symbol] = new_target

    # 5) Crear un nuevo DFA con la información minimizada
    # ---------------------------------------------------
    min_dfa = DFA.__new__(DFA)  # creamos una instancia vacía de DFA
    # Llenamos sus atributos
    min_dfa.alphabet = alphabet
    # Reconstruimos states como { frozenset(...) : id }, aunque ya no necesitamos frozenset.
    # Pero para mantener la misma interfaz, guardamos que cada "bloque" se asocia a un ID.
    min_dfa.states = {}
    for block_idx, block in enumerate(P):
        # construimos un set ficticio como "frozenset(block)"
        # *pero ojo, block contiene IDs, no sets de posiciones
        # si quieres, asigna un dummy: frozenset({block_idx})
        # Lo importante es no romper la interfaz.  ;)
        min_dfa.states[frozenset(block)] = block_idx

    min_dfa.transitions = new_transitions
    min_dfa.initial_state = new_initial_state
    min_dfa.accepting_states = new_accepting_states
    min_dfa.followpos = None  # ya no es relevante
    min_dfa.pos_to_symbol = None  # ya no es relevante
    return min_dfa


def render_mindfa(dfa, filename="mindfa"):
    dot = graphviz.Digraph(format="png")
    for state_set, state_id in dfa.states.items():
        shape = "doublecircle" if state_id in dfa.accepting_states else "circle"
        label = f"q{state_id}\n{state_set}"
        dot.node(str(state_id), label=label, shape=shape)

    dot.node("start", shape="none", label="")
    dot.edge("start", str(dfa.initial_state))

    for state_id, trans_dict in dfa.transitions.items():
        for symbol, target_id in trans_dict.items():
            dot.edge(str(state_id), str(target_id), label=symbol)

    dot.render(filename, view=True)



if __name__ == "__main__":
    """
    Ejemplo de uso de la función minimize_dfa
    """
    from regex_parser import RegexParser
    from syntax_tree import SyntaxTree
    # Importar la clase DFA
    from dfa import DFA

    regex = "(a|b)*abb#"
    parser = RegexParser(regex)
    postfix = parser.parse()
    syntax_tree = SyntaxTree(postfix)
    dfa = DFA(syntax_tree)

    print("=== DFA original ===")
    dfa.print_dfa()

    min_dfa = minimize_dfa(dfa)

    print("\n=== DFA mínimo ===")
    min_dfa.print_dfa()

    # Ejemplo de simulación con el DFA mínimo
    test_strings = ["aaabb", "aabb", "ababb", "ababbbbabb"]
    for s in test_strings:
        result = min_dfa.simulate(s)
        print(f"La cadena '{s}' {'es aceptada' if result else 'NO es aceptada'} por el DFA mínimo.")

    render_mindfa(min_dfa, "mindfa")

