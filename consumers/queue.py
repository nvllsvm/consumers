"""Consumers is a simple, flexible way to parallelize processing."""

import logging
import multiprocessing
import time

from . import exceptions


STATUS_DONE = 'done'
"""Queue item value which informs a consumer it is done"""


class _Process(multiprocessing.Process):
    """Base process class."""

    def __init__(self, queue, process_number):
        super().__init__()
        self.queue = queue
        self.process_number = process_number
        self.name = '{}-{}'.format(self.queue.consumer.__name__,
                                   self.process_number)
        self.logger = logging.getLogger(self.name)

    def run(self):
        """Consume events from the queue"""
        consumer = self.queue.consumer(*self.queue.init_args,
                                       **self.queue.init_kwargs)
        consumer._process_init(self.name, self.logger)
        while True:
            try:
                item = self.queue.get()
                if item == STATUS_DONE:
                    break
                consumer.process(*item['args'], **item['kwargs'])
            except Exception as exception:
                self.logger.exception(exception)
                raise
        consumer.shutdown()


class Queue:
    """A queue with consumers."""

    PROCESS_ALIVE_TIMEOUT = 0.1
    """Time between loops when checking if all processes are done."""

    def __init__(self, consumer, quantity=None, queues=None):
        self.logger = logging.getLogger(__name__)
        self.quantity = quantity or multiprocessing.cpu_count()
        self.processes = []
        self._queue = multiprocessing.Queue()
        self._active = False
        self._queues = queues or ()

        if isinstance(consumer, type):
            self.consumer = consumer
            self.init_args = ()
            self.init_kwargs = {}
        else:
            self.consumer = type(consumer)
            self.init_args = consumer.init_args
            self.init_kwargs = consumer.init_kwargs

    def _assert_active_state(self, state):
        if self._active != state:
            raise exceptions.QueueError

    def start(self):
        """Start the consumers."""
        self._assert_active_state(False)
        self._active = True

        for queue in self._queues:
            try:
                queue.start()
            except exceptions.QueueError:  # queue already running
                pass

        for process_number in range(1, self.quantity + 1):
            process = _Process(self, process_number)
            process.start()
            self.processes.append(process)

    def stop(self):
        """Stop the consumers."""
        self._assert_active_state(True)
        self._set_done()
        self._wait_until_done()

    def _set_done(self):
        """
        Enqueue a signal to inform consumers that no more data will be added
        to the queue.
        """
        self._active = False

        for _ in self.processes:
            self._queue.put(STATUS_DONE)

    def _wait_until_done(self):
        """
        Wait until the queue has been drained and the processes have exited.
        """
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

        for queue in self._queues:
            try:
                queue.stop()
            except exceptions.ConsumerError:
                # raised later so we can ensure all queues get stopped
                consumer_error = True
            except exceptions.QueueError:
                pass

        if consumer_error:
            raise exceptions.ConsumerError

    def __enter__(self):
        """Start the consumers upon entering a runtime context."""
        self.start()
        return self

    def __exit__(self, *args):
        """Cleanup the consumers upon exiting a runtime context."""
        self.stop()

    def get(self):
        """Get an item from the queue."""
        self._assert_active_state(True)
        return self._queue.get(True)

    def put(self, *args, **kwargs):
        """
        Enqueue a pair `*args` and `**kwargs` to be passed to a consumer's
        :py:method:`consumers.Consumer.process` method.
        """
        self._assert_active_state(True)
        self._queue.put({
            'args': args,
            'kwargs': kwargs})
