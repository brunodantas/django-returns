from django.db.models import Manager, QuerySet
from returns.result import safe
from returns.maybe import maybe


class ReturnsQueryset(QuerySet):
    """QuerySet implementation including new methods
    that return Result instead of raising exceptions.
    """

    def __getattr__(self, name):
        if name.endswith("_safe"):
            base_method = name[:-5]
            if hasattr(self, base_method):
                original_method = getattr(self, base_method)
                return safe(original_method)

        raise AttributeError(f"{self.__class__.__name__} has no attribute {name}")

    @maybe
    def first_maybe(self, *args, **kwargs):
        return self.first(*args, **kwargs)

    @maybe
    def last_maybe(self, *args, **kwargs):
        return self.last(*args, **kwargs)


class ReturnsManager(Manager):
    """Manager implementation that uses ReturnsQueryset
    and includes new methods that return Result instead of raising exceptions.
    """
    
    def get_queryset(self):
        return ReturnsQueryset(self.model, using=self._db)
    
    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        return getattr(self.get_queryset(), name)
