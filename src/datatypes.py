from errors import *

############################################
# Datatypes
############################################

class TypeTemplate:
    def __init__(self):
        self.set_pos()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def addition(self, other):
        return self.unsupported_operation(other)
    
    def subtraction(self, other):
        return self.unsupported_operation(other)
    
    def multiplication(self, other):
        return self.unsupported_operation(other)

    def division(self, other):
        return self.unsupported_operation(other)

    def power_by(self, other):
        return self.unsupported_operation(other)

    def compare(self, comp_op, other):
        # Only values of the same type can be compared, e.g. not 1 < "a"
        if type(self) != type(other) or isinstance(self, List):
            return self.unsupported_operation(other)

        if comp_op == ">":
            return Boolean(self.value > other.value)
        elif comp_op == "<":
            return Boolean(self.value < other.value)
        elif comp_op == "==":
            return Boolean(self.value == other.value)
        elif comp_op == "!=":
            return Boolean(self.value != other.value)
        elif comp_op == ">=":
            return Boolean(self.value >= other.value)
        elif comp_op == "<=":
            return Boolean(self.value <= other.value)

    def unsupported_operation(self, other):
        raise RTError(
                    self.pos_start,
                    self.pos_end, "Unsupported operation")

    def __repr__(self):
        return str(self.value)

################################################

class Number(TypeTemplate):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def addition(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value)
        else:
            return self.unsupported_operation(other)
        
    def subtraction(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value)
        else:
            return self.unsupported_operation(other)
        
    def multiplication(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value)
        else:
            return self.unsupported_operation(other)
        
    def division(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                raise RTError(
                    self.pos_start,
                    self.pos_end,
                    "Division By Zero")
            else:    
                return Number(self.value / other.value)
        else:
            return self.unsupported_operation(other)

    def power_by(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value)
        else:
            return self.unsupported_operation(other)
    
############################################

class String(TypeTemplate):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def addition(self, other):
        if not isinstance(other, String):
            return self.unsupported_operation(other)
        return String(self.value + other.value)
        
    def multiplication(self, other):
        if not isinstance(other, Number):
            return self.unsupported_operation(other)
        return String(self.value * other.value)

############################################

class Boolean(TypeTemplate):
    def __init__(self, value):
        super().__init__()
        if value == "true":
            self.value = True
        elif value == "false":
            self.value = False
        else:
            self.value = value

    def logic(self, logic, other):
        if logic == "not":
            return Boolean(True if other.value == False else False)
        elif logic == "or":
            return Boolean(self.value or other.value)
        elif logic == "and":
            return Boolean(self.value and other.value)

    def __repr__(self):
        return "true" if self.value == True else "false"
    
############################################

class List(TypeTemplate):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements
    
    def __repr__(self):
        return f"[{', '.join([repr(x) for x in self.elements])}]"