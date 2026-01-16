from returns.result import Result, safe


@safe
def getattr_safe(obj, name) -> Result:
    """Safe version of getattr that returns a Result."""
    return getattr(obj, name)
