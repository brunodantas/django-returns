from django.db.models import Manager, QuerySet
from returns.future import future_safe
from returns.io import impure_safe
from returns.maybe import maybe
from returns.result import safe


class BaseReturnsQuerySet(QuerySet):
    """QuerySet implementation including new methods
    that return Result instead of raising exceptions.
    """

    UNSAFE_METHODS = [
        "get",
        "earliest",
        "latest",
        "create",
        "get_or_create",
        "update_or_create",
        "delete",
        "bulk_create",
    ]


class MaybeReturnsQuerySet(BaseReturnsQuerySet):
    """A subclass that includes Maybe-returning methods."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for method_name in ["first", "last"]:
            original_method = getattr(self, method_name)
            maybe_method = maybe(original_method)
            setattr(self, method_name, maybe_method)


class SafeReturnsQuerySet(MaybeReturnsQuerySet):
    """A subclass that overrides unsafe methods
    to return Result instead of raising exceptions.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for method_name in self.UNSAFE_METHODS:
            original_method = getattr(self, method_name)
            safe_method = safe(original_method)
            setattr(self, method_name, safe_method)


class ImpureReturnsQuerySet(MaybeReturnsQuerySet):
    """A subclass that overrides unsafe methods
    to return IOResult instead of raising exceptions.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for method_name in self.UNSAFE_METHODS:
            original_method = getattr(self, method_name)
            impure_safe_method = impure_safe(original_method)
            setattr(self, method_name, impure_safe_method)


class IncrementedReturnsQuerySet(BaseReturnsQuerySet):
    """A subclass that includes safe versions (ending with _safe)
    of unsafe methods that can be used separately from the original methods."""

    def __getattr__(self, name):
        """Dynamically provide safe versions of QuerySet methods."""
        if name.endswith("_safe"):
            base_method = name[:-5]
            if hasattr(self, base_method):
                original_method = getattr(self, base_method)
                if base_method.startswith("a"):
                    # Async method
                    return future_safe(original_method)
                return safe(original_method)

        raise AttributeError(f"{self.__class__.__name__} has no attribute {name}")

    @maybe
    def first_maybe(self, *args, **kwargs):
        return self.first(*args, **kwargs)

    @maybe
    def last_maybe(self, *args, **kwargs):
        return self.last(*args, **kwargs)


class ReturnsManager(Manager):
    """Manager that selects a QuerySet according to init params
    and defaults to IncrementedReturnsQuerySet.
    """

    def __init__(
        self, override_with_safe=False, override_with_impure=False, *args, **kwargs
    ):
        self._override_with_safe = override_with_safe
        self._override_with_impure = override_with_impure
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        if self._override_with_safe:
            return SafeReturnsQuerySet(self.model, using=self._db)
        if self._override_with_impure:
            return ImpureReturnsQuerySet(self.model, using=self._db)

        return IncrementedReturnsQuerySet(self.model, using=self._db)

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )
        return getattr(self.get_queryset(), name)
