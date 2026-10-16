# Dock

A small interpreted programming language written in Python, built from scratch with no parser libraries.

I made Dock alone during my first year at Linköping University for the course TDP019 (*Projekt: datorspråk*). I've cleaned it up a little since then: there are fewer bugs and less boilerplate. Otherwise it's still a first-year project, rough edges included.

```
def factorial(n){
    if(n <= 1){
        return 1
    }
    return n * factorial(n - 1)
}

for(i=1, 6){
    print(factorial(i))
}
```

## Running it

You need Python 3 and nothing else.

```sh
python3 src/main.py examples/demo.dock
python3 src/main.py examples/functions.dock
```

## The language

**Values:** integers, floats, strings (`"..."` or `'...'`), booleans (`true` / `false`) and lists.

```
n = 20
pi = 3.14
name = "dock"
done = false
items = [1, "two", 3.0]
```

**Operators:** `+ - * / ^`, comparisons `== != < > <= >=`, and `and`, `or`, `not`.
Strings can be joined with `+` and repeated with `*`.

```
print(-3 + 2 * 2^2)        # 5
print("ab" * 3)            # ababab
print(not (1 == 2) and true)
```

**Conditionals:**

```
if(x == 1){
    print("one")
}
elif(x == 2){
    print("two")
}
else{
    print("many")
}
```

**Loops:** `while`, plus a `for` that loops over a number (`0..n-1`), the characters of a string, or the elements of a list.
The value after `=` is where to start.

```
i = 0
while(i < 3){
    print(i)
    i = i + 1
}

for(i=0, 3){ print(i) }            # 0 1 2
for(c=0, "abc"){ print(c) }        # a b c
for(x=1, [10, 20, 30]){ print(x) } # 20 30
```

**Functions:** they can take parameters, `return` from anywhere in the body, call themselves, and read variables from the code that called them.

```
def square(n){
    return n^2
}
print(square(7))
```

Statements are separated by newlines, and there are no semicolons.

## How it works

Running a program passes the source through a classic three-stage pipeline:

```
source ──▶ Lexer ──▶ tokens ──▶ Parser ──▶ AST ──▶ Interpreter ──▶ output
```

| File | What it does |
|---|---|
| `src/main.py` | Entry point. Reads the file, runs it through the pipeline and prints any error. |
| `src/lexer.py` | Walks the source one character at a time and produces tokens (`INT:5`, `IDENTIFIER:x`, `COMP_OPERATOR:==`, ...). It tracks line and column for error messages. |
| `src/parserDock.py` | A hand-written **recursive-descent parser**. Each grammar rule is a method. Operator precedence comes from the call order `logic → compare → arith_expr → term → factor → power → atom`. |
| `src/nodes.py` | The AST node classes (`BinaryOpNode`, `IfStmtNode`, `FuncDeclareNode`, ...). |
| `src/interpreter.py` | A **tree-walking interpreter** using the visitor pattern: `visit(node)` calls `visit_<NodeType>`. It also contains `Scope`, a chain of variable and function tables. |
| `src/datatypes.py` | Runtime values (`Number`, `String`, `Boolean`, `List`). Each type decides which operators it supports. |
| `src/errors.py` | Errors are exceptions that carry a position. `main.py` catches them and prints e.g. `Runtime Error: Division By Zero, line: 3`. |

The full grammar is in [`docs/grammar.bnf`](docs/grammar.bnf).

## Known limitations

These are left as they are on purpose.

- Identifiers can only contain letters: no digits or underscores.
- There are no comments, no modulo, no list indexing and no `null`. A function with no `return` produces nothing usable.
- Function scope is *dynamic*: a function sees the variables of whoever called it. Assignments inside a function stay local, so a function can't change a global variable.
- Comparing values of different types (`1 == "1"`) is an error rather than `false`.
- Error messages only report the line, not the column.
- Deep recursion runs into Python's own recursion limit.
