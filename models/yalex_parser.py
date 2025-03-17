# models/yalex_parser.py

import re

class YALexParser:
    def __init__(self, filename):
        self.filename = filename
        self.header_code = ""
        self.trailer_code = ""
        self.definitions = {}  # guardará {ident: regex_string}
        self.rules = []        # lista de (regex_string, action_code)
        self.entrypoint = None # nombre de la regla principal, si lo usas

    def parse(self):
        with open(self.filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Extraer {header} (asumiendo que el header es el primer bloque entre { })
        header_match = re.search(r'^\s*\{(.*?)\}', content, re.DOTALL)
        if header_match:
            self.header_code = header_match.group(1).strip()
            content = content[header_match.end():]  # quitar el header

        # 2. Extraer definiciones de tipo "let IDENT = regex"
        for match in re.finditer(r'let\s+(\w+)\s*=\s*(.+)', content):
            ident = match.group(1)
            regex_str = match.group(2).strip()
            self.definitions[ident] = regex_str

        # 3. Extraer la sección de reglas
        rule_match = re.search(r'rule\s+(\w+)(?:\s*\[.*?\])?\s*=\s*(.*)', content, re.DOTALL)
        if rule_match:
            self.entrypoint = rule_match.group(1).strip()
            rules_content = rule_match.group(2).strip()
            # Asumimos que cada alternativa tiene el formato: regexp { action }
            rules = re.findall(r'(.*?)\{(.*?)\}', rules_content, re.DOTALL)
            self.rules = [(r.strip(), a.strip()) for r, a in rules]

        # 4. Extraer {trailer} (si existe, asumimos que es el último bloque entre { } al final)
        trailer_match = re.search(r'\{(.*?)\}\s*$', content, re.DOTALL)
        if trailer_match:
            self.trailer_code = trailer_match.group(1).strip()

    def expand_definitions(self, regex_str):
        # Reemplaza en regex_str cada identificador definido en self.definitions
        for ident, definition in self.definitions.items():
            regex_str = re.sub(r'\b' + re.escape(ident) + r'\b', f'({definition})', regex_str)
        return regex_str