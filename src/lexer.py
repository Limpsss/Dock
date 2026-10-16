from errors import *
import string

############################################
# CONSTANTS
############################################

DIGITS = "0123456789"
LETTERS = string.ascii_letters

############################################
# POSITION
############################################

class Position:
    def __init__(self, index, line, column, filename, filetext):
        self.index = index
        self.line = line
        self.column = column
        self.filename = filename
        self.filetext = filetext

    def advance(self, current_char=None):
        self.index += 1
        self.column += 1

        # Vid newline nollställs column och line ökar med 1 
        if current_char == "\n":
            self.line += 1
            self.column = 0
        return self
    
    def copy(self):
        return Position(self.index, self.line, self.column, self.filename, self.filetext)

############################################
# TOKENS
############################################

TT_IDENTIFIER       = "IDENTIFIER"
TT_KEYWORD          = "KEYWORD"
TT_LOG_OPERATOR     = "LOG_OPERATOR"
TT_COMP_OPERATOR    = "COMP_OPERATOR"
TT_STRING           = "STRING"
TT_INT              = "INT"
TT_FLOAT            = "FLOAT"
TT_PLUS             = "PLUS"
TT_MINUS            = "MINUS"
TT_MUL              = "MUL"
TT_DIV              = "DIV"
TT_EQUALS           = "EQUALS"
TT_LPAREN           = "LPAREN"
TT_RPAREN           = "RPAREN"
TT_LBRACK           = "LBRACK"
TT_RBRACK           = "RBRACK"
TT_LSQUARE          = "LSQUARE"
TT_RSQUARE          = "RSQUARE"
TT_POWEROP          = "POWEROP"
TT_COMMA            = "COMMA"
TT_NEWLINE          = "NEWLINE"
TT_EOF              = "EOF"
TT_TRUE             = "TRUE"
TT_FALSE            = "FALSE"

KEYWORDS = [
    "def",
    "return",
    "if",
    "elif",
    "else",
    "for",
    "while",
    "print",
    "or",
    "and",
    "not",
    "true",
    "false"
]
LOG_OPERATORS = [
    "or",
    "and",
    "not"
]
COMP_OPERATORS = [
    "==",
    "!=",
    ">",
    ">=",
    "<",
    "<="
]

class Token:
    def __init__(self, type, value=None, pos_start=None, pos_end=None):
        self.type = type
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
        if pos_end:
            self.pos_end = pos_end.copy()
        # If pos_end not given assume its pos_start + 1
        else:
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
    
    def __repr__(self):
        if self.value:
            return f"{self.type}:{self.value}"
        return f"{self.type}"
    
############################################
# LEXER
############################################

class Lexer:
    def __init__(self, filename, text):
        self.filename = filename
        self.text = text
        self.pos = Position(-1, 0, -1, filename, text)
        self.current_char = None
        self.advance()

    # Advance to next letter
    def advance(self):
        self.pos.advance(self.current_char)
        if self.pos.index < len(self.text):
            self.current_char = self.text[self.pos.index]
        else:
            self.current_char = None
    
    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            # If current character is whitespace, ignore
            if self.current_char in " \t":
                self.advance()
            elif self.current_char == "\n":
                tokens.append(Token(TT_NEWLINE, pos_start=self.pos))
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())

            elif any(self.current_char in c for c in COMP_OPERATORS):
                tokens.append(self.make_operator())

            elif self.current_char == '"' or self.current_char == "'":
                tokens.append(self.make_string())

            elif self.current_char == "+":
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == "-":
                tokens.append(Token(TT_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == "*":
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == "/":
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == "(":
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ")":
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == "[":
                tokens.append(Token(TT_LSQUARE, pos_start=self.pos))
                self.advance()
            elif self.current_char == "]":
                tokens.append(Token(TT_RSQUARE, pos_start=self.pos))
                self.advance()
            elif self.current_char == "{":
                tokens.append(Token(TT_LBRACK, pos_start=self.pos))
                self.advance()
            elif self.current_char == "}":
                tokens.append(Token(TT_RBRACK, pos_start=self.pos))
                self.advance()
            elif self.current_char == ",":
                tokens.append(Token(TT_COMMA, pos_start=self.pos))
                self.advance()
            elif self.current_char == "^":
                tokens.append(Token(TT_POWEROP, pos_start=self.pos))
                self.advance()
            # If character is illegal return error
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                raise IllegalCharError(pos_start, self.pos, '"' + char + '"')
        tokens.append(Token(TT_EOF, pos_start=self.pos))

        return tokens

    def make_string(self):
        string = ""
        quote = self.current_char
        pos_start = self.pos.copy()
        self.advance()

        if quote == '"':
            while self.current_char != '"' and self.current_char != None:
                string += self.current_char
                self.advance()
        elif quote == "'":
            while self.current_char != "'" and self.current_char != None:
                string += self.current_char
                self.advance()
        
        # Reached end of file without finding the closing quote
        if self.current_char != quote:
            raise SyntaxError(pos_start, self.pos, "Missing/wrong quote")
        
        self.advance()
        return Token(TT_STRING, string, pos_start, self.pos)
    
    # Return a TT_INT or TT_FLOAT Token based on if theres a dot in number
    def make_number(self):
        num_str = ""
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + ".":
            if self.current_char == ".":
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += "."
            else:
                num_str += self.current_char

            self.advance()
        
        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)
    
    # Return an IDENTIFIER Token, KEYWORD Token or LOG_OPERATOR Token
    def make_identifier(self):
        identifier = ""
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in LETTERS:
            identifier += self.current_char
            self.advance()

        token_type = TT_IDENTIFIER
        if identifier in KEYWORDS:
            token_type = TT_KEYWORD
            if identifier in LOG_OPERATORS:
                token_type = TT_LOG_OPERATOR

        return Token(token_type, identifier, pos_start, self.pos)
    
    # Return EQUAL Token or COMP_OPERATOR Token
    def make_operator(self):
        operator = ""
        pos_start = self.pos.copy()

        while self.current_char != None and any(self.current_char in c for c in COMP_OPERATORS):
            operator += self.current_char
            self.advance()
        # If operator is a single "=" return an equals Token
        if operator == "=":
            return Token(TT_EQUALS, pos_start=self.pos)
        elif operator in COMP_OPERATORS:
            return Token(TT_COMP_OPERATOR, operator, pos_start, self.pos)
        else:
            raise IllegalCharError(pos_start, self.pos, '"' + operator + '"')
        