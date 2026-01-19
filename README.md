# django-returns

[![PyPI](https://img.shields.io/pypi/v/django-returns)](https://pypi.org/project/django-returns/)
[![Python Versions](https://img.shields.io/pypi/pyversions/django-returns?logo=python)](https://pypi.org/project/django-returns/)
![Django](https://img.shields.io/badge/django-4.2%20%7C%205.2%20%7C%206.0-0C4B33)
[![Docs](https://img.shields.io/badge/docs-brunodantas.github.io-0D9488)](https://brunodantas.github.io/django-returns)


Meaningful Django utils based on Functional Programming.

Made possible by [`returns`](https://returns.readthedocs.io/en/latest)

## Install

```bash
pip install django-returns
```

## What

`django-returns` is a tiny layer on top of Django’s ORM that lets you opt into
`returns` containers when you want explicit success/failure return types
instead of exceptions.

## How

By subclassing `QuerySet` and applying `returns` decorators to its methods.

Note: the default `ReturnsManager` does **not** change Django semantics. It keeps the original methods intact and adds new ones:

- `*_result` variants for sync operations (return `Success` / `Failure`)
- `*_ioresult` variants for both sync and async operations (return `IOSuccess` / `IOFailure`)
- `first_maybe()` / `last_maybe()` for "might be `None`" QS methods (return `Some` / `Nothing`)

## Safe ORM

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

Methods with the `_result` suffix return `returns.result.Result`.

```python
from returns.result import Failure, Result, Success


def get_person_name(person_id):
    result: Result = Person.objects.get_result(id=person_id)

    match result:
        case Success(person):
            return Success(person.name)
        case Failure(Person.DoesNotExist()):
            return ""
```

## IO Methods

Async/IO `*_ioresult` methods return an IO-wrapped result (`IOSuccess` / `IOFailure`).

```python
from returns.io import unsafe_perform_io
from returns.result import Failure, Success


async def get_person_id_async(name):
    io_result = await Person.objects.aget_ioresult(name=name)
    result = unsafe_perform_io(io_result)

    match result:
        case Success(person):
            return person.id
        case Failure(error):
            return -1
```
