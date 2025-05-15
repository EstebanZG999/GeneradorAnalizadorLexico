# models/syntax_tree.py

import os
import graphviz

class NodoBase:
    def __init__(self, valor):
        self.valor = valor
        self.nullable = False
        self.firstpos = set()
        self.lastpos = set()

    # Método polimórfico a sobrescribir en hijos
    def to_dot(self, dot):
        pass

class NodoHoja(NodoBase):
    def __init__(self, valor, posicion):
        super().__init__(valor)
        self.posicion = posicion
        self.firstpos.add(posicion)
        self.lastpos.add(posicion)
        self.nullable = (valor == 'ε')

    def to_dot(self, dot):
        """Agrega este nodo hoja al gráfico DOT."""
        dot.node(str(id(self)),
                 f"{self.valor} ({self.posicion})",
                 shape="ellipse")


class NodoBinario(NodoBase):
    def __init__(self, valor, izquierdo, derecho):
        super().__init__(valor)
        self.izquierdo = izquierdo
        self.derecho = derecho
        self.calcular_propiedades()

    def calcular_propiedades(self):
        if self.valor == '.':  # Concatenación
            self.nullable = self.izquierdo.nullable and self.derecho.nullable

            self.firstpos = (self.izquierdo.firstpos |
                             (self.derecho.firstpos if self.izquierdo.nullable else set()))
            self.lastpos = (self.derecho.lastpos |
                            (self.izquierdo.lastpos if self.derecho.nullable else set()))

        elif self.valor == '|':  # Alternancia
            self.nullable = self.izquierdo.nullable or self.derecho.nullable
            self.firstpos = self.izquierdo.firstpos | self.derecho.firstpos
            self.lastpos = self.izquierdo.lastpos | self.derecho.lastpos


    def to_dot(self, dot):
        """Agrega este nodo binario y sus conexiones al gráfico DOT."""
        dot.node(str(id(self)),
                 f"{self.valor}",
                 shape="box")

        # Dibujar hijos
        self.izquierdo.to_dot(dot)
        self.derecho.to_dot(dot)

        # Conectar con aristas
        dot.edge(str(id(self)), str(id(self.izquierdo)))
        dot.edge(str(id(self)), str(id(self.derecho)))



class NodoUnario(NodoBase):
    def __init__(self, valor, hijo):
        super().__init__(valor)
        self.hijo = hijo
        self.calcular_propiedades()

    def calcular_propiedades(self):
        if self.valor == '*':  # Cerradura de Kleene
            self.nullable = True
            self.firstpos = self.hijo.firstpos
            self.lastpos = self.hijo.lastpos

    def to_dot(self, dot):
        """Agrega este nodo unario y su conexión al gráfico DOT."""
        dot.node(str(id(self)),
                 f"{self.valor}",
                 shape="diamond")

        self.hijo.to_dot(dot)
        dot.edge(str(id(self)), str(id(self.hijo)))



class SyntaxTree:
    def __init__(self, postfix):
        self.postfix = postfix
        self.posicion_actual = 1
        self.raiz = self.construir_arbol()
    
    def construir_arbol(self):
        stack = []
        for token in self.postfix:
            # token es un Symbol. Para hojas comparamos token.value
            if (token.value.isalnum() or token.value == '#') or not token.is_operator:
                nodo_hoja = NodoHoja(token.value, self.posicion_actual)
                stack.append(nodo_hoja)
                self.posicion_actual += 1
            elif token.value == '*':  # Nodo unario
                nodo = stack.pop()
                stack.append(NodoUnario(token.value, nodo))
            elif token.value == '+':  # Operador unario de "una o más"
                # Transformamos A+ en A concatenado con A*
                nodo = stack.pop()                    # A
                nodo_clausura = NodoUnario('*', nodo)   # A*
                nodo_concat = NodoBinario('.', nodo, nodo_clausura)  # A · A*
                stack.append(nodo_concat)
            elif token.value in {'.', '|'}:  # Nodo binario
                derecho = stack.pop()
                izquierdo = stack.pop()
                stack.append(NodoBinario(token.value, izquierdo, derecho))
            elif token.value == '?':  # Operador unario de "cero o una"
                nodo = stack.pop()                      # A
                # lo convertimos en (A | ε)
                hoja_epsilon = NodoHoja('ε', self.posicion_actual); self.posicion_actual += 1
                altern = NodoBinario('|', nodo, hoja_epsilon)
                stack.append(altern)

        # El último nodo en el stack es la raíz

        return stack.pop()
    
    def obtener_raiz(self):
        return self.raiz

    

    def render(self, filename="syntax_tree"):
        """Genera una imagen (PNG) del árbol sintáctico y la guarda en 'imagenes/'."""

        # Asegurar que la carpeta 'imagenes' existe
        if not os.path.exists("imagenes"):
            os.makedirs("imagenes")

        dot = graphviz.Digraph(format="png")
        if self.raiz:
            self.raiz.to_dot(dot)

        # Guardar la imagen en la carpeta 'imagenes/'
        output_path = f"imagenes/{filename}"
        dot.render(output_path, view=False)

        print(f"Imagen del árbol sintáctico guardada en: {output_path}.png")

if __name__ == "__main__":
    from regex_parser import RegexParser

    regex = "(a|b)a*bb#"
    parser = RegexParser(regex)
    postfix = parser.parse()
    
    # Imprimimos tokens y postfix para verificar
    print("Tokens:", [str(t) for t in parser.tokens])
    print("Postfix:", [str(p) for p in postfix])

    syntax_tree = SyntaxTree(postfix)
    raiz = syntax_tree.obtener_raiz()
    
    # Genera y muestra el árbol con Graphviz
    syntax_tree.render("syntax_tree")

    print("Árbol sintáctico construido y graficado correctamente.")
