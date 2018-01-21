"""Consumers is a simple, flexible way to parallelize processing."""

import logging
import multiprocessing
import time


STATUS_DONE = 'done'
"""Queue item value which informs a consumer it is done"""


class ConsumerError(Exception):
    """An exception in a consumer occurred."""


class QueueError(Exception):
    """An error occurred accessing a queue."""


class Process(multiprocessing.Process):
    """Base process class."""

    def __init__(self, queue, process_number):
        super().__init__()
        self.queue = queue
        self.consumer = self.queue.consumer(*self.queue.init_args,
                                            **self.queue.init_kwargs)
        self.name = '{}-{}'.format(self.queue.consumer.__name__,
                                   process_number)
        self.logger = logging.getLogger(self.name)
        self.consumer._process_init(self.name, self.logger)

    def run(self):
        """Consume events from the queue"""
        while True:
            try:
                item = self.queue.get()
                if item == STATUS_DONE:
                    break
                self.consumer.process(*item['args'], **item['kwargs'])
            except Exception as exception:
                self.logger.exception(exception)
                raise

        self.consumer.shutdown()


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


class Queue:
    """A queue with consumers."""

    PROCESS_ALIVE_TIMEOUT = 0.1
    """Time between loops when checking if all processes are done."""

    def __init__(self, consumer, quantity=multiprocessing.cpu_count()):
        self.logger = logging.getLogger(__name__)
        self.consumer = consumer
        self.quantity = quantity
        self.processes = []
        self._queue = multiprocessing.Queue()
        self._active = False

        if isinstance(consumer, type):
            self.init_args = ()
            self.init_kwargs = {}
        else:
            self.consumer = type(consumer)
            self.init_args = consumer.init_args
            self.init_kwargs = consumer.init_kwargs

    def start(self):
        """Start the consumers."""
        if self._active:
            raise QueueError

        self._active = True

        for process_number in range(1, self.quantity + 1):
            process = Process(self, process_number)
            process.start()
            self.processes.append(process)

    def stop(self):
        """Stop the consumers."""
        if not self._active:
            raise QueueError

        self.set_done()

        while True:
            if not any(c.is_alive() for c in self.processes):
                break
            time.sleep(self.PROCESS_ALIVE_TIMEOUT)

        consumer_error = False
        for consumer in self.processes:
            if consumer.exitcode:
                consumer_error = True
                self.logger.error('%s exited with %d', consumer.name,
                                  consumer.exitcode)

        if consumer_error:
            raise ConsumerError

    def __enter__(self):
        """Start the consumers upon entering a runtime context."""
        self.start()
        return self

    def __exit__(self, *args):
        """Cleanup the consumers upon exiting a runtime context."""
        self.stop()

    def get(self):
        """Get an item from the queue."""
        if not self._active:
            raise QueueError

        return self._queue.get(True)

    def put(self, *args, **kwargs):
        """Enqueue a pair `*args` and `**kwargs` to be passed to a consumer's
        :py:method:`consumers.Consumer.process` method.
        """
        if not self._active:
            raise QueueError

        self._queue.put({
            'args': args,
            'kwargs': kwargs})

    def set_done(self):
        """Enqueue a signal to inform consumers that no more data will be added
        to the queue.
        """
        if not self._active:
            raise QueueError

        self._active = False

        for _ in self.processes:
            self._queue.put(STATUS_DONE)
