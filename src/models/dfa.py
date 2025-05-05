# src/models/dfa.py
import os
import graphviz
from src.models.syntax_tree import NodoHoja, NodoBinario, NodoUnario, SyntaxTree

class DFA:
    def __init__(self, syntax_tree):
        self.syntax_tree = syntax_tree
        # Calcula la función followpos y el mapeo de posiciones a símbolos
        self.followpos = self.compute_followpos(syntax_tree.raiz)
        self.pos_to_symbol = self.compute_pos_to_symbol(syntax_tree.raiz)
        # Definir el alfabeto (excluimos el marcador '#' de entrada)
        self.alphabet = { sym for sym in self.pos_to_symbol.values() if sym != '#' }
        # Diccionario para almacenar los estados (clave: frozenset de posiciones, valor: ID del estado)
        self.states = {}
        # Tabla de transiciones: {estado_id: {símbolo: estado_id_destino}}
        self.transitions = {}
        self.initial_state = None
        self.accepting_states = set()
        # Construir el AFD
        self.build_dfa()

    def compute_followpos(self, node):
        followpos = {}

        def init_followpos(n):
            if isinstance(n, NodoHoja):
                followpos[n.posicion] = set()
            elif isinstance(n, NodoBinario):
                init_followpos(n.izquierdo)
                init_followpos(n.derecho)
            elif isinstance(n, NodoUnario):
                init_followpos(n.hijo)
        init_followpos(node)

        def traverse(n):
            if isinstance(n, NodoBinario):
                traverse(n.izquierdo)
                traverse(n.derecho)
                if n.valor == '.':
                    # Para cada p en lastpos(izquierdo), followpos[p] += firstpos(derecho)
                    for pos in n.izquierdo.lastpos:
                        followpos[pos].update(n.derecho.firstpos)
            elif isinstance(n, NodoUnario):
                traverse(n.hijo)
                if n.valor == '*':
                    # Para cada p en lastpos(hijo), followpos[p] += firstpos(hijo)
                    for pos in n.hijo.lastpos:
                        followpos[pos].update(n.hijo.firstpos)
            # NodoHoja no hace nada
        traverse(node)

        return followpos


    def compute_pos_to_symbol(self, node):
        """Crea un diccionario que mapea cada posición de un nodo hoja a su símbolo."""
        pos_to_symbol = {}

        def traverse(n):
            if isinstance(n, NodoHoja):
                pos_to_symbol[n.posicion] = n.valor
            elif isinstance(n, NodoBinario):
                traverse(n.izquierdo)
                traverse(n.derecho)
            elif isinstance(n, NodoUnario):
                traverse(n.hijo)
        traverse(node)
        return pos_to_symbol

    def build_dfa(self):
        initial = frozenset(self.syntax_tree.raiz.firstpos)
        self.states[initial] = 0
        self.initial_state = 0
        unmarked_states = [initial]
        state_id_counter = 0

        while unmarked_states:
            current = unmarked_states.pop(0)
            current_state_id = self.states[current]
            self.transitions[current_state_id] = {}

            for symbol in self.alphabet:
                u = set()
                for pos in current:
                    if self.pos_to_symbol[pos] == symbol:
                        u.update(self.followpos[pos])
                if u:
                    u = frozenset(u)
                    if u not in self.states:
                        state_id_counter += 1
                        self.states[u] = state_id_counter
                        unmarked_states.append(u)
                    self.transitions[current_state_id][symbol] = self.states[u]

        # Estados de aceptación: usa get() para evitar KeyError si falta alguna posición
        for state_set, state_id in self.states.items():
            if any(self.pos_to_symbol.get(pos) == '#' for pos in state_set):
                self.accepting_states.add(state_id)
        # Fallback: solo si aún no hay aceptadores Y hay posiciones definidas
        if not self.accepting_states and self.pos_to_symbol:
            max_pos = max(self.pos_to_symbol.keys())
            for state_set, state_id in self.states.items():
                if max_pos in state_set:
                    self.accepting_states.add(state_id)
        

    def simulate(self, string):
        """
        Simula el AFD con la cadena de entrada 'string'.
        Retorna True si, tras procesar todos los caracteres,
        el estado en que quedas está marcado como de aceptación.
        """
        current = self.initial_state
        for ch in string:
            trans = self.transitions.get(current, {})
            if ch not in trans:
                return False
            current = trans[ch]
        return current in self.accepting_states



    def print_dfa(self):
        """Imprime la tabla de transiciones y los estados de aceptación."""
        print("Estados y sus conjuntos de posiciones:")
        for state_set, state_id in self.states.items():
            aceptacion = " (aceptación)" if state_id in self.accepting_states else ""
            print(f"Estado {state_id}{aceptacion}: {set(state_set)}")
        print("\nTransiciones:")
        for state_id, trans in self.transitions.items():
            for symbol, target in trans.items():
                print(f"  δ({state_id}, '{symbol}') = {target}")




    def render_dfa(self, filename="dfa"):
        """
        Genera un diagrama del AFD usando Graphviz y lo guarda en la carpeta 'imagenes/'.
        """
        # Asegurar que la carpeta 'imagenes' existe
        if not os.path.exists("imagenes"):
            os.makedirs("imagenes")

        dot = graphviz.Digraph(format="png")

        # Agregar estados
        for state_set, state_id in self.states.items():
            shape = "doublecircle" if state_id in self.accepting_states else "circle"
            label = f"q{state_id}\n{state_set}"
            dot.node(str(state_id), label=label, shape=shape)

        # Estado inicial
        dot.node("start", shape="none", label="")
        dot.edge("start", str(self.initial_state))

        # Agregar transiciones
        for state_id, trans_dict in self.transitions.items():
            for symbol, target_id in trans_dict.items():
                symbol_escaped = symbol.replace('\\', '\\\\').replace('"', '\\"')
                dot.edge(str(state_id), str(target_id), label=f"\"{symbol_escaped}\"")

        # Guardar la imagen en la carpeta 'imagenes/'
        output_path = f"imagenes/{filename}"
        dot.render(output_path, view=False)

        print(f"Imagen del DFA guardada en: {output_path}.png")

    def match_prefix(self, input_str):
        """
        Returns the length of the longest prefix (including the implicit '#')
        that lands in an accepting state.
        """
        current_state = self.initial_state
        last_accept_pos = -1
        pos = 0
        # scan all chars _and_ the trailing '#'
        for ch in input_str + '#':
            trans = self.transitions.get(current_state, {})
            if ch in trans:
                current_state = trans[ch]
                pos += 1
                if current_state in self.accepting_states:
                    last_accept_pos = pos
            else:
                break
        # if we never hit an accepting state, return 0
        return last_accept_pos if last_accept_pos != -1 else 0

 
 
if __name__ == "__main__":
    # Ejemplo de uso:
    # 1. Se define una expresión regular.
    regex = "(a|b)*abb#"
    # 2. Se crea el parser y se genera la notación postfija.
    from regex_parser import RegexParser
    parser = RegexParser(regex)
    postfix = parser.parse()
    # 3. Se construye el árbol sintáctico.
    syntax_tree = SyntaxTree(postfix)
    # 4. Se construye el AFD a partir del árbol sintáctico.
    dfa = DFA(syntax_tree)
    
    # Imprime la tabla de transiciones y los estados.
    print("Tokens:", [str(token) for token in parser.tokens])
    print("Postfix:", [str(token) for token in postfix])

    dfa.print_dfa()
    
    # 5. Simulación del AFD con cadenas de prueba.
    test_strings = ["aaabb", "aabb", "ababb", "ababbbbabb"]
    for s in test_strings:
        result = dfa.simulate(s)
        print(f"\nLa cadena '{s}' {'es aceptada' if result else 'NO es aceptada'} por la expresión regular.")

    dfa.render_dfa("dfa")  