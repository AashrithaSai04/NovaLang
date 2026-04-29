from ast_nodes import (
    AssignmentNode, BinaryOpNode, NumberNode, PrintNode, ProgramNode,
    VariableNode, IfNode, IfElseNode, ComparisonNode, WhileNode, StringNode,
    UnaryOpNode
)


class SemanticError(Exception):
    pass


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}
        self.scopes = [{}]

    def analyze(self, node):
        self._visit(node)
        return self.symbol_table

    def _enter_scope(self):
        self.scopes.append({})

    def _exit_scope(self):
        self.scopes.pop()

    def _declare(self, name, value_type):
        if name in self.scopes[-1]:
            raise SemanticError(f"Variable '{name}' already declared in this scope")
        self.scopes[-1][name] = value_type
        self.symbol_table[name] = value_type

    def _lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise SemanticError(f"Variable '{name}' used before declaration")

    def _visit(self, node):
        if isinstance(node, ProgramNode):
            for stmt in node.statements:
                self._visit(stmt)
            return

        if isinstance(node, AssignmentNode):
            value_type = self._visit(node.value)

            if node.is_declaration:
                self._declare(node.name, value_type)
            else:
                existing_type = self._lookup(node.name)
                if existing_type != value_type:
                    raise SemanticError(
                        f"Type mismatch for '{node.name}': {existing_type} vs {value_type}"
                    )
            return value_type

        if isinstance(node, PrintNode):
            return self._visit(node.value)

        if isinstance(node, IfNode):
            cond_type = self._visit(node.condition)
            if cond_type != 'boolean':
                raise SemanticError("Condition must be boolean")

            self._enter_scope()
            for stmt in node.then_body:
                self._visit(stmt)
            self._exit_scope()
            return

        if isinstance(node, IfElseNode):
            cond_type = self._visit(node.condition)
            if cond_type != 'boolean':
                raise SemanticError("Condition must be boolean")

            self._enter_scope()
            for stmt in node.then_body:
                self._visit(stmt)
            self._exit_scope()

            self._enter_scope()
            for stmt in node.else_body:
                self._visit(stmt)
            self._exit_scope()
            return

        if isinstance(node, WhileNode):
            cond_type = self._visit(node.condition)
            if cond_type != 'boolean':
                raise SemanticError("Condition must be boolean")

            self._enter_scope()
            for stmt in node.body:
                self._visit(stmt)
            self._exit_scope()
            return

        if isinstance(node, ComparisonNode):
            left = self._visit(node.left)
            right = self._visit(node.right)
            if left != 'number' or right != 'number':
                raise SemanticError("Comparison requires numbers")
            return 'boolean'

        if isinstance(node, BinaryOpNode):
            left = self._visit(node.left)
            right = self._visit(node.right)
            if left != 'number' or right != 'number':
                raise SemanticError("Arithmetic requires numbers")
            return 'number'

        if isinstance(node, UnaryOpNode):
            operand = self._visit(node.operand)
            if node.operator == '-' and operand == 'number':
                return 'number'
            raise SemanticError("Invalid unary operation")

        if isinstance(node, NumberNode):
            return 'number'

        if isinstance(node, StringNode):
            return 'string'

        if isinstance(node, VariableNode):
            return self._lookup(node.name)

        raise SemanticError(f"Unsupported node {type(node).__name__}")