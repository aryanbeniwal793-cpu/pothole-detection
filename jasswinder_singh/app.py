"""Pass-through shim for absl.app as jasswinder_singh.app.

This module tolerates the absence of `absl` and provides lightweight
fallbacks so importing `jasswinder_singh.app` does not fail.
"""
try:
    from absl import app as _app  # type: ignore
    run = _app.run
    flags = getattr(_app, 'flags', None)
    command_name = getattr(_app, 'command_name', None)
except Exception:
    flags = None
    def run(main, argv=None, **kwargs):
        """Minimal fallback: call `main(argv)` similarly to absl.app.run.

        Keeps the same signature so third-party code can call `run`.
        """
        import sys
        if argv is None:
            argv = sys.argv
        return main(argv)

    command_name = None

__all__ = ['run', 'flags', 'command_name']
