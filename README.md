# django-returns

![CI](https://github.com/brunodantas/django-returns/actions/workflows/ci.yml/badge.svg)
[![PyPI](https://img.shields.io/pypi/v/django-returns)](https://pypi.org/project/django-returns/)
[![Python Versions](https://img.shields.io/pypi/pyversions/django-returns)](https://pypi.org/project/django-returns/)
![Django](https://img.shields.io/badge/django-4.2%20%7C%205.2%20%7C%206.0-0C4B33)

Meaningful Django utils based on Functional Programming.

> Made possible by [`returns`](https://returns.readthedocs.io/en/latest)

## What

`django-returns` is a tiny layer on top of Django’s ORM that lets you opt into
`returns` containers when you want explicit success/failure return types
instead of exceptions.

## How

By subclassing `QuerySet` and applying `returns` decorators to its methods.

Note: the default `ReturnsManager` does **not** change Django semantics. It keeps the original methods intact and adds new ones:

- `*_safe` variants for exception-raising operations (return `Success` / `Failure`)
- `first_maybe()` / `last_maybe()` for “might be empty” queries (return `Some` / `Nothing`)
- async `*_safe` variants which return an IO-wrapped `Result` and can be unwrapped
  with `django_returns.utils.unsafe_perform_io`

### Opt-in Safety With `*_safe` Suffix

Enable it by using the provided base model.

```python
from django_returns.models import ReturnsModel


class Person(ReturnsModel):
    name = models.CharField(max_length=255, unique=True)
```

Or by using the custom Manager.

```python
from django_returns.managers import ReturnsManager


class Person(models.Model):
    objects = ReturnsManager()
```

## Basic Usage

Methods with the `_safe` suffix return `returns.result.Result`.

```python
from returns.result import Failure, Success

from .models import Person


def get_person_name(person_id):
    result: Result = Person.objects.get_safe(id=person_id)

    match result:
        case Success(person):
            return Success(person.name)
        case Failure(Person.DoesNotExist()):
            return ""
```

## Async Methods

Async `*_safe` methods return an IO-wrapped result (`IOSuccess` / `IOFailure`).

```python
from django_returns.utils import unsafe_perform_io
from returns.result import Failure, Success

from .models import Person


async def get_person_id_async(name):
    io_result = await Person.objects.aget_safe(name=name)
    result = unsafe_perform_io(io_result)

    match result:
        case Success(person):
            return person.id
        case Failure(error):
            return -1
```
