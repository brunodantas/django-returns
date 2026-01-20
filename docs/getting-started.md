# Getting Started

## Prerequisites

`django-returns` is tested on Python 3.10+ and Django 4.2+

## Install

```bash
pip install django-returns
```

## Safe ORM

There are currently two options for using the safe ORM methods.

- Subclassing `ReturnsManager`
- Subclassing `ReturnsModel`

Note that the second option comes with more functionality.

### `ReturnsManager`

Includes `queryset.*_result` and `queryset.*_ioresult` methods for unsafe methods,
which are defined as follows.

```python
--8<-- "src/django_returns/managers.py:13:22"
```

Example:

```python
from django.db import models
from django_returns.managers import ReturnsManager
from returns.result import Failure, Success


class Person(models.Model):
    name = models.CharField(max_length=100, unique=True)
    dob = models.DateField()

    objects = ReturnsManager()


result = Person.objects.create_result(name="test", dob=date(2020, 1, 1))
assert isinstance(result, Success)
```

### `ReturnsModel`

Includes `queryset.*_result` and `queryset.*_ioresult` methods
plus `model.*_result` methods for `save`, `delete` etc.

Example:

```python
from django.db import models
from django_returns.models import ReturnsModel
from returns.result import Failure, Success


class Person(ReturnsModel):
    name = models.CharField(max_length=255, unique=True)


creation_result = Person.objects.create_result(name="test", dob=date(2020, 1, 1))
person = result.unwrap()
deletion_result = person.delete_result()
assert isinstance(deletion_result, Success)
```

## Recap

Compared to standard Django ORM, `django-returns` classes:

- Keep the existing Django ORM behavior.
- Adds new methods with suffixes:
    - `*_result` for sync operations
    - `*_ioresult` for sync + async operations
    - `first_maybe()` / `last_maybe()` for optional results
