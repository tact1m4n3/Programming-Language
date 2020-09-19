from lexer import Lexer
from parser_ import Parser
from interpreter import Interpreter, Context, SymbolTable
from compiler import Compiler
import sys


if __name__ == "__main__":
    filename = sys.argv[1]
    with open(filename, 'r') as f:
        code = f.read()

    lexer = Lexer(code, 'stdin')
    tokens, errors = lexer.tokenize()

    if errors:
        for error in errors:
            print(error.as_string())
        exit()

    parser = Parser(tokens)
    ast = parser.parse_program()
    if parser.errors.errors:
        for error in parser.errors.errors:
            print(error.as_string())
        exit()
    print(ast)
    
    compiler = Compiler()
    compiler.visit(ast)

    with open(filename[:-3] + "bin", "w+") as f:
        f.write(" ".join(compiler.code))