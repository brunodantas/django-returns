from django.db import models
from returns.result import safe

from django_returns.managers import ReturnsManager


class ReturnsModel(models.Model):
    """Model base class that provides safe methods via returns."""

    objects = ReturnsManager()

    class Meta:
        abstract = True

    def __getattr__(self, name):
        if name.endswith("_safe"):
            base_method = name[:-5]
            if hasattr(self, base_method):
                original_method = getattr(self, base_method)
                return safe(original_method)

        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )
