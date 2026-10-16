from parserDock import *
from datatypes import *

############################################
# INTERPRETER
############################################

# Raised by a return statement and caught by the function call,
# which lets return work from anywhere inside a function body
class ReturnSignal(Exception):
    def __init__(self, node, value):
        super().__init__()
        self.node = node
        self.value = value

class Interpreter:
    def visit(self, node, scope):
        # Creates visit_ string based on what node it is
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, scope)

    def no_visit_method(self, node, scope):
        raise Exception(f"visit_{type(node).__name__} method missing")

############################################

    def visit_ProgramNode(self, node, scope):
        elements = []

        for list in node.program_list:
            elements.append(self.visit(list, scope))

        return List(elements).set_pos(node.pos_start, node.pos_end)

    def visit_FuncDeclareNode(self, node, scope):
        func_id = node.func_id.value
        scope.set(func_id, (node.parameters, node.code_block), func=True)
        return node.code_block

    def visit_FuncAccessNode(self, node, scope):
        func_id = node.func_id.value
        func = scope.get(func_id, func=True)

        if func is None:
            raise RTError(
                node.pos_start,
                node.pos_end,
                f'"{func_id}" has not been defined')

        params, func_body = func
        arguments = [self.visit(arg, scope) for arg in node.args]

        if len(arguments) != len(params):
            raise RTError(
                node.pos_start,
                node.pos_end,
                f"Expected {len(params)} arguments, {len(arguments)} were given")

        # The function gets its own scope that can still see the variables
        # and functions of the scope it was called from
        func_scope = Scope(parent=scope)
        for param, arg in zip(params, arguments):
            func_scope.set(param.value, arg)

        # Execute the function block until it is done or hits a return
        try:
            self.visit(func_body, func_scope)
        except ReturnSignal as ret:
            return ret.value
        return None

    def visit_ReturnNode(self, node, scope):
        raise ReturnSignal(node, self.visit(node.expr, scope))

    def visit_WhileLoopNode(self, node, scope):
        while_loop_result = None

        # While the condition is true execute the code block
        while self.visit(node.condition, scope).value == True:
            while_loop_result = self.visit(node.code_block, scope)

        return while_loop_result

    def visit_ForLoopNode(self, node, scope):
        it_name = node.iterator.name.value

        iterator = self.visit(node.iterator, scope)
        iterable = self.visit(node.iterable, scope)

        for_loop_result = False

        # For-loop if its a number iterable
        if isinstance(iterable, Number):
            value = iterator.value
            while value < iterable.value:
                scope.set(it_name, Number(value))
                for_loop_result = self.visit(node.code_block, scope)
                value += 1

        # For-loop if its a list iterable
        elif isinstance(iterable, List):
            for elem in iterable.elements[iterator.value:]:
                scope.set(it_name, elem)
                for_loop_result = self.visit(node.code_block, scope)

        # For-loop if its a string iterable
        elif isinstance(iterable, String):
            for char in iterable.value[iterator.value:]:
                scope.set(it_name, String(char))
                for_loop_result = self.visit(node.code_block, scope)

        else:
            raise RTError(
                iterable.pos_start,
                iterable.pos_end,
                "Can only loop over a number, string or list")

        # Remove iterator variable from scope when finished
        scope.remove(it_name)
        return for_loop_result

    def visit_IfStmtNode(self, node, scope):
        for stmt in node.ifs:
            if stmt[0] == "else":
                return self.visit(stmt[1], scope)

            # If condition is true interpret the expr code
            condition = self.visit(stmt[1], scope)
            if condition.value == True:
                return self.visit(stmt[2], scope)

        return None

    def visit_PrintStmtNode(self, node, scope):
        expr = self.visit(node.expr, scope)
        print(expr)
        return expr

    def visit_VariableAssignNode(self, node, scope):
        var_name = node.name.value
        var_value = self.visit(node.value, scope)
        scope.set(var_name, var_value)
        return var_value

    def visit_VariableAccessNode(self, node, scope):
        var_name = node.name.value
        var_value = scope.get(var_name)

        if var_value is None:
            raise RTError(
                node.pos_start,
                node.pos_end,
                f'"{var_name}" has not been defined')
        return var_value

    def visit_NumberNode(self, node, scope):
        return Number(node.token.value).set_pos(node.pos_start, node.pos_end)

    def visit_ListNode(self, node, scope):
        elements = []

        for element in node.element_list:
            elements.append(self.visit(element, scope))
        return List(elements).set_pos(node.pos_start, node.pos_end)

    def visit_StringNode(self, node, scope):
        return String(node.token.value).set_pos(node.pos_start, node.pos_end)

    def visit_BooleanNode(self, node, scope):
        return Boolean(node.token.value).set_pos(node.pos_start, node.pos_end)

    def visit_BinaryOpNode(self, node, scope):
        left = self.visit(node.left_node, scope)
        right = self.visit(node.right_node, scope)

        # Calls different functions based on token type
        if node.op_token.type == TT_PLUS:
            res = left.addition(right)
        elif node.op_token.type == TT_MINUS:
            res = left.subtraction(right)
        elif node.op_token.type == TT_MUL:
            res = left.multiplication(right)
        elif node.op_token.type == TT_DIV:
            res = left.division(right)
        elif node.op_token.type == TT_POWEROP:
            res = left.power_by(right)
        elif node.op_token.type == TT_COMP_OPERATOR:
            res = left.compare(node.op_token.value, right)
        # If left and right side are boolean values call logic function
        # Else send error
        elif node.op_token.type == TT_LOG_OPERATOR:
            if not (isinstance(left, Boolean) and isinstance(right, Boolean)):
                raise RTError(node.pos_start, node.pos_end, "Expected Boolean values.")
            res = left.logic(node.op_token.value, right)

        return res.set_pos(node.pos_start, node.pos_end)

    def visit_UnaryOpNode(self, node, scope):
        number = self.visit(node.node, scope)

        if node.op_token.type == TT_MINUS:
            number = number.multiplication(Number(-1))

        if node.op_token.value == "not":
            if not isinstance(number, Boolean):
                raise RTError(number.pos_start, number.pos_end, "Expected Boolean value.")
            number = number.logic("not", number)

        return number


############################################
# SCOPE
############################################

class Scope:
    def __init__(self, parent=None):
        self.variables = {}
        # Function name -> (parameters, code block)
        self.functions = {}
        self.parent = parent

    # Look in this scope first, then in the scopes above it
    def get(self, name, func=False):
        table = self.functions if func else self.variables
        if name in table:
            return table[name]
        if self.parent:
            return self.parent.get(name, func)
        return None

    def set(self, name, value, func=False):
        if func:
            self.functions[name] = value
        else:
            self.variables[name] = value

    def remove(self, name):
        del self.variables[name]
