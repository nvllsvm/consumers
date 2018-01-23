"""
Exceptions
==========
"""


class ConsumerError(Exception):
    """An exception in a consumer occurred."""


class QueueError(Exception):
    """An error occurred accessing a queue."""
