from ast_nodes import (
    AssignmentNode, BinaryOpNode, NumberNode, PrintNode, ProgramNode,
    VariableNode, IfNode, IfElseNode, ComparisonNode, WhileNode, StringNode,
    UnaryOpNode
)


class ParserError(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def parse(self):
        program = self.program()
        self._expect('EOF')
        return program

    def program(self):
        self._expect('BEGIN')
        statements = self.statement_list()
        self._expect('END')
        return ProgramNode(statements)

    def statement_list(self):
        statements = []
        while self._current().type not in ('END', 'EOF'):
            statements.append(self.statement())
        return statements

    def statement(self):
        token = self._current()
        if token.type == 'KEYWORD' and token.value == 'var':
            return self.declaration()
        if token.type == 'KEYWORD' and token.value == 'show':
            return self.print_statement()
        if token.type == 'KEYWORD' and token.value == 'if':
            return self.if_statement()
        if token.type == 'KEYWORD' and token.value == 'while':
            return self.while_statement()
        if token.type == 'IDENTIFIER':
            return self.assignment()
        raise ParserError(f'Unexpected token {token.type} at position {token.position}')

    def declaration(self):
        self._expect('KEYWORD', 'var')
        name = self._expect('IDENTIFIER').value
        self._expect('ASSIGN')
        value = self.expr()
        return AssignmentNode(name, value, is_declaration=True)

    def assignment(self):
        name = self._expect('IDENTIFIER').value
        self._expect('ASSIGN')
        value = self.expr()
        return AssignmentNode(name, value, is_declaration=False)

    def print_statement(self):
        self._expect('KEYWORD', 'show')
        self._expect('ARROW')
        value = self.expr()
        return PrintNode(value)

    def if_statement(self):
        self._expect('KEYWORD', 'if')
        condition = self.comparison()
        self._expect('LBRACE')
        then_body = self.block()
        self._expect('RBRACE')
        
        if self._current().type == 'KEYWORD' and self._current().value == 'else':
            self._advance()
            self._expect('LBRACE')
            else_body = self.block()
            self._expect('RBRACE')
            return IfElseNode(condition, then_body, else_body)
        
        return IfNode(condition, then_body)

    def while_statement(self):
        self._expect('KEYWORD', 'while')
        condition = self.comparison()
        self._expect('LBRACE')
        body = self.block()
        self._expect('RBRACE')
        return WhileNode(condition, body)

    def block(self):
        statements = []
        while self._current().type not in ('RBRACE', 'EOF'):
            statements.append(self.statement())
        return statements

    def comparison(self):
        left = self.expr()
        if self._current().type == 'RELOP':
            operator = self._advance().value
            right = self.expr()
            return ComparisonNode(left, operator, right)
        return left

    def expr(self):
        node = self.term()
        while self._current().type in ('PLUS', 'MINUS'):
            operator = self._advance().value
            right = self.term()
            node = BinaryOpNode(node, operator, right)
        return node

    def term(self):
        node = self.factor()
        while self._current().type in ('STAR', 'SLASH'):
            operator = self._advance().value
            right = self.factor()
            node = BinaryOpNode(node, operator, right)
        return node

    def factor(self):
        token = self._current()
        if token.type == 'MINUS':
            self._advance()
            operand = self.factor()
            return UnaryOpNode('-', operand)
        if token.type == 'NUMBER':
            self._advance()
            return NumberNode(token.value)
        if token.type == 'STRING':
            self._advance()
            return StringNode(token.value)
        if token.type == 'IDENTIFIER':
            self._advance()
            return VariableNode(token.value)
        if token.type == 'LPAREN':
            self._advance()
            node = self.expr()
            self._expect('RPAREN')
            return node
        raise ParserError(f'Unexpected token {token.type} at position {token.position}')

    def _current(self):
        return self.tokens[self.position]

    def _advance(self):
        token = self.tokens[self.position]
        self.position += 1
        return token

    def _expect(self, token_type, token_value=None):
        token = self._current()
        if token.type != token_type:
            raise ParserError(f'Expected {token_type} but found {token.type} at position {token.position}')
        if token_value is not None and token.value != token_value:
            raise ParserError(f'Expected {token_value!r} but found {token.value!r} at position {token.position}')
        self.position += 1
        return token