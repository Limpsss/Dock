############################################
# NODES
############################################

class ProgramNode:
    def __init__(self, program_list, pos_start, pos_end):
        self.program_list = program_list

        self.pos_start = pos_start
        self.pos_end = pos_end

class FuncDeclareNode:
    def __init__(self, func_id, code_block, parameters):
        self.func_id = func_id
        self.code_block = code_block
        self.parameters = parameters

        self.pos_start = self.func_id.pos_start
        self.pos_end = self.code_block.pos_end

class FuncAccessNode:
    def __init__(self, func_id, args):
        self.func_id = func_id
        self.args = args

        self.pos_start = self.func_id.pos_start
        self.pos_end = self.func_id.pos_end

class ReturnNode:
    def __init__(self, expr):
        self.expr = expr

        self.pos_start = self.expr.pos_start
        self.pos_end = self.expr.pos_end

class WhileLoopNode:
    def __init__(self, condition, code_block):
        self.condition = condition
        self.code_block = code_block

        self.pos_start = self.condition.pos_start
        self.pos_end = self.code_block.pos_end

class ForLoopNode:
    def __init__(self, iterator, iterable, code_block):
        self.iterator = iterator
        self.iterable = iterable
        self.code_block = code_block

        self.pos_start = self.iterator.pos_start
        self.pos_end = self.code_block.pos_end

class IfStmtNode:
    def __init__(self, ifs):
        # ifs = list with tuples:
        # [("if", condition, code_block), ("elif", condition, code_block), ("else", code_block)]
        self.ifs = ifs

        self.pos_start = self.ifs[0][1].pos_start
        self.pos_end = self.ifs[-1][1].pos_end

class PrintStmtNode:
    def __init__(self, expr):
        self.expr = expr
        
        self.pos_start = self.expr.pos_start
        self.pos_end = self.expr.pos_end

class VariableAssignNode:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        
        self.pos_start = self.name.pos_start
        self.pos_end = self.value.pos_end

class VariableAccessNode:
    def __init__(self, name):
        self.name = name

        self.pos_start = self.name.pos_start
        self.pos_end = self.name.pos_end

class ListNode:
    def __init__(self, element_list, pos_start, pos_end):
        self.element_list = element_list

        self.pos_start = pos_start
        self.pos_end = pos_end

class StringNode:
    def __init__(self, token):
        self.token = token

        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end
        
    def __repr__(self):
        return f"{self.token}"

class NumberNode:
    def __init__(self, token):
        self.token = token
    
        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end
        
    def __repr__(self):
        return f"{self.token}"
    
class BooleanNode:
    def __init__(self, token):
        self.token = token
    
        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end
        
    def __repr__(self):
        return f"{self.token}"
    
class BinaryOpNode:
    def __init__(self, left_node, op_token, right_node):
        self.left_node = left_node
        self.op_token = op_token
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end
    
class UnaryOpNode:
    def __init__(self, op_token, node):
        self.op_token = op_token
        self.node = node

        self.pos_start = self.op_token.pos_start
        self.pos_end = self.node.pos_end
     
    def __repr__(self):
        return f"({self.op_token}, {self.node})"
