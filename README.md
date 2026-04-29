# NovaLang Mini-Compiler

> A fully functional educational compiler that translates NovaLang source code through a complete 6-stage compilation pipeline — from raw source text to assembly-like output.

---

## Overview

NovaLang is a custom-designed programming language built to demonstrate every core concept of modern compiler construction. The mini-compiler processes NovaLang programs through six distinct phases: lexical analysis, syntax analysis, semantic analysis, intermediate code generation, optimization, and final code generation.

The project is designed to be readable, extensible, and easy to follow — each phase is implemented in its own module with a clear input/output contract.

---

## Language Features

| Feature | Syntax | Example |
|---|---|---|
| Variable declaration | `var name <- value` | `var x <- 10` |
| Assignment | `name <- value` | `x <- 20` |
| Arithmetic | `+` `-` `*` `/` | `var c <- a + b * 2` |
| Unary minus | `-expression` | `var x <- -5` |
| Print statement | `show -> expr` | `show -> x + 1` |
| String print | `show -> "text"` | `show -> "Hello"` |
| Comparison ops | `== != < > <= >=` | `a > b` |
| If / else | `if condition { }` | `if x > 0 { show -> x }` |
| While loop | `while condition { }` | `while x < 10 { x <- x + 1 }` |
| Comments | `// text` | `// this is a comment` |
| Program delimiters | `#begin ... #end` | wraps every program |

---

## Project Structure

```
NovaLang/
├── ast_nodes       # AST node definitions (data classes)
├── lexer.py        # Lexical analysis — source code → token stream
├── parser.py       # Syntax analysis — tokens → AST
├── semantic.py     # Semantic analysis — type checking, symbol table
├── icg.py          # Intermediate code generation — AST → TAC
├── optimizer.py    # Optimization — constant folding & propagation
└── codegen.py      # Code generation — TAC → assembly-like output
```

### Module Descriptions

- **`ast_nodes`** — Data classes for every AST node type: `NumberNode`, `StringNode`, `VariableNode`, `BinaryOpNode`, `UnaryOpNode`, `AssignmentNode`, `PrintNode`, `IfNode`, `WhileNode`, `ProgramNode`.
- **`lexer.py`** — Scans source code character by character and produces a flat list of typed tokens. Handles all keywords, identifiers, numbers, string literals, operators, and comments.
- **`parser.py`** — Consumes the token stream using recursive descent parsing and builds an Abstract Syntax Tree that encodes the full structure of the program.
- **`semantic.py`** — Walks the AST to enforce language rules: catches undeclared variables, type mismatches, and builds a symbol table mapping every identifier to its type.
- **`icg.py`** — Converts the validated AST into Three-Address Code (TAC), a flat intermediate representation using temporary variables (`t1`, `t2`, ...).
- **`optimizer.py`** — Performs constant folding (evaluates compile-time expressions like `3 + 4 → 7`) and constant propagation on both the AST and TAC.
- **`codegen.py`** — Translates optimized TAC into a simple assembly-like instruction set with registers, MOV, arithmetic instructions, jumps, and PRINT.

---

## Compilation Pipeline

```
Source Code
    │
    ▼
[1] Lexer        →  Token stream
    │
    ▼
[2] Parser       →  Abstract Syntax Tree (AST)
    │
    ▼
[3] Semantic     →  Validated AST + Symbol Table
    │
    ▼
[4] ICG          →  Three-Address Code (TAC)
    │
    ▼
[5] Optimizer    →  Optimized TAC
    │
    ▼
[6] Codegen      →  Assembly-like output
```

---

## Phase Breakdown

### Phase 1 — Lexical Analysis (`lexer.py`)
Reads raw source code and breaks it into a stream of tokens. Handles all language constructs including keywords, string literals, comparison operators, and comments (which are silently discarded).

```
Input:   var x <- 5 + 3
Output:  KEYWORD(var)  IDENTIFIER(x)  ASSIGN(<-)  NUMBER(5)  OP(+)  NUMBER(3)
```

### Phase 2 — Syntax Analysis (`parser.py`)
Implements a recursive descent parser that builds an AST from the token stream. Supports operator precedence, nested expressions, control flow blocks, and unary operators.

```
Input:   KEYWORD(var)  IDENTIFIER(x)  ASSIGN(<-)  NUMBER(5)  OP(+)  NUMBER(3)
Output:  AssignmentNode(name='x', value=BinaryOpNode(NumberNode(5), '+', NumberNode(3)), is_declaration=True)
```

### Phase 3 — Semantic Analysis (`semantic.py`)
Walks the AST and enforces language rules. Builds a symbol table, catches use of undeclared variables, and verifies type consistency across expressions.

```
Input:   AST from Phase 2
Output:  Symbol table: { x: 'number' }
         Error (if any): "Undeclared variable: y"
```

### Phase 4 — Intermediate Code Generation (`icg.py`)
Flattens the AST into Three-Address Code — a sequence of simple instructions each involving at most one operator and three operands (two sources, one destination).

```
Input:   AST from Phase 3
Output:
    t1 = 5 + 3
    x = t1
```

### Phase 5 — Optimization (`optimizer.py`)
Applies constant folding and propagation at both the AST and TAC levels. Eliminates unnecessary temporaries and pre-evaluates expressions whose values are known at compile time.

```
Input:   t1 = 5 + 3   →   x = t1
Output:  x = 8
```

### Phase 6 — Code Generation (`codegen.py`)
Converts optimized TAC into a register-based assembly-like output. Each TAC instruction maps to one or more assembly instructions using MOV, ADD, SUB, MUL, DIV, CMP, JMP, and PRINT.

```
Input:   x = 8
Output:
    MOV x, 8
    MOV R1, x
    PRINT R1
```

---

## Usage

Run each phase individually or chain them in a driver script:

```python
from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer
from optimizer import Optimizer
from icg import IntermediateCodeGenerator
from codegen import CodeGenerator

source_code = open("program.nova").read()

tokens       = Lexer(source_code).tokenize()
ast          = Parser(tokens).parse()
              SemanticAnalyzer().analyze(ast)
opt_ast      = Optimizer().optimize(ast)
tac          = IntermediateCodeGenerator().generate(opt_ast)
assembly     = CodeGenerator().generate_text(tac)

print(assembly)
```

---

## Example Programs

### Basic Arithmetic
```
#begin
var a <- 12
var b <- 4
var c <- (a + b) * 2
show -> c
#end
```
Output: `32`

---

### Conditional Logic
```
#begin
var score <- 85
if score >= 50 {
    show -> "Pass"
}
else {
    show -> "Fail"
}
#end
```
Output: `Pass`

---

### While Loop
```
#begin
var i <- 1
var total <- 0
while i <= 5 {
    total <- total + i
    i <- i + 1
}
show -> total
#end
```
Output: `15`

---

### Comments and Unary Minus
```
#begin
// Calculate absolute difference
var x <- -8
var y <- 3
var diff <- y + x
show -> diff
#end
```
Output: `-5`

---

## Limitations

- Integer arithmetic only — no floating point support.
- No function declarations or recursion.
- Single-file programs only — no imports or modules.
- Assembly output is educational/illustrative, not directly executable.

---

