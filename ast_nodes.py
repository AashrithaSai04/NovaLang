from dataclasses import dataclass
from typing import List


@dataclass
class NumberNode:
    value: int


@dataclass
class StringNode:
    value: str


@dataclass
class VariableNode:
    name: str


@dataclass
class BinaryOpNode:
    left: object
    operator: str
    right: object


@dataclass
class UnaryOpNode:
    operator: str
    operand: object


@dataclass
class ComparisonNode:
    left: object
    operator: str
    right: object


@dataclass
class AssignmentNode:
    name: str
    value: object
    is_declaration: bool = False


@dataclass
class PrintNode:
    value: object


@dataclass
class IfNode:
    condition: object
    then_body: List[object]


@dataclass
class IfElseNode:
    condition: object
    then_body: List[object]
    else_body: List[object]


@dataclass
class WhileNode:
    condition: object
    body: List[object]


@dataclass
class ProgramNode:
    statements: List[object]