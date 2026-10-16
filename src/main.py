import sys
from interpreter import *

def run(filename, text):
    # Generate tokens
    tokens = Lexer(filename, text).make_tokens()

    # Generate AST
    ast = Parser(tokens).parse()

    # Execute the code
    try:
        return Interpreter().visit(ast, Scope())
    except ReturnSignal as ret:
        raise RTError(ret.node.pos_start, ret.node.pos_end, "'return' outside of function")

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <file.dock>")
        sys.exit(1)

    filename = sys.argv[1]
    with open(filename, "r") as f:
        text = f.read()

    try:
        run(filename, text)
    except Error as error:
        print(error.as_string())
        sys.exit(1)

if __name__ == "__main__":
    main()
