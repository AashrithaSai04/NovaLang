import re

class CodeGenerator:
    OP_MAP = {
        '+': 'ADD',
        '-': 'SUB',
        '*': 'MUL',
        '/': 'DIV'
    }

    CMP_MAP = {
        '<': 'JGE',
        '>': 'JLE',
        '<=': 'JG',
        '>=': 'JL',
        '==': 'JNE',
        '!=': 'JE'
    }

    def generate(self, tac):
        output = []
        for line in tac:
            output.extend(self._translate(line.strip()))
        return output

    def _translate(self, line):
        if not line:
            return []

        if line.endswith(':'):
            return [line]

        # print
        m = re.match(r'print (.+)', line)
        if m:
            val = m.group(1)
            return [f"MOV R1, {val}", "PRINT R1"]

        # ifFalse
        m = re.match(r'ifFalse (.+) goto (.+)', line)
        if m:
            cond, label = m.groups()
            l, op, r = cond.split()
            return [
                f"MOV R1, {l}",
                f"MOV R2, {r}",
                "CMP R1, R2",
                f"{self.CMP_MAP[op]} {label}"
            ]

        # goto
        m = re.match(r'goto (.+)', line)
        if m:
            return [f"JMP {m.group(1)}"]

        # assignment
        m = re.match(r'(\w+) = (.+)', line)
        if m:
            target, expr = m.groups()

            # binary
            parts = expr.split()
            if len(parts) == 3:
                l, op, r = parts
                return [
                    f"MOV R1, {l}",
                    f"MOV R2, {r}",
                    f"{self.OP_MAP[op]} R1, R2",
                    f"MOV {target}, R1"
                ]

            return [f"MOV {target}, {expr}"]

        raise ValueError(f"Unknown TAC: {line}")