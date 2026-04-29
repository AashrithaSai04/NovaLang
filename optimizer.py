from ast_nodes import (
    AssignmentNode, BinaryOpNode, NumberNode, PrintNode, ProgramNode,
    VariableNode, IfNode, IfElseNode, ComparisonNode, WhileNode, StringNode,
    UnaryOpNode
)
import re


class Optimizer:
    def optimize(self, node):
        constants = {}
        return self._optimize(node, constants)

    def _optimize(self, node, constants):
        if isinstance(node, ProgramNode):
            return ProgramNode([self._optimize(statement, constants) for statement in node.statements])

        if isinstance(node, AssignmentNode):
            optimized_value = self._optimize(node.value, constants)
            if isinstance(optimized_value, NumberNode):
                constants[node.name] = optimized_value.value
            else:
                constants.pop(node.name, None)
            return AssignmentNode(node.name, optimized_value, node.is_declaration)

        if isinstance(node, PrintNode):
            return PrintNode(self._optimize(node.value, constants))

        if isinstance(node, IfNode):
            optimized_condition = self._optimize(node.condition, constants)
            optimized_body = [self._optimize(stmt, constants) for stmt in node.then_body]
            return IfNode(optimized_condition, optimized_body)

        if isinstance(node, IfElseNode):
            optimized_condition = self._optimize(node.condition, constants)
            optimized_then = [self._optimize(stmt, constants) for stmt in node.then_body]
            optimized_else = [self._optimize(stmt, constants) for stmt in node.else_body]
            return IfElseNode(optimized_condition, optimized_then, optimized_else)

        if isinstance(node, WhileNode):
            optimized_condition = self._optimize(node.condition, constants)
            optimized_body = [self._optimize(stmt, constants) for stmt in node.body]
            return WhileNode(optimized_condition, optimized_body)

        if isinstance(node, ComparisonNode):
            left = self._optimize(node.left, constants)
            right = self._optimize(node.right, constants)
            return ComparisonNode(left, node.operator, right)

        if isinstance(node, VariableNode):
            if node.name in constants:
                return NumberNode(constants[node.name])
            return node

        if isinstance(node, BinaryOpNode):
            left = self._optimize(node.left, constants)
            right = self._optimize(node.right, constants)
            if isinstance(left, NumberNode) and isinstance(right, NumberNode):
                return NumberNode(self._apply(node.operator, left.value, right.value))
            return BinaryOpNode(left, node.operator, right)

        if isinstance(node, UnaryOpNode):
            operand = self._optimize(node.operand, constants)
            if node.operator == '-' and isinstance(operand, NumberNode):
                return NumberNode(-operand.value)
            return UnaryOpNode(node.operator, operand)

        return node

    def _apply(self, operator, left, right):
        if operator == '+':
            return left + right
        if operator == '-':
            return left - right
        if operator == '*':
            return left * right
        if operator == '/':
            if right == 0:
                raise ZeroDivisionError('Division by zero')
            return left // right
        raise ValueError(f'Unknown operator {operator!r}')

    def optimize_tac(self, instructions):
        constants = {}
        optimized = []

        for instruction in instructions:
            line = instruction.strip()
            if not line:
                continue

            print_match = re.fullmatch(r'print\s+(.+)', line)
            if print_match:
                value = self._resolve_value(print_match.group(1).strip(), constants)
                optimized.append(f'print {value}')
                continue

            assign_match = re.fullmatch(r'([A-Za-z_]\w*)\s*=\s*(.+)', line)
            if not assign_match:
                optimized.append(line)
                continue

            target = assign_match.group(1)
            expression = assign_match.group(2).strip()

            binary_match = re.fullmatch(r'(\S+)\s*([+\-*/])\s*(\S+)', expression)
            if binary_match:
                left_raw, operator, right_raw = binary_match.groups()
                left = self._resolve_value(left_raw, constants)
                right = self._resolve_value(right_raw, constants)

                if self._is_int(left) and self._is_int(right):
                    result = self._apply(operator, int(left), int(right))
                    optimized.append(f'{target} = {result}')
                    constants[target] = result
                else:
                    optimized.append(f'{target} = {left} {operator} {right}')
                    constants.pop(target, None)
                continue

            value = self._resolve_value(expression, constants)
            optimized.append(f'{target} = {value}')
            if self._is_int(value):
                constants[target] = int(value)
            else:
                constants.pop(target, None)

        return optimized

    def _resolve_value(self, token, constants):
        if token in constants:
            return str(constants[token])
        return token

    def _is_int(self, text):
        return re.fullmatch(r'-?\d+', text) is not None
