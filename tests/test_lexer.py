"""Tests for lexical analysis."""

import pytest

from src.configlang.errors import LexError
from src.configlang.lexer import Lexer


def test_tokenizes_comment_and_number():
    tokens = Lexer("NB. note\nglobal x = -1.25E+2;").tokenize()
    assert [token.kind for token in tokens] == [
        "GLOBAL", "IDENT", "EQUAL", "NUMBER", "SEMI", "EOF"
    ]
    assert tokens[3].value == "-1.25E+2"


@pytest.mark.parametrize("number", ["1e0", "-2.5E+3", "+7.0e-2", "123.4e5"])
def test_accepts_valid_number(number):
    assert Lexer(number).tokenize()[0].value == number


@pytest.mark.parametrize("number", ["12", "1.", ".5e2", "1e", "+abc", "@"])
def test_rejects_invalid_number_or_token(number):
    with pytest.raises(LexError):
        Lexer(number).tokenize()


def test_recognizes_dictionary_and_reference():
    kinds = [item.kind for item in Lexer("@{x=#(y);}").tokenize()]
    assert kinds == ["DICT_START", "IDENT", "EQUAL", "REF_START",
                     "IDENT", "RPAREN", "SEMI", "RBRACE", "EOF"]


def test_identifier_rules():
    tokens = Lexer("name_9").tokenize()
    assert tokens[0].kind == "IDENT"
    assert tokens[0].value == "name_9"


def test_identifier_cannot_start_with_underscore():
    with pytest.raises(LexError):
        Lexer("_name").tokenize()
