
class ConfigError(ValueError):
    """An error in configuration loading or processing occured."""

class RunTimeError:
    """An error during processing occured."""

class ContextError(RunTimeError, OSError):
    """An external error during processing occured."""

# vim:fenc=utf-8
