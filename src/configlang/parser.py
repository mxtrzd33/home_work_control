
"""Recursive-descent parser for configuration declarations."""

from dataclasses import dataclass
from typing import TypeAlias

from src.configlang.errors import ParseError
from src.configlang.lexer import Lexer, Token


@dataclass(frozen=True)
class Reference:
    """A reference to a compile-time global constant."""

    name: str
    line: int
    column: int


Value: TypeAlias = float | dict[str, "Value"] | Reference


@dataclass(frozen=True)
class Declaration:
    """A global constant declaration."""

    name: str
    value: Value
    line: int
    column: int


class Parser:
    """Parse a sequence of global declarations."""

    def __init__(self, tokens: list[Token]) -> None:
        """Initialize the parser with a complete token stream."""
        self.tokens = tokens
        self.position = 0

    def parse(self) -> list[Declaration]:
        """Parse the whole program and reject trailing unexpected tokens."""
        declarations = []
        while self._current().kind != "EOF":
            declarations.append(self._parse_declaration())
        return declarations

    def _parse_declaration(self) -> Declaration:
        """Parse `global name = value;`."""
        start = self._expect("GLOBAL")
        name = self._expect("IDENT")
        self._expect("EQUAL")
        value = self._parse_value()
        self._expect("SEMI")
        return Declaration(name.value, value, start.line, start.column)

    def _parse_value(self) -> Value:
        """Parse a number, dictionary, or constant reference."""
        token = self._current()
        if token.kind == "NUMBER":
            self.position += 1
            return float(token.value)
        if token.kind == "DICT_START":
            return self._parse_dictionary()
        if token.kind == "REF_START":
            return self._parse_reference()

        message = "Ожидалось число, словарь или ссылка на константу"
        self._fail(token, message)

    def _parse_dictionary(self) -> dict[str, Value]:
        """Parse a dictionary with semicolon-terminated entries."""
        self._expect("DICT_START")
        result = {}

        while self._current().kind != "RBRACE":
            name = self._expect("IDENT")
            if name.value in result:
                message = f"Повторный ключ словаря {name.value!r}"
                self._fail(name, message)

            self._expect("EQUAL")
            result[name.value] = self._parse_value()
            self._expect("SEMI")

        self._expect("RBRACE")
        return result

    def _parse_reference(self) -> Reference:
        """Parse a compile-time reference in the form `#(name)`."""
        start = self._expect("REF_START")
        name = self._expect("IDENT")
        self._expect("RPAREN")
        return Reference(name.value, start.line, start.column)

    def _expect(self, kind: str) -> Token:
        """Consume a token of the expected kind or raise a located error."""
        token = self._current()
        if token.kind != kind:
            message = f"Ожидался токен {kind}, получен {token.kind}"
            self._fail(token, message)

        self.position += 1
        return token

    def _current(self) -> Token:
        """Return the token at the current parser position."""
        return self.tokens[self.position]

    @staticmethod
    def _fail(token: Token, message: str) -> None:
        """Raise a syntax error with line and column information."""
        location = f"строка {token.line}, столбец {token.column}"
        raise ParseError(f"{message}: {location}")


def parse_source(source: str) -> list[Declaration]:
    """Tokenize and parse source text into declarations."""
    return Parser(Lexer(source).tokenize()).parse()
