"""Consumers is a simple, flexible way to parallelize processing."""

import logging
import multiprocessing
import time


STATUS_DONE = 'done'
"""Queue item value which informs a consumer it is done"""


class ConsumerError(Exception):
    """An exception in a consumer occurred."""


class Consumer(multiprocessing.Process):
    """Base consumer class."""

    def __init__(self, queue, init_args, init_kwargs):
        super().__init__()
        self.queue = queue
        self.logger = logging.getLogger(self.name)

        init_args = init_args or ()
        init_kwargs = init_kwargs or {}
        self.initialize(*init_args, **init_kwargs)

    def initialize(self, *args, **kwargs):
        """Initialize the consumer."""
        pass

    def process(self, *args, **kwargs):
        """Process an item from the queue."""
        raise NotImplementedError

    def shutdown(self):
        """Run when the consumer is shutting down."""
        pass

    def run(self):
        """Consume events from the queue"""
        while True:
            try:
                item = self.queue.get(True)
                if item == STATUS_DONE:
                    break
                self.process(*item['args'], **item['kwargs'])
            except Exception as exception:
                self.logger.exception(exception)
                raise

        self.shutdown()


class Queue:
    """A queue with consumers."""

    PROCESS_ALIVE_TIMEOUT = 0.1
    """Time between loops when checking if all processes are done."""

    def __init__(self, factory, num_consumers=multiprocessing.cpu_count(),
                 init_args=None, init_kwargs=None):
        self.logger = logging.getLogger(__name__)
        self.factory = factory
        self.num_consumers = num_consumers
        self.consumers = []
        self._queue = multiprocessing.Queue()

        self.init_args = init_args or ()
        self.init_kwargs = init_kwargs or {}

    def __enter__(self):
        """Start the consumers upon entering a runtime context."""
        for _ in range(self.num_consumers):
            process = self.factory(self._queue, self.init_args,
                                   self.init_kwargs)
            process.start()
            self.consumers.append(process)

        return self

    def __exit__(self, *args):
        """Cleanup the consumers upon exiting a runtime context."""
        self.set_done()

        while True:
            if not any(c.is_alive() for c in self.consumers):
                break
            time.sleep(self.PROCESS_ALIVE_TIMEOUT)

        consumer_error = False
        for consumer in self.consumers:
            if consumer.exitcode:
                consumer_error = True
                self.logger.error('%s exited with %d', consumer.name,
                                  consumer.exitcode)

        if consumer_error:
            raise ConsumerError

    def put(self, *args, **kwargs):
        """Enqueue a pair `*args` and `**kwargs` to be passed to a consumer's
        :py:method:`consumers.Consumer.process` method.
        """
        self._queue.put({
            'args': args,
            'kwargs': kwargs})

    def set_done(self):
        """Enqueue a signal to inform consumers that no more data will be added
        to the queue.
        """
        for _ in self.consumers:
            self._queue.put(STATUS_DONE)
