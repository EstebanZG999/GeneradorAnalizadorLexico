# models/regex_parser.py

import re
from collections import deque

class Symbol:
    def __init__(self, value, is_operator=False):
        self.value = value
        self.is_operator = is_operator

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value 

class RegexParser:
    OPERATORS = {'|', '.', '*', '+'} 
    PRECEDENCE = {'|': 1, '.': 2, '*': 3, '+': 3} 

    def __init__(self, regex):
        self.regex = regex
        self.tokens = []
    
    def should_concat(self, last_token, current_token_type):
        """
        Decide si se debe insertar un operador de concatenación antes de agregar un token
        """
        if last_token is None:
            return False
        if last_token.is_operator:
            if last_token.value not in {')', '*', '+'}:
                return False
        # Si el token actual es literal o el inicio de un grupo, se concatena.
        if current_token_type in ['literal', 'group_start']:
            return True
        return False

    def expand_range(self, c1, c2):
        """
        Retorna la lista de caracteres que van desde c1..c2.
        """
        start = ord(c1)
        end = ord(c2)
        if start > end:
            start, end = end, start
        
        expanded = []
        for code in range(start, end + 1):
            expanded.append(chr(code))
        return expanded
    
    def parse_bracket_expression(self, bracket_content):
        """
        Dado el contenido dentro de [ ], genera una lista de tokens equivalente
        """
        i = 0
        elements = []  # guardará listas de caracteres
        
        while i < len(bracket_content):
            # Verificamos si hay patrón X-Y
            if i+2 < len(bracket_content) and bracket_content[i+1] == '-':
                # Tenemos un patrón X-Y
                c1 = bracket_content[i]
                c2 = bracket_content[i+2]
                expanded_chars = self.expand_range(c1, c2)
                elements.append(expanded_chars)
                i += 3  # saltamos X-Y
            else:
                # Es un carácter suelto
                elements.append([bracket_content[i]])
                i += 1

        all_chars = []
        for idx, block in enumerate(elements):
            # block es lista de caracteres expandidos
            if not block:
                continue
            # Insertar los caracteres de 'block' separados por '|'
            for j, c in enumerate(block):
                # Añadimos el carácter como literal
                all_chars.append(Symbol(c, is_operator=False))
                # Si no es el último carácter de este bloque, ponemos '|'
                if j < len(block) - 1:
                    all_chars.append(Symbol('|', is_operator=True))
            # Si no es el último bloque, añadimos otro OR
            if idx < len(elements) - 1:
                all_chars.append(Symbol('|', is_operator=True))

        final_tokens = []
        final_tokens.append(Symbol('(', is_operator=True))
        final_tokens.extend(all_chars)
        final_tokens.append(Symbol(')', is_operator=True))
        
        return final_tokens

    
    def tokenize(self):
        """
        Convierte la expresión regular en una lista de tokens, insertando concatenaciones explícitas.
        Se utiliza enumerate para saber cuándo es el último carácter (por ejemplo, para el '#' final).
        """
        output = []
        last_token = None 
        escaped = False

        skip_until = -1
        
        for i, char in enumerate(self.regex):
            if i < skip_until:
                continue
            if escaped: # Si el carácter está escapado, lo tratamos como literal.
                if self.should_concat(last_token, 'literal'):
                    output.append(Symbol('.', is_operator=True))
                token = Symbol(char, is_operator=False)
                output.append(token)
                last_token = token
                escaped = False
                continue
            elif char == '\\':
                escaped = True
                continue

            # Detectar '['
            elif char == '[':
                # Buscar la posición del ']' correspondiente
                j = i + 1
                found_closing = False
                while j < len(self.regex):
                    if self.regex[j] == ']':
                        found_closing = True
                        break
                    j += 1
                if not found_closing:
                    raise ValueError("Falta ']' de cierre en la expresión regular.")
                
                bracket_content = self.regex[i+1 : j]  # extraemos todo lo que hay dentro de [ ]
                
                # Expandimos a un grupo de tokens
                bracket_tokens = self.parse_bracket_expression(bracket_content)
            
                # Verificamos si hace falta concatenar
                if self.should_concat(last_token, 'literal'):
                    output.append(Symbol('.', is_operator=True))
                
                output.extend(bracket_tokens)
                last_token = bracket_tokens[-1] if bracket_tokens else None

                skip_until = j + 1
                continue
            elif char == "'" or char == '"':
                # Procesar literal entre comillas.
                quote_char = char
                literal = ""
                j = i + 1
                while j < len(self.regex) and self.regex[j] != quote_char:
                    literal += self.regex[j]
                    j += 1
                if j >= len(self.regex):
                    raise ValueError("No se encontró la comilla de cierre para literal.")
                # Actualizamos 'skip_until' para saltar el literal entero
                skip_until = j + 1
                if self.should_concat(last_token, 'literal'):
                    output.append(Symbol('.', is_operator=True))
                literal = bytes(literal, "utf-8").decode("unicode_escape")
                token = Symbol(literal, is_operator=False)
                output.append(token)
                last_token = token
                continue
            elif char.isalnum() or char == '#'or char == '$':  # Simbolo o marcador de fin
                # Inserta concatenación si no es el último
                if self.should_concat(last_token, 'literal'):
                    output.append(Symbol('.', is_operator=True))
                token = Symbol(char, is_operator=False)
                output.append(token)
                last_token = token
                continue
            elif char in self.OPERATORS:
                token = Symbol(char, is_operator=True)
                output.append(token)
                if char == '|':
                    last_token = None
                else:
                    last_token = token
                continue
            elif char == '(':
                if self.should_concat(last_token, 'group_start'):
                    output.append(Symbol('.', is_operator=True))
                token = Symbol('(', is_operator=True)
                output.append(token)
                last_token = None
                continue
            elif char == ')':
                output.append(Symbol(')', is_operator=True))
                last_token = Symbol(')', is_operator=True)
                continue
            elif char.isspace():
                continue
            elif ord(char) >= 128:
                if self.should_concat(last_token, 'literal'):
                    output.append(Symbol('.', is_operator=True))
                token = Symbol(char, is_operator=False)
                output.append(token)
                last_token = token
                continue
            raise ValueError(f"Carácter no reconocido: {char}")

        if escaped:
            raise ValueError("Secuencia de escape incompleta en la expresión regular.")

        self.tokens = output
        return output
    
    def to_postfix(self):
        output = []
        stack = deque()
        
        for token in self.tokens:
            if not token.is_operator:
                output.append(token)
            elif token.value == '(':
                stack.append(token)
            elif token.value == ')':
                while stack and stack[-1].value != '(':
                    output.append(stack.pop())
                if stack:
                    stack.pop()  # Descarta el '('
                else:
                    raise ValueError("No se encontró un '(' que haga match con ')'.")
            elif token.value in {'|', '.'}:  # operadores binarios
                while (stack and stack[-1].value in {'|', '.'} and
                       self.PRECEDENCE[token.value] <= self.PRECEDENCE[stack[-1].value]):
                    output.append(stack.pop())
                stack.append(token)
            elif token.value in {'*', '+'}:  # operadores unarios
                output.append(token)
            else:
                stack.append(token)
        
        while stack:
            op = stack.pop()
            if op.value in {'(', ')'}:
                raise ValueError("Paréntesis desbalanceados")
            output.append(op)
    
        return output

    
    def parse(self):
        """
        Método principal que convierte la expresión en tokens y en notación postfija.
        """
        self.tokenize()
        return self.to_postfix()

if __name__ == "__main__":
    regex = "[A-Za-z]bb#"
    parser = RegexParser(regex)
    postfix = parser.parse()
    print("Tokens:", [str(token) for token in parser.tokens])  
    print("Postfix:", [str(token) for token in postfix])  
