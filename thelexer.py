# Código generado automáticamente por YALex
from src.runtime.token_types import *

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
                local_env = {'lexeme': lexeme, 'text': text}
                action_code = selected_rule['action'].replace('return', 'token =')
                exec(action_code, globals(), local_env)
                token = local_env.get('token', None)
                if token is not None:
                   tokens.append((token, lexeme))
                print(f'⟶ Token: {token!r}, lexema: {lexeme!r}')
                pos += longest_match
        return tokens

    @property
    def rules(self):
        rules = []
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: (([' ' '	'])+)
        parser = RegexParser("(([' ' '\t'])+)" + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': "(([' ' '\t'])+)", 'action': 'return None', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: "###".*[\n]
        parser = RegexParser('"###".*[\\n]' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': '"###".*[\\n]', 'action': 'return None', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: '\n'
        parser = RegexParser("'\\n'" + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': "'\\n'", 'action': 'return EOL', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: ((['A'-'Z''a'-'z']) (((['A'-'Z''a'-'z']) | (['0'-'9'])))*)
        parser = RegexParser("((['A'-'Z''a'-'z']) (((['A'-'Z''a'-'z']) | (['0'-'9'])))*)" + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': "((['A'-'Z''a'-'z']) (((['A'-'Z''a'-'z']) | (['0'-'9'])))*)", 'action': 'return ID', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: ((['0'-'9'])+ ('.' (['0'-'9'])+)? ('E' ['+' '-' ]? (['0'-'9'])+ )?)
        parser = RegexParser("((['0'-'9'])+ ('.' (['0'-'9'])+)? ('E' ['+' '-' ]? (['0'-'9'])+ )?)" + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': "((['0'-'9'])+ ('.' (['0'-'9'])+)? ('E' ['+' '-' ]? (['0'-'9'])+ )?)", 'action': 'return NUMBER', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: ":="
        parser = RegexParser('":="' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': '":="', 'action': "return ('ASSIGN', lexeme)", 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: '+'
        parser = RegexParser("'+'" + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': "'+'", 'action': "return ('PLUS',     lexeme)", 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: '-'
        parser = RegexParser("'-'" + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': "'-'", 'action': "return ('MINUS',    lexeme)", 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: '*'
        parser = RegexParser("'*'" + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': "'*'", 'action': "return ('TIMES',    lexeme)", 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: '/'
        parser = RegexParser("'/'" + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': "'/'", 'action': "return ('DIV',      lexeme)", 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: '('
        parser = RegexParser("'('" + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': "'('", 'action': "return ('LPAREN',   lexeme)", 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: ')'
        parser = RegexParser("')'" + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': "')'", 'action': "return ('RPAREN',   lexeme)", 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: ','
        parser = RegexParser("','" + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': "','", 'action': "return ('COMMA',    lexeme)", 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: ';'
        parser = RegexParser("';'" + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': "';'", 'action': "return ('SEMICOLON',lexeme)", 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: ':'
        parser = RegexParser("':'" + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': "':'", 'action': "return ('COLON',    lexeme)", 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: '<'
        parser = RegexParser("'<'" + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': "'<'", 'action': "return ('LT',       lexeme)", 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: '='
        parser = RegexParser("'='" + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': "'='", 'action': "return ('EQ',       lexeme)", 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: '>'
        parser = RegexParser("'>'" + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': "'>'", 'action': "return ('GT',       lexeme)", 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: eof
        parser = RegexParser('eof' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': 'eof', 'action': 'return EOF', 'dfa': dfa})
        from src.models.regex_parser import RegexParser
        from src.models.syntax_tree import SyntaxTree
        from src.models.dfa import DFA
        # Regla: .
        parser = RegexParser('.' + '#')
        parser.tokenize()
        postfix = parser.to_postfix()
        syntax_tree = SyntaxTree(postfix)
        dfa = DFA(syntax_tree)
        rules.append({'regex': '.', 'action': "return ('SYMBOL', lexeme)", 'dfa': dfa})
        return rules

