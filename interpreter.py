import sys
from errors import RTError
from token_ import *
from ast import *

# ---------------------------------------------

class Value(object):
    def __init__(self):
        self.set_pos()
        self.set_context()
    
    def set_pos(self, position_start=None, position_end=None):
        self.position_start = position_start
        self.position_end = position_end
        return self
    
    def set_context(self, context=None):
        self.context = context
        return self
    
    def add(self, other):
        return None, RTError('Illegal Operation', self.position_start, other.position_end, self.context)
    
    def sub(self, other):
        return None, RTError('Illegal Operation', self.position_start, other.position_end, self.context)
    
    def mul(self, other):
        return None, RTError('Illegal Operation', self.position_start, other.position_end, self.context)
    
    def div(self, other):
        return None, RTError('Illegal Operation', self.position_start, other.position_end, self.context)
    
    def lt(self, other):
        return None, RTError('Illegal Operation', self.position_start, other.position_end, self.context)
    
    def gt(self, other):
        return None, RTError('Illegal Operation', self.position_start, other.position_end, self.context)
    
    def lt_or_eq(self, other):
        return None, RTError('Illegal Operation', self.position_start, other.position_end, self.context)

    def gt_or_eq(self, other):
        return None, RTError('Illegal Operation', self.position_start, other.position_end, self.context)

    def unary(self, tok):
        return None, RTError('Illegal Operation', tok.position_start, self.position_end, self.context)

    def execute(self, args):
        return None, RTError('Illegal Operation', args.position_start, args.position_end, self.context)

    def is_true(self, args):
        return None, RTError('Illegal Operation', args.position_start, args.position_end, self.context)

    def to_string(self, args):
        return None, RTError('Illegal Operation', args.position_start, args.position_end, self.context)

    def to_int(self, args):
        return None, RTError('Illegal Operation', args.position_start, args.position_end, self.context)

    def to_float(self, args):
        return None, RTError('Illegal Operation', args.position_start, args.position_end, self.context)

    def repr(self):
        return None, RTError('Illegal Operation', self.position_start, self.position_end, self.context)

class Number(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
    
    def add(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, RTError('Illegal Operation', self.position_start, other.position_end, self.context)
    
    def sub(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, RTError('Illegal Operation', self.position_start, other.position_end, self.context)
    
    def mul(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, RTError('Illegal Operation', self.position_start, other.position_end, self.context)
    
    def div(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError("Division by 0", self.position_start, other.position_end, self.context)
            return Number(self.value / other.value).set_context(self.context), None
        else:
            return None, RTError('Illegal Operation', self.position_start, other.position_end, self.context)

    def lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None
        else:
            return None, RTError('Illegal Operation', self.position_start, other.position_end, self.context)
    
    def gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None
        else:
            return None, RTError('Illegal Operation', self.position_start, other.position_end, self.context)
    
    def lt_or_eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None
        else:
            return None, RTError('Illegal Operation', self.position_start, other.position_end, self.context)
    
    def gt_or_eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None
        else:
            return None, RTError('Illegal Operation', self.position_start, other.position_end, self.context)
    
    def eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else:
            return None, RTError('Illegal Operation', self.position_start, other.position_end, self.context)

    def unary(self, tok):
        if tok.type == MINUS:
            return Number(-self.value).set_context(self.context), None
        else:
            return None, RTError(f"Unsupported unary operation for {tok.type}", tok.position_start, tok.position_end, self.context)

    def is_true(self):
        if self.value == 0:
            return Number(0).set_context(self.context)
        else:
            return Number(1).set_context(self.context)

    def repr(self):
        return self.value

class Function(Value):
    def __init__(self, name, arg_names, code_node):
        self.name = name
        self.arg_names = arg_names
        self.code_node = code_node
    
    def execute(self, args):
        args, error = self.check_and_populate_args(args)
        if error:
            return None, error
        interpreter = Interpreter()

        exec_ctx = Context(self.name, parent=self.context, parent_start_pos=self.position_start)
        for key, value in args.items():
            exec_ctx.symbol_table.symbols[key] = value

        stmts, error = interpreter.visit(self.code_node, exec_ctx)
        if error:
            return None, error
        
        for key in exec_ctx.symbol_table.symbols.keys():
            if key in self.context.symbol_table.symbols.keys():
                self.context.symbol_table.symbols[key] = exec_ctx.symbol_table.symbols[key]
        
        return interpreter.return_value, None

    def check_and_populate_args(self, arg_values):
        if len(arg_values) != len(self.arg_names):
            return None, RTError(f"Method takes only {str(len(self.arg_names))}, {str(len(arg_values))} were given.", self.position_start, self.position_end, self.context)
        args = {} 
        for i in range(len(arg_values)):
            args[self.arg_names[i]] = arg_values[i]
        
        return args, None

    def repr(self):
        return f"FUNCTION {self.name}"
    
class BuiltInFunction(Value):
    def __init__(self, name, arg_names):
        self.name = name
        self.arg_names = arg_names

    def write(self, arg_values):
        args, error = self.check_and_populate_args(self.arg_names, arg_values)
        if error:
            return None, error
    
        sys.stdout.write(str(args["text"].repr()))
        return NoneType(), None
    
    def execute(self, arg_values):
        func = getattr(self, self.name, None)
        return_value, error = func(arg_values)
        if error:
            return None, error
        return return_value, None
    
    def check_and_populate_args(self, arg_names, arg_values):
        if len(arg_values) != len(arg_names):
            return None, RTError(f"Method takes only {str(len(arg_names))}, {str(len(arg_values))} were given.", self.position_start, self.position_end, self.context)
        args = {} 
        for i in range(len(arg_values)):
            args[arg_names[i]] = arg_values[i]
        
        return args, None

class NoneType(Value):
    def repr(self):
        return "none"

# ---------------------------------------------

global_vars = {
    "true": Number(1),
    "false": Number(0),
    "none": NoneType(),
    "write": BuiltInFunction("write", ["text"]),
}

# ---------------------------------------------

class Context:
    def __init__(self, name, parent=None, parent_start_pos=None):
        self.name = name
        self.parent = parent
        self.parent_start_pos = parent_start_pos
        self.symbol_table = SymbolTable()
    
    def make_main_symbol_table(self):
        base_symbols = {}
        base_symbols.update(global_vars)
        self.symbol_table.symbols = base_symbols

class SymbolTable(object):
    def __init__(self):
        self.symbols = {}
    
    def get(self, name):
        if name in self.symbols.keys():
            return self.symbols[name], True
        else:
            return None, False
    
    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]

class Interpreter(object):
    return_value = NoneType()
       
    def visit(self, node, context):
        func = getattr(self, "visit_" + type(node).__name__, self.no_visit_method)
        value, error = func(node, context)
        return value, error
    
    def no_visit_method(self, node, context):
        raise NotImplementedError(f"No visit method for {type(node).__name__}")

    def visit_Program(self, node, context):
        res = []
        for stmt in node.statements:
            value, error = self.visit(stmt, context)
            if error:
                return None, error
            if not isinstance(self.return_value, NoneType):
                break
            res.append(value.repr())
        return res, None

    def visit_Block(self, node, context):
        res = []
        for stmt in node.statements:
            value, error = self.visit(stmt, context)
            if error:
                return None, error
            if not isinstance(self.return_value, NoneType):
                break
            res.append(value.repr())
        return res, None
    
    def visit_NumberNode(self, node, context):
        if str(int(node.tok.value)) == node.tok.value:
            return Number(int(node.tok.value)).set_context(context).set_pos(node.position_start, node.position_end), None
        return Number(float(node.tok.value)).set_context(context).set_pos(node.position_start, node.position_end), None
    
    def visit_IdentifierNode(self, node, context):
        value, ok = context.symbol_table.get(node.tok.value)
        if not ok:
            return None, RTError(f"Name {node.tok.value} does not exist", node.position_start, node.position_end, context)
        return value, None

    def visit_UnaryOperationNode(self, node, context):
        value, _ = self.visit(node.node, context)
        return value.unary(node.operation_tok)          
    
    def visit_BinaryOperationNode(self, node, context):
        left, error = self.visit(node.left_node, context)
        if error:
            return None, error
        right, error = self.visit(node.right_node, context)
        if error:
            return None, error
        op_tok = node.operation_tok
        if op_tok.type == PLUS:
            result, error = left.add(right)
        elif op_tok.type == MINUS:
            result, error = left.sub(right)
        elif op_tok.type == ASTERISK:
            result, error = left.mul(right)
        elif op_tok.type == SLASH:
            result, error = left.div(right)
        elif op_tok.type == LESS_THAN:
            result, error = left.lt(right)
        elif op_tok.type == GREATER_THAN:
            result, error = left.gt(right)
        elif op_tok.type == LESS_THAN_OR_EQUAL:
            result, error = left.lt_or_eq(right)
        elif op_tok.type == GREATER_THAN_OR_EQUAL:
            result, error = left.gt_or_eq(right)
        elif op_tok.type == DOUBLE_EQUAL:
            result, error = left.eq(right)
        
        if error:
            return None, error
        return result.set_pos(node.position_start, node.position_end), None
    
    def visit_VarAssignNode(self, node, context):
        value, error = self.visit(node.var_value, context)
        if error:
            return None, error
        context.symbol_table.set(node.var_name.tok.value, value)
        return NoneType(), None

    def visit_FunctionNode(self, node, context):
        name = "anonymous" or node.name.tok.value
        arg_names = []
        if isinstance(node, SetNode):
            for arg in node.arg_node.elements:
                arg_names.append(arg.tok.value)
        elif isinstance(node.arg_node, IdentifierNode):
            arg_names.append(node.arg_node.tok.value)
        else:
            return None, RTError("Function argument must be an identifier", node.arg_node.position_start, node.arg_node.position_end, context)
        function = Function(name, arg_names, node.code_block).set_context(context).set_pos(node.position_start, node.position_end)
        
        if name != "anonymous":
            context.symbol_table.set(name, function)
        return function, None

    def visit_CallNode(self, node, context):
        value, error = self.visit(node.operand, context)
        if error:
            return None, error
        value = value.set_pos(node.position_start, node.position_end)
        args = []
        for arg in node.arg_node.args:
            v, error = self.visit(arg, context)
            if error:
                return None, error
            args.append(v)
        
        return_value, error = value.execute(args)
        if error:
            return None, error

        return return_value, None
    
    def visit_ReturnNode(self, node, context):
        value, error = self.visit(node.return_value, context)
        if error:
            return None, error
        
        self.return_value = value
        return self.return_value, None

    def visit_IfNode(self, node, context):
        if_condition, error = self.visit(node.if_condition, context)
        if error:
            return None, error

        if if_condition.value == 0:
            if node.elif_conditions:
                for i in range(len(node.elif_conditions)):
                    elif_condition, error = self.visit(node.elif_conditions[i], context)
                    if error:
                        return None, error
                    if not elif_condition.value == 0:
                        res, error = self.visit(node.if_block_statements[i], context)
                        if error:
                            return None, error
            if node.else_block_statement:
                res, error = self.visit(node.else_block_statement, context)
                if error:
                    return None, error
        else:
            res, error = self.visit(node.if_block_statement, context)
            if error:
                return None, error

        return NoneType(), None
