"""Pass-through shim for absl.logging as jasswinder_singh.logging.

Provides a graceful fallback to the standard library `logging` when
`absl` is not available.
"""
try:
    from absl import logging as _logging  # type: ignore
    set_verbosity = _logging.set_verbosity
    INFO = _logging.INFO
    WARNING = _logging.WARNING
    ERROR = _logging.ERROR
    FATAL = _logging.FATAL
    DEBUG = getattr(_logging, 'DEBUG', None)
    get_verbosity = getattr(_logging, 'get_verbosity', None)
except Exception:
    import logging as _logging
    def set_verbosity(level):
        _logging.getLogger().setLevel(level)

    INFO = _logging.INFO
    WARNING = _logging.WARNING
    ERROR = _logging.ERROR
    FATAL = _logging.FATAL
    DEBUG = getattr(_logging, 'DEBUG', None)
    def get_verbosity():
        return _logging.getLogger().level

__all__ = ['set_verbosity', 'INFO', 'WARNING', 'ERROR', 'FATAL', 'DEBUG', 'get_verbosity']
