from token_ import *
from errors import InvalidSyntaxError
from ast import *


class ParserErrors:
    def __init__(self):
        self.errors = []

    def register_error(self, error):
        self.errors.append(error)


###################
# Parser
###################
class Parser(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = -1
        self.current_tok = None
        self.errors = ParserErrors()

        self.advance()

    def advance(self):
        self.index += 1
        self.current_tok = self.tokens[self.index] if self.index < len(self.tokens) else None

    def parse_program(self):
        program = Program()

        while self.current_tok.type is not EOF:
            stmt = self.parse_statement()

            if stmt:
                program.statements.append(stmt)

        return program

    def parse_statement(self):
        if self.current_tok.matches(KEYWORD, "let"):
            return self.parse_let_statement()
        elif self.current_tok.matches(KEYWORD, "var"):
            return self.parse_var_statement()
        elif self.current_tok.matches(KEYWORD, "return"):
            return self.parse_return_statement()
        elif self.current_tok.type in (INT, FLOAT, STRING, IDENTIFIER, PLUS, MINUS, LPAREN, LSQUAREBRACKET, KEYWORD):
            stmt = self.parse_expression_statement()
            return stmt
        else:
            self.errors.register_error(InvalidSyntaxError(
                "Expected INT, IDENTIFIER, '+', '-', '(', '['",
                self.current_tok.position_start,
                self.current_tok.position_end,
            ))
            self.advance()
            return None

    def parse_let_statement(self):
        position_start = self.current_tok.position_start
        if not self.current_tok.matches(KEYWORD, "let"):
            self.errors.register_error(InvalidSyntaxError(
                "Expected 'let'",
                self.current_tok.position_start,
                self.current_tok.position_end,
            ))
            return None

        self.advance()

        constant_name = self.factor()
        if not isinstance(constant_name, IdentifierNode):
            self.errors.register_error(InvalidSyntaxError(
                f"You can't assign a value to {constant_name}",
                self.current_tok.position_start,
                self.current_tok.position_end,
            ))
            return None

        if self.current_tok.type != EQUAL:
            self.errors.register_error(InvalidSyntaxError(
                "Expected '='",
                self.current_tok.position_start,
                self.current_tok.position_end,
            ))
            return None

        self.advance()
        constant_value = self.parse_math_expression()

        if self.current_tok.type != SEMICOLON:
            self.errors.register_error(InvalidSyntaxError(
                "Expected ';'",
                self.current_tok.position_start,
                self.current_tok.position_end,
            ))
            return None

        self.advance()
        return ConstAssignNode(constant_name, constant_value, position_start, self.current_tok.position_end)

    def parse_var_statement(self):
        position_start = self.current_tok.position_start
        if not self.current_tok.matches(KEYWORD, "var"):
            self.errors.register_error(InvalidSyntaxError(
                "Expected 'var'",
                self.current_tok.position_start,
                self.current_tok.position_end,
            ))
            return None
        
        self.advance()
        variable_name = self.factor()
        if not isinstance(variable_name, IdentifierNode):
            self.errors.register_error(InvalidSyntaxError(
                f"You can't assign a value to {variable_name}",
                self.current_tok.position_start,
                self.current_tok.position_end,
            ))
            return None

        if self.current_tok.type != EQUAL:
            self.errors.register_error(InvalidSyntaxError(
                "Expected '='",
                self.current_tok.position_start,
                self.current_tok.position_end,
            ))
            return None

        self.advance()
        variable_value = self.parse_math_expression()

        if self.current_tok.type != SEMICOLON:
            self.errors.register_error(InvalidSyntaxError(
                "Expected ';' or a new line",
                self.current_tok.position_start,
                self.current_tok.position_end,
            ))
            return None

        self.advance()
        return VarAssignNode(variable_name, variable_value, position_start, self.current_tok.position_end)

    def parse_return_statement(self):
        position_start = self.current_tok.position_start
        if not self.current_tok.matches(KEYWORD, "return"):
            self.errors.register_error(InvalidSyntaxError(
                "Expected 'return'",
                self.current_tok.position_start,
                self.current_tok.position_end,
            ))
            return None

        self.advance()

        return_value = self.parse_math_expression()

        if self.current_tok.type != SEMICOLON:
            self.errors.register_error(InvalidSyntaxError(
                "Expected ';'",
                self.current_tok.position_start,
                self.current_tok.position_end,
            ))
            return None

        self.advance()
        return ReturnNode(return_value, position_start, self.current_tok.position_end)

    def parse_expression_statement(self):
        if self.current_tok.matches(KEYWORD, "if"):
            stmt = self.parse_if_expression()
            return stmt
        elif self.current_tok.type in (INT, FLOAT, STRING, IDENTIFIER, PLUS, MINUS, LPAREN, LSQUAREBRACKET):
            stmt = self.parse_assign_expression()
            if self.current_tok.type != SEMICOLON:
                self.errors.register_error(InvalidSyntaxError(
                    "Expected ';'",
                    self.current_tok.position_start,
                    self.current_tok.position_end,
                ))
                return None
            self.advance()
            return stmt
        else:
            self.errors.register_error(InvalidSyntaxError(
                "Expected INT, IDENTIFIER, '+', '-', '(', '[', 'if'",
                self.current_tok.position_start,
                self.current_tok.position_end,
            ))
            return None

    def parse_if_expression(self):
        position_start = self.current_tok.position_start
        if not self.current_tok.matches(KEYWORD, "if"):
            self.errors.register_error(InvalidSyntaxError(
                "Expected 'if'",
                self.current_tok.position_start,
                self.current_tok.position_end,
            ))
            return None

        self.advance()

        if self.current_tok.type == EOF:
            self.errors.register_error(InvalidSyntaxError(
                    "Expected INT, IDENTIFIER, '+', '-', '(', ')', '[', ']'",
                    self.current_tok.position_start,
                    self.current_tok.position_end,
                ))
            return None

        if_condition = self.parse_math_expression()

        if_block = self.parse_block_statement()
        self.advance()

        if self.current_tok.matches(KEYWORD, "elif"):
            elif_conditions = []
            elif_blocks_statements = []

            while self.current_tok.matches(KEYWORD, "elif"):
                self.advance()
                if self.current_tok.type == EOF:
                    self.errors.register_error(InvalidSyntaxError(
                        "Expected INT, IDENTIFIER, '+', '-', '(', ')', '[', ']'",
                        self.current_tok.position_start,
                        self.current_tok.position_end,
                    ))
                    return None
                elif_condition = self.parse_math_expression()

                elif_block = self.parse_block_statement()

                self.advance()

                elif_conditions.append(elif_condition)
                elif_blocks_statements.append(elif_block)

            if self.current_tok.matches(KEYWORD, "else"):
                self.advance()

                else_block = self.parse_block_statement()
                self.advance()

                return IfNode(if_condition, if_block, elif_conditions, elif_blocks_statements, else_block, position_start=position_start, position_end=self.current_tok.position_end)
            else:
                return IfNode(if_condition, if_block, elif_conditions, elif_blocks_statements, position_start=position_start, position_end=self.current_tok.position_end)

        elif self.current_tok.matches(KEYWORD, "else"):
            self.advance()

            else_block = self.parse_block_statement()
            self.advance()

            return IfNode(if_condition, if_block, else_block_statements=else_block, position_start=position_start, position_end=self.current_tok.position_end)
        else:
            return IfNode(if_condition, if_block, position_start=position_start, position_end=self.current_tok.position_end)

    def parse_block_statement(self):
        if self.current_tok.type != LBRACKET:
            self.errors.register_error(InvalidSyntaxError(
                "Expected '{'",
                self.current_tok.position_start,
                self.current_tok.position_end,
            ))
            return None

        self.advance()
        block = Block()

        while self.current_tok.type != RBRACKET:
            if self.current_tok.type == EOF:
                self.errors.register_error(InvalidSyntaxError(
                    "EOF error(maybe you forgot a '}') :))",
                    self.current_tok.position_start,
                    self.current_tok.position_end,
                ))
                return None
            stmt = self.parse_statement()
            
            if stmt:
                block.statements.append(stmt)

        return block

    def parse_assign_expression(self):
        position_start = self.current_tok.position_start
        left = self.parse_math_expression()
        if self.current_tok.type == EQUAL:
            if not isinstance(left, IdentifierNode):
                self.errors.register_error(InvalidSyntaxError(
                    f"You can't assign a value to {left}",
                    self.current_tok.position_start,
                    self.current_tok.position_end,
                ))
                return None
            self.advance()
            right = self.parse_math_expression()
            return VarAssignNode(left, right, position_start, self.current_tok.position_end)
        return left

    def parse_math_expression(self):
        if self.current_tok.type in (INT, FLOAT, STRING, IDENTIFIER, PLUS, MINUS, LPAREN, LSQUAREBRACKET):
            return self.parse_comparator_expression()
        else:
            self.errors.register_error(InvalidSyntaxError(
                "Expected INT, IDENTIFIER, '+', '-', '(', '['",
                self.current_tok.position_start,
                self.current_tok.position_end,
            ))
            return None

    def parse_comparator_expression(self):
        position_start = self.current_tok.position_start
        left = self.expression()
        if self.current_tok.type in (LESS_THAN, LESS_THAN_OR_EQUAL, GREATER_THAN, GREATER_THAN_OR_EQUAL, DOUBLE_EQUAL, NOT_EQUAL):
            operator = self.current_tok
            self.advance()

            right = self.expression()
            return BinaryOperationNode(left, operator, right, position_start, self.current_tok.position_end)
        else:
            return left

    def expression(self):
        position_start = self.current_tok.position_start
        left = self.term()

        while self.current_tok is not None and self.current_tok.type in (PLUS, MINUS):
            if not self.current_tok.type in (PLUS, MINUS):
                self.errors.register_error(InvalidSyntaxError(
                    "Expected '+' or '-'",
                    self.current_tok.position_start,
                    self.current_tok.position_end,
                ))
                return None
            operation_tok = self.current_tok
            self.advance()
            right = self.term()
            left = BinaryOperationNode(left, operation_tok, right, position_start, self.current_tok.position_end)

        return left

    def term(self):
        position_start = self.current_tok.position_start
        left = self.parse_call_or_index_expr()

        while self.current_tok is not None and self.current_tok.type in (ASTERISK, SLASH):
            if not self.current_tok.type in (ASTERISK, SLASH):
                self.errors.register_error(InvalidSyntaxError(
                    "Expected '*' or '/'",
                    self.current_tok.position_start,
                    self.current_tok.position_end,
                ))
                return None
            operation_tok = self.current_tok
            self.advance()
            right = self.parse_call_or_index_expr()
            left = BinaryOperationNode(left, operation_tok, right, position_start, self.current_tok.position_end)

        return left
    
    def parse_call_or_index_expr(self):
        position_start = self.current_tok.position_start
        left = self.parse_arrow_func_expression()

        while self.current_tok.type in (LPAREN, LSQUAREBRACKET):
            if self.current_tok.type == LPAREN:
                left = CallNode(left, self.parse_paren_expr(), position_start, self.current_tok.position_end)
                self.advance()
            else:
                self.advance()
                left = IndexNode(left, self.parse_math_expression(), position_start, self.current_tok.position_end)
                if self.current_tok.type != RSQUAREBRACKET:
                    self.errors.register_error(InvalidSyntaxError(
                        "Expected ']'",
                        self.current_tok.position_start,
                        self.current_tok.position_end,
                    ))
                    return None
                self.advance()
        return left

    def parse_arrow_func_expression(self):
        position_start = self.current_tok.position_start
        left = self.factor()

        if self.current_tok.type == ARROW:
            self.advance()
            code_block = self.parse_block_statement()
            self.advance()
            return FunctionNode("anonymous", left, code_block, position_start, self.current_tok.position_end)
        return left

    def factor(self):
        position_start = self.current_tok.position_start
        tok = self.current_tok

        if tok.type == LPAREN:
            self.advance()

            if self.current_tok.type == RPAREN:
                position_end = self.current_tok.position_end
                self.advance()
                return SetNode([], position_start, position_end)

            result = self.parse_math_expression()
            if self.current_tok.type != COMMA:
                if self.current_tok.type != RPAREN:
                    self.errors.register_error(InvalidSyntaxError(
                        "Expected ')'",
                        self.current_tok.position_start,
                        self.current_tok.position_end,
                    ))
                    return None
                self.advance()
                return result
            elements = []
            elements.append(result)
            self.advance()
            while self.current_tok.type != RPAREN:
                elements.append(self.parse_math_expression())
                if self.current_tok.type == COMMA:
                    self.advance()
            self.advance()
            return SetNode(elements, position_start, self.current_tok.position_end)
        elif tok.type == INT or tok.type == FLOAT:
            self.advance()
            return NumberNode(tok, position_start, self.current_tok.position_end)
        elif tok.type == STRING:
            self.advance()
            return StringNode(tok, position_start, self.current_tok.position_end)
        elif tok.type == IDENTIFIER:
            self.advance()
            return IdentifierNode(tok, position_start, self.current_tok.position_end)
        elif tok.type in (PLUS, MINUS, NOT):
            if self.current_tok.type not in (PLUS, MINUS, NOT):
                self.errors.register_error(InvalidSyntaxError(
                    "Expected '+', '-' or '!'",
                    self.current_tok.position_start,
                    self.current_tok.position_end,
                ))
                return None
            op_tok = self.current_tok
            self.advance()
            right = self.factor()
            return UnaryOperationNode(op_tok, right, position_start, self.current_tok.position_end)
        elif tok.type == LSQUAREBRACKET:
            elements = []
            while not self.current_tok.type == RSQUAREBRACKET:
                self.advance()
                elements.append(self.current_tok)
                self.advance()
                if self.current_tok.type not in (RSQUAREBRACKET, COMMA):
                    self.errors.register_error(InvalidSyntaxError(
                        "Expected ',' or ']'",
                        self.current_tok.position_start,
                        self.current_tok.position_end,
                    ))
                    return None
            self.advance()
            return ListNode(elements, position_start, self.current_tok.position_end)
        self.errors.register_error(InvalidSyntaxError(
            "Expected INT, IDENTIFIER, '+', '-', '(', '[', 'if'",
            self.current_tok.position_start,
            self.current_tok.position_end,
        ))
    
    def parse_paren_expr(self):
        position_start = self.current_tok.position_start
        if self.current_tok.type == LPAREN:
            self.advance()
            args = []

            if self.current_tok.type == RPAREN:
                return ArgNode(args, position_start, self.current_tok.position_end)

            while self.current_tok.type != RPAREN:
                if self.current_tok.type == EOF:
                    self.errors.register_error(InvalidSyntaxError(
                        "EOF error(maybe you forgot a '}') :))",
                        self.current_tok.position_start,
                        self.current_tok.position_end,
                    ))
                    return None

                args.append(self.parse_math_expression())
                if self.current_tok.type != COMMA and self.current_tok.type != RPAREN:
                    self.errors.register_error(InvalidSyntaxError(
                        "Expected ',' or '('",
                        self.current_tok.position_start,
                        self.current_tok.position_end,
                    ))
                    return None
                elif self.current_tok.type == RPAREN:
                    break

                self.advance()
            
            return ArgNode(args, position_start, self.current_tok.position_end)
    
    def is_type(self, token):
        return True if token.matches(KEYWORD, "int") or token.matches(KEYWORD, "float") or token.matches(KEYWORD, "string") or token.matches(KEYWORD, "bool") else False
