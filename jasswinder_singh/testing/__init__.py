"""Shim package re-exporting absl.testing under jasswinder_singh.testing.

When `absl.testing` isn't available we provide lightweight fallbacks so
tests and imports don't fail immediately.
"""
try:
    from absl.testing import absltest as absltest  # type: ignore
    from absl.testing import parameterized as parameterized  # type: ignore
    from absl.testing import flagsaver as flagsaver  # type: ignore
except Exception:
    import unittest as absltest

    def parameterized(params):
        def _decorator(fn):
            return fn
        return _decorator

    class flagsaver:
        def __enter__(self):
            return None
        def __exit__(self, exc_type, exc, tb):
            return False

__all__ = ['absltest', 'parameterized', 'flagsaver']
