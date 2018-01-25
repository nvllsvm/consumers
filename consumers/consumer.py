"""
Consumers
=========
"""


class Consumer:
    """Base consumer class.

    Any parameters passed during instantiation will be passed to the
    :py:meth:`initialize` method upon process creation.
    """

    def __init__(self, *args, **kwargs):
        self.init_args = args
        self.init_kwargs = kwargs

    def _process_init(self, name, logger):
        self._name = name
        self._logger = logger
        self.initialize(*self.init_args, **self.init_kwargs)

    @property
    def logger(self):
        """A :py:class:`logging.Logger` instance configured with the
        :py:attr:`name` of the consumer."""
        return self._logger

    @property
    def name(self):
        """The unique name of the consumer."""
        return self._name

    def initialize(self, *args, **kwargs):
        """Initialize the consumer process.

        Can optionally be overriden. Default implementation does nothing.
        """
        pass

    def process(self, *args, **kwargs):
        """Implement this method to process a single item from the queue."""
        raise NotImplementedError

    def shutdown(self):
        """Run when the consumer is shutting down.

        Can optionally be overriden. Default implementation does nothing.

        Any value returned by this function will be appended to
        :py:attr:`consumers.Queue.results` upon the queue stopping.
        """
        pass
