############################################
# IMPORTS
############################################

from lexer import *
from nodes import *
from errors import *

############################################
# PARSER
############################################

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_index = -1
        self.advance()

    def advance(self, reverse=""):
        if reverse == "reverse":
            self.token_index -= 1
        else:
            self.token_index += 1

        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        return self.current_token

    def parse(self):
        program = self.program()

        # Haven't reached end of file means code still
        # left to be parsed which means there is a syntax error
        if self.current_token.type != TT_EOF:
            raise SyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,
                "Parse error")
        return program

############################################

    # Raise a syntax error if the current token is not of the expected type
    def check(self, expected_type, error_message):
        token = self.current_token
        if token.type != expected_type:
            raise SyntaxError(token.pos_start, token.pos_end, error_message)
        return token

    # Same as check but also moves past the token
    def expect(self, expected_type, error_message):
        token = self.check(expected_type, error_message)
        self.advance()
        return token

    def skip_newlines(self):
        while self.current_token.type == TT_NEWLINE:
            self.advance()

############################################

    def program(self):
        pos_start = self.current_token.pos_start.copy()
        program_list = []

        while self.current_token.type != TT_EOF:
            program_list.append(self.stmt_list())

        return ProgramNode(program_list, pos_start, self.current_token.pos_start.copy())

    def stmt_list(self):
        statement_list = []
        pos_start = self.current_token.pos_start.copy()

        self.skip_newlines()

        # Append first statement
        statement_list.append(self.stmt())

        # Check if there are more statements and append them
        while True:
            newline = 0
            while self.current_token.type == TT_NEWLINE:
                self.advance()
                newline += 1
            if newline == 0:
                break
            if self.current_token.type in (TT_RBRACK, TT_EOF):
                break

            statement_list.append(self.stmt())

        # Add more statements if there are more after first loop
        while self.current_token.type != TT_RBRACK and self.current_token.type != TT_EOF:
            statement_list.append(self.stmt())
            self.skip_newlines()

        return ListNode(statement_list, pos_start, self.current_token.pos_start.copy())

    def stmt(self):
        if self.current_token.type == TT_KEYWORD and self.current_token.value == "def":
            return self.func_declare()
        elif self.current_token.type == TT_KEYWORD and self.current_token.value == "for":
            return self.for_loop()
        elif self.current_token.type == TT_KEYWORD and self.current_token.value == "while":
            return self.while_loop()
        elif self.current_token.type == TT_KEYWORD and self.current_token.value == "if":
            return self.if_stmt()
        elif self.current_token.type == TT_KEYWORD and self.current_token.value == "print":
            return self.print_stmt()
        elif self.current_token.type == TT_IDENTIFIER:
            return self.assign()
        else:
            return self.expr()

    def func_declare(self):
        parameters = []
        self.advance()

        func_id = self.expect(TT_IDENTIFIER, "Expected 'identifier'")
        self.expect(TT_LPAREN, "Expected '('")

        # Parameters are optional identifiers, seperated by a comma ","
        if self.current_token.type != TT_RPAREN:
            parameters.append(self.expect(TT_IDENTIFIER, "Expected parameter name"))
            while self.current_token.type == TT_COMMA:
                self.advance()
                parameters.append(self.expect(TT_IDENTIFIER, "Expected parameter name"))

        self.expect(TT_RPAREN, "Expected ')'")
        code_block = self.code_block()

        return FuncDeclareNode(func_id, code_block, parameters)

    def func_call(self, id_token):
        args = []
        self.expect(TT_LPAREN, "Expected '('")

        # Arguments are optional, seperated by a comma ","
        if self.current_token.type != TT_RPAREN:
            args.append(self.expr())
            while self.current_token.type == TT_COMMA:
                self.advance()
                args.append(self.expr())

        self.expect(TT_RPAREN, "Expected ')'")

        return FuncAccessNode(id_token, args)

    def code_block(self):
        self.skip_newlines()
        self.expect(TT_LBRACK, "Expected '{'")

        # Expressions that should evaluate
        statements = self.stmt_list()

        self.expect(TT_RBRACK, "Expected '}'")
        self.skip_newlines()

        return statements

    # A condition inside parentheses, used by while, if and print
    def paren_expr(self):
        self.expect(TT_LPAREN, "Expected '('")
        expr = self.expr()
        self.expect(TT_RPAREN, "Expected ')'")
        return expr

    def while_loop(self):
        self.advance()

        # The while-condition, should be a boolean value
        condition = self.paren_expr()

        # The code that will evaluate if the condition is true
        code_block = self.code_block()
        return WhileLoopNode(condition, code_block)

    def for_loop(self):
        self.advance()

        # For-loop must begin with parenthesis
        self.expect(TT_LPAREN, "Expected '('")

        # First you have to assign an iterator variable
        self.check(TT_IDENTIFIER, "Expected 'assignment'")
        iterator = self.assign()

        # After an iterator, seperated by a comma ",", you declare the iterable (number, string or list)
        self.expect(TT_COMMA, "Expected ','")
        iterable = self.expr()

        # For-loop must end with parenthesis
        self.expect(TT_RPAREN, "Expected ')'")
        code_block = self.code_block()

        return ForLoopNode(iterator, iterable, code_block)


    def if_stmt(self, ifs=None):
        # ifs is shared between the if, elif and else parts of the same statement
        if ifs is None:
            ifs = []

        # Save if, elif or else as a string
        name = self.current_token.value
        self.advance()

        if name == "else":
            ifs.append((name, self.code_block()))
            return IfStmtNode(ifs)

        # The if-condition, should be true or false
        condition = self.paren_expr()

        # The code that will evaluate if the condition is true
        code_block = self.code_block()
        ifs.append((name, condition, code_block))

        if self.current_token.value in ("elif", "else"):
            self.if_stmt(ifs)

        return IfStmtNode(ifs)


    def print_stmt(self):
        self.advance()

        # Expression that will be printed
        expr = self.paren_expr()
        return PrintStmtNode(expr)


    def assign(self):
        var_name = self.current_token
        self.advance()

        # If next token is not "=" reverse the parser to get previous token
        # and branch down the recursive functions to get the value of the identifier
        if self.current_token.type != TT_EQUALS:
            self.advance("reverse")
            return self.expr()

        # Next token should be the indentifiers value:
        self.advance()
        # Traverse the AST to get the value of the variable
        var_value = self.stmt()
        return VariableAssignNode(var_name, var_value)

    def list(self):
        element_list = []
        pos_start = self.current_token.pos_start.copy()
        self.advance()

        # If next token after "[" is == "]" then it's an empty list
        # If not then append every expression node to element_list that is seperated by a comma
        if self.current_token.type != TT_RSQUARE:
            element_list.append(self.expr())
            while self.current_token.type == TT_COMMA:
                self.advance()
                element_list.append(self.expr())

        self.expect(TT_RSQUARE, "Expected ']'")

        return ListNode(element_list, pos_start, self.current_token.pos_end.copy())

    def expr(self):
        return self.logic()

    def logic(self):
        return self.binary_op(self.compare, (TT_LOG_OPERATOR, ))

    def compare(self):
        if self.current_token.value == "not":
            token = self.current_token
            self.advance()
            return UnaryOpNode(token, self.compare())

        return self.binary_op(self.arith_expr, (TT_COMP_OPERATOR, ))

    def arith_expr(self):
        return self.binary_op(self.term, (TT_PLUS, TT_MINUS))

    def term(self):
        return self.binary_op(self.factor, (TT_MUL, TT_DIV))

    def factor(self):
        token = self.current_token
        # Unary operation
        if token.type in (TT_PLUS, TT_MINUS):
            self.advance()
            return UnaryOpNode(token, self.factor())

        return self.power()

    # Power operator "^"
    def power(self):
        return self.binary_op(self.atom, (TT_POWEROP, ))

    def atom(self):
        token = self.current_token

        if token.type in (TT_INT, TT_FLOAT):
            self.advance()
            return NumberNode(token)

        elif token.type == TT_STRING:
            self.advance()
            return StringNode(token)

        elif token.type == TT_LSQUARE:
            return self.list()

        elif token.type == TT_IDENTIFIER:
            self.advance()
            if self.current_token.type == TT_LPAREN:
                return self.func_call(token)
            return VariableAccessNode(token)

        elif token.type == TT_KEYWORD and token.value in ("true", "false"):
            self.advance()
            return BooleanNode(token)

        elif token.type == TT_KEYWORD and token.value == "return":
            self.advance()
            return ReturnNode(self.expr())

        # Paranthesis, highest priority
        elif token.type == TT_LPAREN:
            return self.paren_expr()

        raise SyntaxError(token.pos_start, token.pos_end, f"Unexpected {token}")

############################################

    def binary_op(self, func, ops):
        left = func()

        while self.current_token.type in ops:
            op_token = self.current_token
            self.advance()
            right = func()
            left = BinaryOpNode(left, op_token, right)

        return left
