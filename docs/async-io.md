# Async Methods

Keeping the pattern established by `returns`, `django-returns`' Async ORM calls
make IO operations explicit by **returning IO-tracked containers**.

With this:

- Async safe methods are exposed as `a*_ioresult` (e.g. `aget_ioresult`).
- They return `returns.future.FutureResult`, which is awaitable.
- When awaited, you get an `IOResult`.

## Unwrapping `IOResult`

Use an explicit boundary where you decide to "run" effects:

```python
from returns.future import FutureResult
from returns.io import IOResult, unsafe_perform_io
from returns.result import Result

future_result: FutureResult = Person.objects.aget_ioresult(name="Guido")
io_result: IOResult = await future_result
result = unsafe_perform_io(io_result)
assert isinstance(result, Result)
```

Note: it's generally recommended to keep such side effects
at the edges of the application, i.e. `functional core, imperative shell`.

- Unwrap in the outermost layer (views/commands/handlers).
- Keep services pure where possible by passing containers around.
