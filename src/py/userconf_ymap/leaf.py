
class ConfigError(ValueError):
    """A color, font, or size in argv or X resources is unusable."""

class RunTimeError(OSError): ""

class ContextError(RunTimeError): ""

# vim:fenc=utf-8
