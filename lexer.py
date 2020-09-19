import string
from token_ import *
from errors import IllegalCharError, UnexpectedCharError, CharacterNotFoundError

###################
# Constants
###################
DIGITS = '0123456789'
LETTERS = string.ascii_letters


###################
# Position
###################
class Position(object):
    def __init__(self, _index, _column, _line, _ftext, _filename):
        self.index = _index
        self.column = _column
        self.line = _line
        self.ftext = _ftext
        self.filename = _filename

    def advance(self, _current_char=None):
        self.index += 1
        self.column += 1

        if _current_char == "\n":
            self.line += 1
            self.column = 0

    def copy(self):
        return Position(self.index, self.column, self.line, self.ftext, self.filename)


###################
# Lexer
###################
class Lexer(object):
    def __init__(self, _input, _filename):
        self.input = _input
        self.filename = _filename
        self.position = Position(-1, -1, 0, self.input, self.filename)
        self.current_char = None
        self.errors = []

        self.advance()

    def advance(self):
        self.position.advance(self.current_char)
        self.current_char = self.input[self.position.index] if self.position.index < len(self.input) else None

    def tokenize(self):
        tokens = []

        while self.current_char is not None:
            if self.current_char in " \n\t":
                self.advance()
            elif self.is_number(self.current_char):
                tokens.append(self.make_number())
            elif self.is_letter(self.current_char):
                tokens.append(self.make_identifier())
            elif self.current_char == '"':
                tokens.append(self.make_string())
            elif self.current_char == "+":
                tokens.append(Token(PLUS, _position_start=self.position.copy()))
                self.advance()
            elif self.current_char == "-":
                tokens.append(Token(MINUS, _position_start=self.position.copy()))
                self.advance()
            elif self.current_char == "*":
                tokens.append(Token(ASTERISK, _position_start=self.position.copy()))
                self.advance()
            elif self.current_char == "/":
                tokens.append(Token(SLASH, _position_start=self.position.copy()))
                self.advance()
            elif self.current_char == "(":
                tokens.append(Token(LPAREN, _position_start=self.position.copy()))
                self.advance()
            elif self.current_char == ")":
                tokens.append(Token(RPAREN, _position_start=self.position.copy()))
                self.advance()
            elif self.current_char == "[":
                tokens.append(Token(LSQUAREBRACKET, _position_start=self.position.copy()))
                self.advance()
            elif self.current_char == "]":
                tokens.append(Token(RSQUAREBRACKET, _position_start=self.position.copy()))
                self.advance()
            elif self.current_char == "{":
                tokens.append(Token(LBRACKET, _position_start=self.position.copy()))
                self.advance()
            elif self.current_char == "}":
                tokens.append(Token(RBRACKET, _position_start=self.position.copy()))
                self.advance()
            elif self.current_char == "=":
                tokens.append(self.make_equals())
                self.advance()
            elif self.current_char == "<":
                tokens.append(self.make_less_than())
                self.advance()
            elif self.current_char == ">":
                tokens.append(self.make_greater_than())
                self.advance()
            elif self.current_char == ":":
                tokens.append(Token(COLON, _position_start=self.position.copy()))
                self.advance()
            elif self.current_char == ";":
                tokens.append(Token(SEMICOLON, _position_start=self.position.copy()))
                self.advance()
            elif self.current_char == ",":
                tokens.append(Token(COMMA, _position_start=self.position.copy()))
                self.advance()
            else:
                # TODO: FIND A CLEANER SOLUTION!!!
                _position_start = self.position.copy()
                pos_start = _position_start
                _position_start.advance()
                _position_end = _position_start

                self.errors.append(IllegalCharError(f"Illegal character {self.current_char}", pos_start, _position_end))
                self.advance()

        tokens.append(Token(EOF, _position_start=self.position))

        if self.errors:
            return None, self.errors
        return tokens, None

    def make_number(self):
        position_start = self.position.copy()
        dot_count = 0
        while self.is_number(self.current_char) or self.current_char == ".":
            if self.current_char == ".":
                dot_count += 1
            if dot_count > 1:
                _position_start = self.position.copy()
                pos_start = _position_start
                _position_start.advance()
                _position_end = _position_start

                self.errors.append(UnexpectedCharError(f"Unexpected character '{self.current_char}'", pos_start, _position_end))
                
                self.advance()
                return
            self.advance()
        
        if dot_count == 0:
            return Token(INT, int(self.input[position_start.index:self.position.index]), position_start, self.position.copy())
        else:
            return Token(FLOAT, float(self.input[position_start.index:self.position.index]), position_start, self.position.copy())
        
    def make_identifier(self):
        position_start = self.position.copy()

        while self.is_letter(self.current_char, mode=1):
            self.advance()

        identifier = self.input[position_start.index:self.position.index]
        if identifier in keywords:
            return Token(KEYWORD, identifier, position_start, self.position.copy())
        else:
            return Token(IDENTIFIER, identifier, position_start, self.position.copy())

    def make_string(self):
        position_start = self.position.copy()

        self.advance()

        while self.current_char != "\"":
            self.advance()
            if self.current_char == None:
                self.errors.append(CharacterNotFoundError(f"String quotation marks are not closed", position_start, self.position.copy()))
                return

        self.advance()

        return Token(STRING, self.input[position_start.index+1:self.position.index-1], position_start, self.position.copy())

    def make_equals(self):
        position_start = self.position.copy()

        try:
            if self.input[self.position.index + 1] == "=":
                self.advance()
                return Token(DOUBLE_EQUAL, _position_start=position_start, _position_end=self.position.copy())
            elif self.input[self.position.index + 1] == ">":
                self.advance()
                return Token(ARROW, _position_start=position_start, _position_end=self.position.copy())
        except:
            pass
        return Token(EQUAL, _position_start=position_start)
    
    def make_not_equals(self):
        position_start = self.position.copy()

        try:
            if self.input[self.position.index + 1] == "=":
                self.advance()
                return Token(NOT_EQUAL, _position_start=position_start, _position_end=self.position.copy())
        except:
            pass
        return Token(NOT, _position_start=position_start)
    def make_less_than(self):
        position_start = self.position.copy()

        try:
            if self.input[self.position.index + 1] == "=":
                self.advance()
                return Token(LESS_THAN_OR_EQUAL, _position_start=position_start, _position_end=self.position.copy())
        except:
            pass
        return Token(LESS_THAN, _position_start=position_start)

    def make_greater_than(self):
        position_start = self.position.copy()

        try:
            if self.input[self.position.index + 1] == "=":
                self.advance()
                return Token(GREATER_THAN_OR_EQUAL, _position_start=position_start, _position_end=self.position.copy())
        except:
            pass
        return Token(GREATER_THAN, _position_start=position_start)

    def is_number(self, char):
        if str(char) in DIGITS:
            return True
        return False

    def is_letter(self, char, mode=0):
        if mode == 0:
            if str(char) in LETTERS + "_":
                return True
            else:
                return False
        else:
            if str(char) in LETTERS + "_" + DIGITS:
                return True
            else:
                return False





