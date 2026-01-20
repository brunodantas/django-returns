from typing import TypeVar

from django.db import models
from returns.result import Result

from django_returns.managers import ReturnsManager

_M = TypeVar("_M", bound="ReturnsModel")

class ReturnsModel(models.Model):
    """Model base class that provides safe methods via returns."""

    objects: ReturnsManager

    def save_result(self, *args, **kwargs) -> Result[None, Exception]: ...
    def delete_result(
        self, *args, **kwargs
    ) -> Result[tuple[int, dict[str, int]], Exception]: ...
    def full_clean_result(self, *args, **kwargs) -> Result[None, Exception]: ...
    def refresh_from_db_result(self, *args, **kwargs) -> Result[None, Exception]: ...
