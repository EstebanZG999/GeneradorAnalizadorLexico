# src/runtime/token_types.py

SKIP  = "skip"
EOL   = "EOL"
PLUS  = "PLUS"
MINUS = "MINUS"
TIMES = "TIMES"
LPAREN= "LPAREN"
RPAREN= "RPAREN"
LBRACE   = "LBRACE"
RBRACE   = "RBRACE"
EOF   = "EOF"
WORD  = "WORD"
LETTER= "LETTER"
NUMBER= "NUMBER"
ID        = "ID"
SEMICOLON = "SEMICOLON"
ASSIGNOP  = "ASSIGNOP"
LT        = "LT"
EQ        = "EQ"
IF       = "IF"
ELSE     = "ELSE"
WHILE    = "WHILE"
FOR      = "FOR"
RETURN   = "RETURN"
BREAK    = "BREAK"
CONTINUE = "CONTINUE"
KEYWORDS = {
    "if":     IF,
    "else":   ELSE,
    "while":  WHILE,
    "for":    FOR,
    "return": RETURN,
    "break":  BREAK,
    "continue": CONTINUE,
}