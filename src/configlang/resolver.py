
"""Resolve compile-time constants and build JSON-compatible values."""

from src.configlang.errors import ResolveError
from src.configlang.parser import Declaration, Reference, Value


class Resolver:
    """Evaluate declarations, including forward references."""

    def __init__(self, declarations: list[Declaration]) -> None:
        """Index declarations and prepare resolution state."""
        self.declarations = {}
        self.values = {}
        self.active = set()

        for declaration in declarations:
            name = declaration.name
            if name in self.declarations:
                message = (
                    f"Повторное объявление константы {name!r}: "
                    f"строка {declaration.line}, "
                    f"столбец {declaration.column}"
                )
                raise ResolveError(message)

            self.declarations[name] = declaration

    def resolve(self) -> dict[str, object]:
        """Return all declared constants as a JSON-compatible mapping."""
        for name in self.declarations:
            self._resolve_name(name)

        return self.values.copy()

    def _resolve_name(self, name: str) -> object:
        """Resolve one constant and detect dependency errors."""
        if name in self.values:
            return self.values[name]

        if name in self.active:
            message = (
                f"Обнаружена циклическая зависимость "
                f"константы {name!r}"
            )
            raise ResolveError(message)

        if name not in self.declarations:
            raise ResolveError(f"Неизвестная константа {name!r}")

        self.active.add(name)
        declaration = self.declarations[name]
        value = self._resolve_value(declaration.value)
        self.active.remove(name)

        self.values[name] = value
        return value

    def _resolve_value(self, value: Value) -> object:
        """Recursively replace references inside dictionaries."""
        if isinstance(value, Reference):
            return self._resolve_name(value.name)

        if isinstance(value, dict):
            return {
                key: self._resolve_value(item)
                for key, item in value.items()
            }

        return value


def resolve_constants(
    declarations: list[Declaration],
) -> dict[str, object]:
    """Resolve declarations into a JSON-compatible mapping."""
    return Resolver(declarations).resolve()
