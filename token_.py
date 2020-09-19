###################
# Token Types
###################
INT = "INT"
FLOAT = "FLOAT"
STRING = "STRING"
IDENTIFIER = "IDENTIFIER"
KEYWORD = "KEYWORD"
PLUS = "PLUS"
MINUS = "MINUS"
ASTERISK = "ASTERISK"
SLASH = "SLASH"
LPAREN = "LPAREN"
RPAREN = "RPAREN"
LSQUAREBRACKET = "LSQUAREBRACKET"
RSQUAREBRACKET = "RSQUAREBRACKET"
LBRACKET = "LBRACKET"
RBRACKET = "RBRACKET"
EQUAL = "EQUAL"
DOUBLE_EQUAL = "DOUBLE_EQUAL"
NOT_EQUAL = "NOT_EQUAL"
LESS_THAN = "LESS_THAN"
GREATER_THAN = "GREATER_THAN"
LESS_THAN_OR_EQUAL = "LESS_THAN_OR_EQUAL"
GREATER_THAN_OR_EQUAL = "GREATER_THAN_OR_EQUAL"
COLON = "COLON"
NOT = "NOT"
SEMICOLON = "SEMICOLON"
COMMA = "COMMA"
ARROW = "A"
EOF = "EOF"

###################
# KEYWORDS
###################
keywords = [
    "let",
    "var",
    "if",
    "else",
    "elif",
    "func",
    "return",
    "while",
    "for",
    "int",
    "float",
    "str",
    "bool"
]


###################
# Token
###################
class Token(object):
    def __init__(self, _type, _value=None, _position_start=None, _position_end=None):
        self.type = _type
        self.value = _value

        self.position_start = _position_start
        if _position_end:
            self.position_end = _position_end
        else:
            self.position_end = _position_start.advance()

    def matches(self, _type, _val):
        if self.type == _type and self.value == _val:
            return True
        else:
            return False

    def __repr__(self):
        if self.value:
            return "{}:{}".format(self.type, self.value)
        return "{}".format(self.type)

