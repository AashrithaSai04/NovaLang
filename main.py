import sys
from dataclasses import fields, is_dataclass

from codegen import CodeGenerator
from icg import IntermediateCodeGenerator
from lexer import Lexer, LexerError
from optimizer import Optimizer
from parser import Parser, ParserError
from semantic import SemanticAnalyzer, SemanticError


class Interpreter:
    def __init__(self):
        self.environment = {}

    def execute(self, node):
        return self._visit(node)

    def _visit(self, node):
        from ast_nodes import (
            AssignmentNode, BinaryOpNode, NumberNode, PrintNode, ProgramNode,
            VariableNode, IfNode, IfElseNode, ComparisonNode, WhileNode, StringNode,
            UnaryOpNode
        )

        if isinstance(node, ProgramNode):
            result = None
            for statement in node.statements:
                result = self._visit(statement)
            return result

        if isinstance(node, AssignmentNode):
            value = self._visit(node.value)
            self.environment[node.name] = value
            return value

        if isinstance(node, PrintNode):
            value = self._visit(node.value)
            print(value)
            return value

        if isinstance(node, IfNode):
            condition = self._visit(node.condition)
            if condition:
                result = None
                for statement in node.then_body:
                    result = self._visit(statement)
                return result
            return None

        if isinstance(node, IfElseNode):
            condition = self._visit(node.condition)
            if condition:
                result = None
                for statement in node.then_body:
                    result = self._visit(statement)
                return result
            else:
                result = None
                for statement in node.else_body:
                    result = self._visit(statement)
                return result

        if isinstance(node, WhileNode):
            result = None
            while self._visit(node.condition):
                for statement in node.body:
                    result = self._visit(statement)
            return result

        if isinstance(node, ComparisonNode):
            left = self._visit(node.left)
            right = self._visit(node.right)
            if node.operator == '==':
                return left == right
            if node.operator == '!=':
                return left != right
            if node.operator == '<':
                return left < right
            if node.operator == '>':
                return left > right
            if node.operator == '<=':
                return left <= right
            if node.operator == '>=':
                return left >= right
            raise ValueError(f'Unknown comparison operator {node.operator!r}')

        if isinstance(node, BinaryOpNode):
            left = self._visit(node.left)
            right = self._visit(node.right)
            if node.operator == '+':
                return left + right
            if node.operator == '-':
                return left - right
            if node.operator == '*':
                return left * right
            if node.operator == '/':
                if right == 0:
                    raise ZeroDivisionError('Division by zero')
                return left // right
            raise ValueError(f'Unknown operator {node.operator!r}')

        if isinstance(node, UnaryOpNode):
            operand = self._visit(node.operand)
            if node.operator == '-':
                return -operand
            raise ValueError(f'Unknown unary operator {node.operator!r}')

        if isinstance(node, NumberNode):
            return node.value

        if isinstance(node, StringNode):
            return node.value

        if isinstance(node, VariableNode):
            if node.name not in self.environment:
                raise NameError(f'Variable {node.name!r} is not defined')
            return self.environment[node.name]

        raise TypeError(f'Unsupported node type {type(node).__name__}')


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

    interpreter = Interpreter()
    final_output = interpreter.execute(optimized_ast)

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
var z <- (x + y) * 4
show -> z
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

        # Final Output
        output_lines.append("Final Output:")
        if phase_output['final_output'] is not None:
            output_lines.append(str(phase_output['final_output']))

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