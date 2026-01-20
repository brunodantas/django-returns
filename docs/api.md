# API Reference

This page documents the method families added by `ReturnsManager`.

## Method Matrix

For each unsafe ORM method, `django-returns` generates safe variants:

| ORM Method | Sync Result | Sync IOResult | Async IOResult |
|------------|-------------|---------------|----------------|
{% for method in ["get", "earliest", "latest", "create", "get_or_create", "update_or_create", "delete", "bulk_create"] -%}
| `{{ method }}` | `{{ method }}_result` | `{{ method }}_ioresult` | `a{{ method }}_ioresult` |
{% endfor %}

Plus: `first_maybe()`, `last_maybe()` for optional results.

## Result Methods (Sync)

Use these when you want explicit success/failure without exception handling.

```python
get_result(**kwargs) -> Result[Model, Exception]
create_result(**kwargs) -> Result[Model, Exception]
get_or_create_result(**kwargs) -> Result[tuple[Model, bool], Exception]
update_or_create_result(**kwargs) -> Result[tuple[Model, bool], Exception]
delete_result() -> Result[tuple[int, dict[str, int]], Exception]
bulk_create_result(objs) -> Result[list[Model], Exception]
earliest_result(*fields) -> Result[Model, Exception]
latest_result(*fields) -> Result[Model, Exception]
```

### Example

```python
from returns.result import Success, Failure

result = Person.objects.get_result(id=1)

match result:
    case Success(person):
        print(f"Found: {person.name}")
    case Failure(Person.DoesNotExist()):
        print("Person not found")
    case Failure(error):
        print(f"Unexpected error: {error}")
```


## IOResult Methods (Sync)

Use these when you want to track that a method performs side effects (database access).

**Signatures:** Same as Result methods, but return `IOResult[...]` instead.

### Example

```python
from returns.io import unsafe_perform_io
from returns.result import Success, Failure

io_result = Person.objects.get_ioresult(id=1)
result = unsafe_perform_io(io_result)  # Explicit IO boundary

match result:
    case Success(person):
        ...
    case Failure(error):
        ...
```

## IOResult Methods (Async)

Use these for async ORM operations with explicit IO tracking.

**Signatures:** Same as Result methods, but return `FutureResult[...]` instead.


### Example

```python
from returns.io import unsafe_perform_io
from returns.result import Success, Failure

async def get_person_async(person_id):
    future_result = Person.objects.aget_ioresult(id=person_id)
    io_result = await future_result
    result = unsafe_perform_io(io_result)  # Unwrap at boundary

    match result:
        case Success(person):
            return person.name
        case Failure(error):
            return None
```

## Maybe Methods

Use these when a result might be `None`.

**Methods:** `first_maybe()`, `last_maybe()`

**Returns:** `Maybe[Model]`


### Example

```python
from returns.maybe import Some, Nothing

maybe_person = Person.objects.filter(name="Ada").first_maybe()

match maybe_person:
    case Some(person):
        print(f"Found: {person.name}")
    case Nothing:
        print("No match")
```

## Quick Reference

### When to use what?

- **`*_result`**: Sync operations, explicit success/failure, no IO tracking needed
- **`*_ioresult`**: Sync operations where you want IO tracking explicit
- **`a*_ioresult`**: Async operations (IO is always explicit)
- **`*_maybe`**: When `None` is a valid empty state (not an error)

### Pattern: Unwrapping at boundaries

Keep containers (`Result`, `IOResult`, `Maybe`) in your business logic. Unwrap only at application boundaries (views, commands, handlers).

```python
from django.http import JsonResponse
from returns.result import Result, Success, Failure

# Service layer: return containers
def get_user_by_email(email: str) -> Result[User, Exception]:
    return User.objects.get_result(email=email)

# View layer: unwrap and handle
def user_view(request):
    result = get_user_by_email(request.GET['email'])
    match result:
        case Success(user):
            return JsonResponse({'name': user.name})
        case Failure(error):
            return JsonResponse({'error': str(error)}, status=404)
```

### Chaining operations

Use `returns` combinators (`bind`, `map`, `alt`) to chain operations without nested match statements. See the [returns documentation](https://returns.readthedocs.io/) for details.

