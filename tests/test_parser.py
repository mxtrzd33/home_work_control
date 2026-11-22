"""Tests for syntax parsing and nested structures."""

import pytest

from src.configlang.errors import ParseError
from src.configlang.parser import Reference, parse_source


def test_parses_global_number():
    declarations = parse_source("global count = 10e0;")
    assert declarations[0].name == "count"
    assert declarations[0].value == 10.0


def test_parses_nested_dictionary():
    source = "global cfg = @{a = 1e0; b = @{c = 2e0;};};"
    value = parse_source(source)[0].value
    assert value == {"a": 1.0, "b": {"c": 2.0}}


def test_parses_reference():
    value = parse_source("global x = #(later);")[0].value
    assert isinstance(value, Reference)
    assert value.name == "later"


def test_parses_empty_dictionary():
    assert parse_source("global empty = @{};")[0].value == {}


@pytest.mark.parametrize("source", [
    "global x = 1e0",
    "global = 1e0;",
    "global x 1e0;",
    "global x = ;",
    "global x = @{a = 1e0};",
    "global x = @{a = 1e0; a = 2e0;};",
    "global x = #(name;",
])
def test_rejects_invalid_syntax(source):
    with pytest.raises(ParseError):
        parse_source(source)


def test_reports_source_location():
    with pytest.raises(ParseError, match="строка 2"):
        parse_source("global x = 1e0;\nglobal y = ;")
