"""Tests for compile-time constant evaluation."""

import pytest

from src.configlang.errors import ResolveError
from src.configlang.parser import parse_source
from src.configlang.resolver import resolve_constants


def translate(source):
    """Parse and resolve a source string."""
    return resolve_constants(parse_source(source))


def test_resolves_simple_constant():
    assert translate("global x = 2e0;") == {"x": 2.0}


def test_resolves_forward_reference():
    source = "global first = #(second); global second = 3e0;"
    assert translate(source) == {"second": 3.0, "first": 3.0}


def test_resolves_nested_references():
    source = "global n = 4e0; global cfg = @{a = #(n);};"
    assert translate(source) == {"n": 4.0, "cfg": {"a": 4.0}}


def test_resolves_reference_to_dictionary():
    source = "global base = @{port = 8e3;}; global app = #(base);"
    assert translate(source)["app"] == {"port": 8000.0}


def test_rejects_unknown_reference():
    with pytest.raises(ResolveError, match="Неизвестная"):
        translate("global x = #(missing);")


def test_rejects_duplicate_globals():
    with pytest.raises(ResolveError, match="Повторное"):
        translate("global x = 1e0; global x = 2e0;")


def test_rejects_cyclic_references():
    source = "global a = #(b); global b = #(a);"
    with pytest.raises(ResolveError, match="циклическая"):
        translate(source)


def test_rejects_duplicate_nested_key():
    source = "global x = @{a = 1e0; a = 2e0;};"
    from src.configlang.errors import ParseError
    with pytest.raises(ParseError):
        parse_source(source)
