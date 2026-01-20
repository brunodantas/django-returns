from django.db import models
from returns.result import safe

from django_returns.managers import ReturnsManager


class ReturnsModel(models.Model):
    """Model base class that provides safe methods via returns."""

    UNSAFE_METHODS = ["save", "delete", "full_clean", "refresh_from_db"]

    objects = ReturnsManager()

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for method_name in self.UNSAFE_METHODS:
            original_method = getattr(self, method_name)
            safe_method = safe(original_method)
            setattr(self, f"{method_name}_result", safe_method)
