class Consumer:
    """Base consumer class."""

    def __init__(self, *args, **kwargs):
        self.init_args = args
        self.init_kwargs = kwargs

    def _process_init(self, name, logger):
        self.name = name
        self.logger = logger
        self.initialize(*self.init_args, **self.init_kwargs)

    def initialize(self, *args, **kwargs):
        """Initialize the consumer."""
        pass

    def process(self, *args, **kwargs):
        """Process an item from the queue."""
        raise NotImplementedError

    def shutdown(self):
        """Run when the consumer is shutting down."""
        pass
