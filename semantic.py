from ast_nodes import AssignmentNode, BinaryOpNode, NumberNode, PrintNode, ProgramNode, VariableNode


class SemanticError(Exception):
    pass


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}

    def analyze(self, node):
        self._visit(node)
        return self.symbol_table

    def _visit(self, node):
        if isinstance(node, ProgramNode):
            for statement in node.statements:
                self._visit(statement)
            return

        if isinstance(node, AssignmentNode):
            value_type = self._visit(node.value)
            self.symbol_table[node.name] = value_type
            return value_type

        if isinstance(node, PrintNode):
            return self._visit(node.value)

        if isinstance(node, BinaryOpNode):
            left_type = self._visit(node.left)
            right_type = self._visit(node.right)
            if left_type != 'number' or right_type != 'number':
                raise SemanticError('Invalid operation: arithmetic expressions require numeric values')
            return 'number'

        if isinstance(node, NumberNode):
            return 'number'

        if isinstance(node, VariableNode):
            if node.name not in self.symbol_table:
                raise SemanticError(f'Variable {node.name!r} used before declaration')
            return self.symbol_table[node.name]

        raise SemanticError(f'Unsupported syntax node {type(node).__name__}')