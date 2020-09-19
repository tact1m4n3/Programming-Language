from token_ import *

class Variable(object):
    def __init__(self, type, data, address):
        self.type = type
        self.data = data
        self.address = address

class Constant(object):
    def __init__(self, type, data, address):
        self.type = type
        self.data = data
        self.address = address

class Compiler(object):
    code = []

    variables = {}
    constants = {}

    last_variable_address = 0x2000
    last_constant_address = 0x3000
    
    def visit(self, node):
        func = getattr(self, "visit_" + type(node).__name__, self.no_visit_method)
        func(node)

    def no_visit_method(self, node):
        raise NotImplementedError(f"No visit method for {type(node).__name__}")
    
    def visit_Program(self, node):
        for stmt in node.statements:
            self.visit(stmt)

        self.add8bit(9)

    def visit_NumberNode(self, node):
        self.add8bit(3)
        self.add16bit(node.tok.value)

    def visit_IdentifierNode(self, node):
        pass
    
    def visit_StringNode(self, node):
        pass

    def visit_BinaryOperationNode(self, node):
        self.visit(node.left_node)
        self.visit(node.right_node)

        if node.operation_tok.type == PLUS:
            self.add8bit(5)
        elif node.operation_tok.type == MINUS:
            self.add8bit(6)
        elif node.operation_tok.type == ASTERISK:
            self.add8bit(7)
        elif node.operation_tok.type == SLASH:
            self.add8bit(8)

    def add8bit(self, value):
        self.code.append(str(value))

    def add16bit(self, value):
        self.code.append(str((value >> 8) & 0xff))
        self.code.append(str(value & 0xff))
