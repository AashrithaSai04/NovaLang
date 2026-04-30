import sys
from dataclasses import fields, is_dataclass

from codegen import CodeGenerator
from icg import IntermediateCodeGenerator
from lexer import Lexer, LexerError
from optimizer import Optimizer
from parser import Parser, ParserError
from semantic import SemanticAnalyzer, SemanticError



def compile_and_run(source_code):
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    semantic = SemanticAnalyzer()
    symbol_table = semantic.analyze(ast)

    icg = IntermediateCodeGenerator()
    intermediate_code = icg.generate(ast)

    optimizer = Optimizer()
    optimized_ast = optimizer.optimize(ast)
    optimized_intermediate_code = optimizer.optimize_tac(intermediate_code)

    codegen = CodeGenerator()
    generated_code = codegen.generate(optimized_intermediate_code)

    final_output = None

    return {
        'tokens': tokens,
        'ast': ast,
        'symbol_table': symbol_table,
        'intermediate_code': intermediate_code,
        'optimized_ast': optimized_ast,
        'optimized_intermediate_code': optimized_intermediate_code,
        'generated_code': generated_code,
        'final_output': final_output,
    }


def format_ast(node, indent=0):
    padding = '  ' * indent
    if is_dataclass(node):
        lines = [f"{padding}{type(node).__name__}("]
        for field in fields(node):
            value = getattr(node, field.name)
            lines.append(f"{padding}  {field.name}=")
            lines.append(format_ast(value, indent + 2))
        lines.append(f"{padding})")
        return '\n'.join(lines)

    if isinstance(node, list):
        lines = [f"{padding}["]
        for item in node:
            lines.append(format_ast(item, indent + 1))
        lines.append(f"{padding}]")
        return '\n'.join(lines)

    return f"{padding}{repr(node)}"


def format_tokens(tokens):
    return [f"{token.type:10} {repr(token.value)}" for token in tokens]


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as source_file:
            source_code = source_file.read()
    elif sys.stdin.isatty():
        source_code = """
#begin
var x <- 2
var y <- 3
if (x<y) then
show -> "x is less than y"
else
show -> "x is not less than y"
#end
"""
    else:
        source_code = sys.stdin.read()

    try:
        phase_output = compile_and_run(source_code)

        output_lines = []

        # Source
        output_lines.append("Source Program:")
        output_lines.append(source_code.strip())
        output_lines.append("")

        # Tokens
        output_lines.append("Lexical Analysis (Tokens):")
        for token_line in format_tokens(phase_output['tokens']):
            output_lines.append(token_line)
        output_lines.append("")

        # AST
        output_lines.append("Syntax Analysis (AST):")
        output_lines.append(format_ast(phase_output['ast']))
        output_lines.append("")

        # Symbol Table
        output_lines.append("Semantic Analysis (Symbol Table):")
        for name, value_type in phase_output['symbol_table'].items():
            output_lines.append(f"{name}: {value_type}")
        output_lines.append("")

        # TAC
        output_lines.append("Intermediate Code:")
        for instruction in phase_output['intermediate_code']:
            output_lines.append(instruction)
        output_lines.append("")

        # Optimized AST
        output_lines.append("Optimized AST:")
        output_lines.append(format_ast(phase_output['optimized_ast']))
        output_lines.append("")

        # Optimized TAC
        output_lines.append("Optimized Code:")
        for instruction in phase_output['optimized_intermediate_code']:
            output_lines.append(instruction)
        output_lines.append("")

        # Assembly
        output_lines.append("Generated Code:")
        for instruction in phase_output['generated_code']:
            output_lines.append(instruction)
        output_lines.append("")

        # Join everything
        final_output_text = "\n".join(output_lines)

        # ✅ Print to console
        print(final_output_text)

        # ✅ Save to file
        with open("output.txt", "w", encoding="utf-8") as f:
            f.write(final_output_text)

        print("\n✅ Output saved to output.txt")

    except (LexerError, ParserError, SemanticError, ZeroDivisionError, NameError, TypeError, ValueError) as error:
        print(f'Error: {error}')
        sys.exit(1)

if __name__ == '__main__':
    main()