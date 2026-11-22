"""Domain exceptions with source-location diagnostics."""


class ConfigError(Exception):
    """Base class for configuration language errors."""


class LexError(ConfigError):
    """Raised when the lexer encounters an invalid token."""


class ParseError(ConfigError):
    """Raised when the token sequence violates the grammar."""


class ResolveError(ConfigError):
    """Raised when constants cannot be resolved."""
