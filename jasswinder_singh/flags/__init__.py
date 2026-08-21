"""Re-export absl.flags under jasswinder_singh.flags.

When `absl.flags` is not available we provide minimal DEFINE_* helpers and
a simple `FLAGS` object so imports won't fail at import time.
"""
try:
    import absl.flags as _absl_flags  # type: ignore
    for _name in dir(_absl_flags):
        if not _name.startswith('__'):
            globals()[_name] = getattr(_absl_flags, _name)
    __all__ = [n for n in globals().keys() if not n.startswith('_')]
except Exception:
    _flag_store = {}

    def DEFINE_string(name, default='', help=''):
        _flag_store[name] = default

    def DEFINE_integer(name, default=0, help=''):
        _flag_store[name] = default

    def DEFINE_bool(name, default=False, help=''):
        _flag_store[name] = default

    class _FLAGS:
        def __getattr__(self, name):
            return _flag_store.get(name)

    FLAGS = _FLAGS()
    __all__ = ['DEFINE_string', 'DEFINE_integer', 'DEFINE_bool', 'FLAGS']
