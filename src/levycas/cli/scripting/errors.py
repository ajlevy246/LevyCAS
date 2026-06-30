"""Scripting-specific Exceptions"""

class ReferenceError(KeyError):
    pass

class ExecutionError(SystemError):
    pass