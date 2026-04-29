from ast_nodes import AssignmentNode, BinaryOpNode, NumberNode, PrintNode, ProgramNode, VariableNode


class IntermediateCodeGenerator:
    def __init__(self):
        self.instructions = []
        self.temp_counter = 0

    def generate(self, node):
        self.instructions = []
        self.temp_counter = 0
        self._emit_program(node)
        return self.instructions

    def _emit_program(self, node):
        if isinstance(node, ProgramNode):
            for statement in node.statements:
                self._emit_statement(statement)
            return
        self._emit_statement(node)

    def _emit_statement(self, node):
        if isinstance(node, AssignmentNode):
            value = self._emit_expr(node.value)
            self.instructions.append(f'{node.name} = {value}')
            return

        if isinstance(node, PrintNode):
            value = self._emit_expr(node.value)
            self.instructions.append(f'print {value}')
            return

        raise TypeError(f'Unsupported statement node {type(node).__name__}')

    def _emit_expr(self, node):
        if isinstance(node, NumberNode):
            return str(node.value)

        if isinstance(node, VariableNode):
            return node.name

        if isinstance(node, BinaryOpNode):
            left = self._emit_expr(node.left)
            right = self._emit_expr(node.right)
            temp = self._new_temp()
            self.instructions.append(f'{temp} = {left} {node.operator} {right}')
            return temp

        raise TypeError(f'Unsupported expression node {type(node).__name__}')

    def _new_temp(self):
        self.temp_counter += 1
        return f't{self.temp_counter}'