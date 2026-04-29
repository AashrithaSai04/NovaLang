class IntermediateCodeGenerator:
    def __init__(self):
        self.instructions = []
        self.temp_counter = 0
        self.label_counter = 0

    def generate(self, node):
        self.instructions = []
        self.temp_counter = 0
        self.label_counter = 0
        self._emit(node)
        return self.instructions

    def _emit(self, node):
        if hasattr(node, "statements"):
            for stmt in node.statements:
                self._emit(stmt)
            return

        if node.__class__.__name__ == "AssignmentNode":
            val = self._expr(node.value)
            self.instructions.append(f"{node.name} = {val}")

        elif node.__class__.__name__ == "PrintNode":
            val = self._expr(node.value)
            self.instructions.append(f"print {val}")

        elif node.__class__.__name__ == "IfNode":
            end = self._new_label()
            cond = self._condition(node.condition)
            self.instructions.append(f"ifFalse {cond} goto {end}")
            for s in node.then_body:
                self._emit(s)
            self.instructions.append(f"{end}:")

        elif node.__class__.__name__ == "IfElseNode":
            else_l = self._new_label()
            end = self._new_label()
            cond = self._condition(node.condition)
            self.instructions.append(f"ifFalse {cond} goto {else_l}")

            for s in node.then_body:
                self._emit(s)

            self.instructions.append(f"goto {end}")
            self.instructions.append(f"{else_l}:")

            for s in node.else_body:
                self._emit(s)

            self.instructions.append(f"{end}:")

        elif node.__class__.__name__ == "WhileNode":
            start = self._new_label()
            end = self._new_label()

            self.instructions.append(f"{start}:")
            cond = self._condition(node.condition)
            self.instructions.append(f"ifFalse {cond} goto {end}")

            for s in node.body:
                self._emit(s)

            self.instructions.append(f"goto {start}")
            self.instructions.append(f"{end}:")

    def _expr(self, node):
        if node.__class__.__name__ == "NumberNode":
            return str(node.value)

        if node.__class__.__name__ == "VariableNode":
            return node.name

        if node.__class__.__name__ == "StringNode":
            return f'"{node.value}"'

        if node.__class__.__name__ == "BinaryOpNode":
            l = self._expr(node.left)
            r = self._expr(node.right)
            t = self._new_temp()
            self.instructions.append(f"{t} = {l} {node.operator} {r}")
            return t

        if node.__class__.__name__ == "UnaryOpNode":
            val = self._expr(node.operand)
            t = self._new_temp()
            self.instructions.append(f"{t} = 0 - {val}")
            return t

        return self._expr(node)

    def _condition(self, node):
        left = self._expr(node.left)
        right = self._expr(node.right)
        return f"{left} {node.operator} {right}"

    def _new_temp(self):
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def _new_label(self):
        self.label_counter += 1
        return f"L{self.label_counter}"