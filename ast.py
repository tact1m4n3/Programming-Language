class Program:
    def __init__(self):
        self.statements = []

    def __repr__(self):
        string = ""
        for statement in self.statements:
            string += f" [ {statement} ] "
        return string

class Block:
    def __init__(self):
        self.statements = []

    def __repr__(self):
        string = ""
        for statement in self.statements:
            string += f" [ {statement} ] "
        return string

class ConstAssignNode:
    def __init__(self, const_name, const_value, position_start, position_end):
        self.const_name = const_name
        self.const_value = const_value

    def __repr__(self):
        return f"( LET {self.const_name} = {self.const_value} )"

class VarAssignNode:
    def __init__(self, var_name, var_value, position_start, position_end):
        self.var_name = var_name
        self.var_value = var_value
    
    def __repr__(self):
        return f"( VAR {self.var_name} = {self.var_value} )"

class ReturnNode:
    def __init__(self, return_value, position_start, position_end):
        self.return_value = return_value

    def get_c_code(self):
        return f"return {self.return_value};"

    def __repr__(self):
        return f"( RETURN {self.return_value} )"

class NumberNode:
    def __init__(self, tok, position_start, position_end):
        self.tok = tok
        self.position_start = position_start
        self.position_end = position_end

    def get_c_code(self):
        return f"{self.tok.value}"

    def __repr__(self):
        return f"{self.tok}"

class StringNode:
    def __init__(self, tok, position_start, position_end):
        self.tok = tok
        self.position_start = position_start
        self.position_end = position_end

    def __repr__(self):
        return f"{self.tok}"

class IdentifierNode:
    def __init__(self, tok, position_start, position_end):
        self.tok = tok
        self.position_start = position_start
        self.position_end = position_end

    def __repr__(self):
        return f"{self.tok}"

class ListNode:
    def __init__(self, elements, position_start, position_end):
        self.elements = elements
        self.position_start = position_start
        self.position_end = position_end
    
    def __repr__(self):
        return f"{self.elements}"

class SetNode:
    def __init__(self, elements, position_start, position_end):
        self.elements = elements
        self.position_start = position_start
        self.position_end = position_end
    
    def __repr__(self):
        return f"{self.elements}"

class BinaryOperationNode:
    def __init__(self, left_node, operation_tok, right_node, position_start, position_end):
        self.left_node = left_node
        self.operation_tok = operation_tok
        self.right_node = right_node

        self.position_start = position_start
        self.position_end = position_end

    def __repr__(self):
        return f"({self.left_node} {self.operation_tok} {self.right_node})"


class UnaryOperationNode:
    def __init__(self, operation_tok, node, position_start, position_end):
        self.operation_tok = operation_tok
        self.node = node

        self.position_start = position_start
        self.position_end = position_end

    def __repr__(self):
        return f"({self.operation_tok} {self.node})"

class IfNode:
    def __init__(self, if_condition, if_block_statement, elif_conditions=None, elif_block_statements=None, else_block_statements=None, position_start=None, position_end=None):
        self.if_condition = if_condition
        self.if_block_statement = if_block_statement
        self.elif_conditions = elif_conditions
        self.elif_block_statements = elif_block_statements
        self.else_block_statement = else_block_statements

        self.position_start = position_start
        self.position_end = position_end

    def __repr__(self):
        string = f"( IF {self.if_condition} DO {self.if_block_statement} "
        if self.elif_conditions:
            for i in range(len(self.elif_conditions)):
                string += f"ELIF {self.elif_conditions[i]} DO {self.elif_block_statements[i]} "
        if self.else_block_statement:
            string += f"ELSE {self.else_block_statement} "

        string += ')'
        return string

class ArgNode:
    def __init__(self, args, position_start, position_end):
        self.args = args

        self.position_start = position_start
        self.position_end = position_end
    
    def __repr__(self):
        return f"{self.args}"

class FunctionNode:
    def __init__(self, name, arg_node, code_block, position_start, position_end):
        self.name = name
        self.arg_node = arg_node
        self.code_block = code_block

        self.position_start = position_start
        self.position_end = position_end
    def __repr__(self):
        return f"( FUNCTION {self.name} ( {self.arg_node} ) CODE {self.code_block} )"

class CallNode:
    def __init__(self, operand, arg_node, position_start, position_end):
        self.operand = operand
        self.arg_node = arg_node

        self.position_start = position_start
        self.position_end = position_end

    def __repr__(self):
        string = f"( {self.operand}( {self.arg_node} )"

        return string

class IndexNode:
    def __init__(self, operand, index_expr, position_start, position_end):
        self.operand = operand
        self.index_expr = index_expr
        self.position_start = position_start
        self.position_end = position_end

    def __repr__(self):
        return f"( {self.operand} [ {self.index_expr} ] )"

