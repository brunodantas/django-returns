from typing import TypeAlias, TypeVar

from django.db import models
from returns.result import Failure, Success

from django_returns.managers import ReturnsManager

_M = TypeVar("_M", bound="ReturnsModel")
_Value = TypeVar("_Value")
_Error = TypeVar("_Error", bound=Exception)

MatchResult: TypeAlias = Success[_Value] | Failure[_Error]

class ReturnsModel(models.Model):
    """Model base class that provides safe methods via returns."""

    objects: ReturnsManager

    def save_result(self, *args, **kwargs) -> MatchResult[None, Exception]: ...
    def delete_result(
        self, *args, **kwargs
    ) -> MatchResult[tuple[int, dict[str, int]], Exception]: ...
    def full_clean_result(self, *args, **kwargs) -> MatchResult[None, Exception]: ...
    def refresh_from_db_result(
        self, *args, **kwargs
    ) -> MatchResult[None, Exception]: ...
