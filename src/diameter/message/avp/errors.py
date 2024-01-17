"""
Common message handling errors.
"""


class AvpDecodeError(Exception):
    """An exception raised when an AVP value contains data that cannot be
    decoded into a python type."""
    pass


class AvpEncodeError(Exception):
    """An exception raised when a value of an AVP has been set to something
    that the AVP type cannot encode."""
    pass
