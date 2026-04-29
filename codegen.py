import re

class CodeGenerator:
    OPERATION_MAP = {
        '+': 'ADD',
        '-': 'SUB',
        '*': 'MUL',
        '/': 'DIV',
    }

    JUMP_MAP = {
        '<': 'JL',
        '<=': 'JLE',
        '>': 'JG',
        '>=': 'JGE',
        '==': 'JE',
        '!=': 'JNE',
    }

    def generate(self, tac_program):
        # Accept either a raw list of TAC lines or an object exposing .instructions.
        tac_instructions = getattr(tac_program, 'instructions', tac_program)
        assembly = []
        for instruction in tac_instructions:
            assembly.extend(self._translate_instruction(instruction))
        return assembly

    def generate_text(self, tac_program):
        return '\n'.join(self.generate(tac_program))

    def _translate_instruction(self, instruction):
        instruction = instruction.strip()
        if not instruction:
            return []

        if instruction.endswith(':'):
            return [instruction]

        print_match = re.fullmatch(r'print\s+(.+)', instruction)
        if print_match:
            value = print_match.group(1).strip()
            return [
                f'MOV R1, {value}',
                'PRINT R1',
            ]

        if_match = re.fullmatch(r'if\s+(\S+)\s*([<>!=]=?|==|!=)\s*(\S+)\s+goto\s+(\S+)', instruction)
        if if_match:
            left, operator, right, label = if_match.groups()
            if operator not in self.JUMP_MAP:
                raise ValueError(f'Unsupported comparison operator {operator!r}')
            return [
                f'MOV R1, {left}',
                f'MOV R2, {right}',
                'CMP R1, R2',
                f"{self.JUMP_MAP[operator]} {label}",
            ]

        goto_match = re.fullmatch(r'goto\s+(\S+)', instruction)
        if goto_match:
            return [f'JMP {goto_match.group(1)}']

        func_match = re.fullmatch(r'func\s+([A-Za-z_]\w*):', instruction)
        if func_match:
            return [f"{func_match.group(1)}:"]

        return_match = re.fullmatch(r'return\s*(\S+)?', instruction)
        if return_match:
            value = return_match.group(1)
            if value:
                return [f'MOV R1, {value}', 'RET']
            return ['RET']

        assign_match = re.fullmatch(r'([A-Za-z_]\w*)\s*=\s*(.+)', instruction)
        if not assign_match:
            raise ValueError(f'Unsupported TAC instruction: {instruction!r}')

        target = assign_match.group(1)
        expression = assign_match.group(2).strip()

        binary_match = re.fullmatch(r'(\S+)\s*([+\-*/])\s*(\S+)', expression)
        if binary_match:
            left = binary_match.group(1)
            operator = binary_match.group(2)
            right = binary_match.group(3)
            assembly_op = self.OPERATION_MAP[operator]
            return [
                f'MOV R1, {left}',
                f'MOV R2, {right}',
                f'{assembly_op} R1, R2',
                f'MOV {target}, R1',
            ]

        return [f'MOV {target}, {expression}']

    def execute_ir(self, ir_program):
        _ = ir_program
        return ['TODO: Assembly execution']
