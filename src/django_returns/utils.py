from returns.result import Result, safe
from returns.unsafe import unsafe_perform_io as _unsafe_perform_io


@safe
def getattr_safe(obj, name) -> Result:
    """Safe version of getattr that returns a Result."""
    return getattr(obj, name)


def unsafe_perform_io(io):
    """Unwraps IOResult."""
    return _unsafe_perform_io(io)
