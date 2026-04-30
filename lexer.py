from dataclasses import dataclass
from typing import List


@dataclass
class Token:
    type: str
    value: object
    position: int


class LexerError(Exception):
    pass


class Lexer:
    KEYWORDS = {"var", "show", "if", "else", "while", "then"}

    def __init__(self, text: str):
        self.text = text
        self.position = 0

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []

        while self.position < len(self.text):
            char = self.text[self.position]

            if char.isspace():
                self.position += 1
                continue

            # Handle single-line comments
            if self.text.startswith('//', self.position):
                # Skip until end of line
                while self.position < len(self.text) and self.text[self.position] != '\n':
                    self.position += 1
                # Skip the newline as well if present
                if self.position < len(self.text) and self.text[self.position] == '\n':
                    self.position += 1
                continue

            if char == '#':
                word = self._read_word()
                if word == '#begin':
                    tokens.append(Token('BEGIN', word, self.position))
                elif word == '#end':
                    tokens.append(Token('END', word, self.position))
                else:
                    raise LexerError(f'Unknown directive {word!r} at position {self.position}')
                continue

            if char.isalpha() or char == '_':
                identifier = self._read_identifier()
                token_type = 'KEYWORD' if identifier in self.KEYWORDS else 'IDENTIFIER'
                tokens.append(Token(token_type, identifier, self.position))
                continue

            if char.isdigit():
                number = self._read_number()
                tokens.append(Token('NUMBER', int(number), self.position))
                continue

            if char == '"':
                string = self._read_string()
                tokens.append(Token('STRING', string, self.position))
                continue

            if self.text.startswith('<-', self.position):
                tokens.append(Token('ASSIGN', '<-', self.position))
                self.position += 2
                continue

            if self.text.startswith('->', self.position):
                tokens.append(Token('ARROW', '->', self.position))
                self.position += 2
                continue

            # Handle comparison operators (check two-character operators first)
            if self.text.startswith('<=', self.position):
                tokens.append(Token('RELOP', '<=', self.position))
                self.position += 2
                continue

            if self.text.startswith('>=', self.position):
                tokens.append(Token('RELOP', '>=', self.position))
                self.position += 2
                continue

            if self.text.startswith('==', self.position):
                tokens.append(Token('RELOP', '==', self.position))
                self.position += 2
                continue

            if self.text.startswith('!=', self.position):
                tokens.append(Token('RELOP', '!=', self.position))
                self.position += 2
                continue

            # Single-character comparison operators
            if char in '<>':
                token_map = {
                    '<': 'RELOP',
                    '>': 'RELOP',
                }
                tokens.append(Token(token_map[char], char, self.position))
                self.position += 1
                continue

            if char in '+-*/(){}':
                token_map = {
                    '+': 'PLUS',
                    '-': 'MINUS',
                    '*': 'STAR',
                    '/': 'SLASH',
                    '(': 'LPAREN',
                    ')': 'RPAREN',
                    '{': 'LBRACE',
                    '}': 'RBRACE',
                }
                tokens.append(Token(token_map[char], char, self.position))
                self.position += 1
                continue

            raise LexerError(f'Unexpected character {char!r} at position {self.position}')

        tokens.append(Token('EOF', None, self.position))
        return tokens

    def _read_word(self) -> str:
        start = self.position
        self.position += 1
        while self.position < len(self.text) and not self.text[self.position].isspace():
            if self.text[self.position] in '+-*/()':
                break
            self.position += 1
        return self.text[start:self.position]

    def _read_identifier(self) -> str:
        start = self.position
        while self.position < len(self.text) and (self.text[self.position].isalnum() or self.text[self.position] == '_'):
            self.position += 1
        return self.text[start:self.position]

    def _read_number(self) -> str:
        start = self.position
        while self.position < len(self.text) and self.text[self.position].isdigit():
            self.position += 1
        return self.text[start:self.position]

    def _read_string(self) -> str:
        self.position += 1  # Skip opening quote
        start = self.position
        while self.position < len(self.text) and self.text[self.position] != '"':
            self.position += 1
        string_content = self.text[start:self.position]
        if self.position < len(self.text):
            self.position += 1  # Skip closing quote
        return string_content