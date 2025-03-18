# Código generado automáticamente por YALex
class Lexer:
    def __init__(self, input_text):
        self.input_text = input_text
        self.pos = 0

    def get_tokens(self):
        tokens = []
        text = self.input_text
        pos = 0
        while pos < len(text):
            longest_match = 0
            selected_rule = None
            for rule in self.rules:
                match_length = rule['dfa'].match_prefix(text[pos:])
                if match_length > longest_match:
                    longest_match = match_length
                    selected_rule = rule
            if longest_match == 0:
                print(f'Error léxico en posición {pos}: símbolo no reconocido: {text[pos]}')
                pos += 1
            else:
                lexeme = text[pos:pos+longest_match]
                if lexeme.endswith('#'):
                    lexeme = lexeme[:-1]
                local_env = {'lexeme': lexeme, 'text': text}
                action_code = selected_rule['action'].replace('return', 'token =')
                exec(action_code, {}, local_env)
                token = local_env.get('token', None)
                if token is not None:
                   tokens.append(token)
                pos += longest_match
        return tokens

    @property
    def rules(self):
        rules = []
        from models.regex_parser import RegexParser
        from models.syntax_tree import SyntaxTree
        from models.dfa import DFA
        # Regla: [' ' '\t']#
        parser = RegexParser(r'''[' ' '\t']#''')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': r'''[' ' '\t']#''', 'action': r'''return None''', 'dfa': dfa})
        from models.regex_parser import RegexParser
        from models.syntax_tree import SyntaxTree
        from models.dfa import DFA
        # Regla: ([0-9])+#
        parser = RegexParser(r'''([0-9])+#''')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': r'''([0-9])+#''', 'action': r'''return ("NUMBER", int(lexeme))''', 'dfa': dfa})
        from models.regex_parser import RegexParser
        from models.syntax_tree import SyntaxTree
        from models.dfa import DFA
        # Regla: '+'#
        parser = RegexParser(r''''+'#''')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': r''''+'#''', 'action': r'''return ("PLUS", "+")''', 'dfa': dfa})
        from models.regex_parser import RegexParser
        from models.syntax_tree import SyntaxTree
        from models.dfa import DFA
        # Regla: '-'#
        parser = RegexParser(r''''-'#''')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': r''''-'#''', 'action': r'''return ("MINUS", "-")''', 'dfa': dfa})
        from models.regex_parser import RegexParser
        from models.syntax_tree import SyntaxTree
        from models.dfa import DFA
        # Regla: '*'#
        parser = RegexParser(r''''*'#''')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': r''''*'#''', 'action': r'''return ("TIMES", "*")''', 'dfa': dfa})
        from models.regex_parser import RegexParser
        from models.syntax_tree import SyntaxTree
        from models.dfa import DFA
        # Regla: '('#
        parser = RegexParser(r''''('#''')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': r''''('#''', 'action': r'''return ("LPAREN", "(")''', 'dfa': dfa})
        from models.regex_parser import RegexParser
        from models.syntax_tree import SyntaxTree
        from models.dfa import DFA
        # Regla: ')'#
        parser = RegexParser(r'''')'#''')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': r'''')'#''', 'action': r'''return ("RPAREN", ")")''', 'dfa': dfa})
        from models.regex_parser import RegexParser
        from models.syntax_tree import SyntaxTree
        from models.dfa import DFA
        # Regla: eof#
        parser = RegexParser(r'''eof#''')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': r'''eof#''', 'action': r'''return ("EOF", None)''', 'dfa': dfa})
        from models.regex_parser import RegexParser
        from models.syntax_tree import SyntaxTree
        from models.dfa import DFA
        # Regla: '\n'#
        parser = RegexParser(r''''\n'#''')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': r''''\n'#''', 'action': r'''return ("EOL", None)''', 'dfa': dfa})
        return rules

