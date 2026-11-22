"""Integration tests for the command-line interface."""

import json
import subprocess
import sys


def test_cli_prints_json(tmp_path):
    source = tmp_path / "input.conf"
    source.write_text("global answer = 42e0;", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "src.configlang.cli", str(source)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert json.loads(result.stdout) == {"answer": 42.0}


def test_cli_reports_syntax_error(tmp_path):
    source = tmp_path / "broken.conf"
    source.write_text("global x = ;", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "src.configlang.cli", str(source)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "Ошибка:" in result.stderr
    assert result.stdout == ""
