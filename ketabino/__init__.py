import sys


def _patch_django_py314_context_copy():
    """Fix Django 4.2 BaseContext.__copy__ incompatibility with Python 3.14."""
    if sys.version_info < (3, 14):
        return
    try:
        import django
        from django.template.context import BaseContext

        if django.VERSION < (5, 2):
            def _fixed_copy(self):
                duplicate = object.__new__(self.__class__)
                duplicate.__dict__ = self.__dict__.copy()
                duplicate.dicts = self.dicts[:]
                return duplicate

            BaseContext.__copy__ = _fixed_copy
    except Exception:
        pass


_patch_django_py314_context_copy()
