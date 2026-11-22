
"""Tokenize the educational configuration language."""

import re
from dataclasses import dataclass

from src.configlang.errors import LexError

NUMBER = r"[+-]?\d+\.?\d*[eE][+-]?\d+"
NAME_START = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
NAME_BODY = NAME_START + "_0123456789"


@dataclass(frozen=True)
class Token:
    """A token with its original source location."""

    kind: str
    value: str
    line: int
    column: int


class Lexer:
    """Convert source text into a stream of tokens."""

    def __init__(self, source: str) -> None:
        """Initialize a lexer for the supplied source text."""
        self.source = source
        self.index = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> list[Token]:
        """Return all tokens, including the final EOF token."""
        tokens = []
        while self.index < len(self.source):
            char = self.source[self.index]
            if char.isspace():
                self._advance(char)
            elif self.source.startswith("NB.", self.index):
                self._skip_comment()
            else:
                tokens.append(self._read_token())

        tokens.append(Token("EOF", "", self.line, self.column))
        return tokens

    def _read_token(self) -> Token:
        """Read one number, identifier, or punctuation token."""
        line, column = self.line, self.column

        if self.source.startswith("@{", self.index):
            self._advance("@{")
            return Token("DICT_START", "@{", line, column)

        if self.source.startswith("#(", self.index):
            self._advance("#(")
            return Token("REF_START", "#(", line, column)

        char = self.source[self.index]
        punctuation = {
            "=": "EQUAL",
            ";": "SEMI",
            "}": "RBRACE",
            ")": "RPAREN",
        }

        if char in punctuation:
            self._advance(char)
            return Token(punctuation[char], char, line, column)

        if char in "+-" or char.isdigit():
            number = self._read_number()
            return Token("NUMBER", number, line, column)

        if char in NAME_START:
            name = self._read_name()
            kind = "GLOBAL" if name == "global" else "IDENT"
            return Token(kind, name, line, column)

        message = (
            f"Недопустимый символ {char!r}: "
            f"строка {line}, столбец {column}"
        )
        raise LexError(message)

    def _read_number(self) -> str:
        """Read a number matching the required exponent-based pattern."""
        start = self.index

        while self.index < len(self.source):
            char = self.source[self.index]
            if char.isalnum() or char in ".+-":
                self._advance(char)
            else:
                break

        value = self.source[start:self.index]
        if not re.fullmatch(NUMBER, value):
            column = self.column - len(value)
            message = (
                f"Некорректное число {value!r}: "
                f"строка {self.line}, столбец {column}"
            )
            raise LexError(message)

        return value

    def _read_name(self) -> str:
        """Read an identifier beginning with an ASCII letter."""
        start = self.index

        while self.index < len(self.source):
            char = self.source[self.index]
            if char in NAME_BODY:
                self._advance(char)
            else:
                break

        return self.source[start:self.index]

    def _skip_comment(self) -> None:
        """Skip a comment through, but not including, the newline."""
        while self.index < len(self.source):
            char = self.source[self.index]
            if char == "\n":
                break
            self._advance(char)

    def _advance(self, text: str) -> None:
        """Advance the cursor and update line and column counters."""
        for char in text:
            self.index += 1
            if char == "\n":
                self.line += 1
                self.column = 1
            else:
                self.column += 1
