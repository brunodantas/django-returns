from django.db import models
from returns.result import Result

from django_returns.managers import ReturnsManager

class ReturnsModel(models.Model):
    """Model base class that provides safe methods via returns."""

    objects: ReturnsManager

    def save_safe(self, *args, **kwargs) -> Result: ...
    def delete_safe(self, *args, **kwargs) -> Result: ...
    def full_clean_safe(self, *args, **kwargs) -> Result: ...
    def refresh_from_db_safe(self, *args, **kwargs) -> Result: ...
