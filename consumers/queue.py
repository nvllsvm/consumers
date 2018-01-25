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
        consumer = self.queue.consumer(*self.queue.init_args,
                                       **self.queue.init_kwargs)
        consumer._process_init(self.name, self.logger)
        while True:
            try:
                item = self.queue._get()
                if item == STATUS_DONE:
                    break
                consumer.process(*item['args'], **item['kwargs'])
            except Exception as exception:
                self.logger.exception(exception)
                raise
        result = consumer.shutdown()
        self.queue._result_queue.put({'result': result})


class Queue:
    """A queue with consumers.

    Can be used as a context manager to invoke :py:meth:`consumers.Queue.start`
    and :py:meth:`consumers.Queue.stop` at the beginning and end of a context
    respectively.

    :param type,consumers.Consumer consumer:
        The consumer class to use when processing the queue.

        When an instance is passed, any parameters
        passed to the constructor will be passed to the
        :py:meth:`consumer.Consumer.initialize` method when creating the
        consumer processes.

        When a class type is passed, the consumers will be initialized with no
        parameters.

    :param int quantity:
        The number of consumers to create. Defaults to the number of virtual
        CPUs.
    """

    _PROCESS_ALIVE_TIMEOUT = 0.1
    """Time between loops when checking if all processes are done."""

    def __init__(self, consumer, quantity=None):
        self.logger = logging.getLogger(__name__)
        self.quantity = quantity or multiprocessing.cpu_count()
        self.processes = []
        self._queue = multiprocessing.Queue()
        self._result_queue = multiprocessing.Queue()
        self._active = False
        self._results = None

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
        """Start the consumers.

        :raises consumers.QueueError: The consumers have already been started.
        """
        self._assert_active_state(False)
        self._active = True

        self._results = None

        for process_number in range(1, self.quantity + 1):
            process = _Process(self, process_number)
            process.start()
            self.processes.append(process)

    def stop(self):
        """Stop the consumers.

        This method waits for the queue to completely drain before stopping
        the consumers. Any results returned from the consumers will be
        collected and be made available in the queue's
        :py:attr:`consumers.Queue.results` attribute.

        :raises consumers.ConsumerError: An unhandled exception was raised
            in one or more of the consumers while processing.
        :raises consumers.QueueError: The consumers have already been stopped.
        """
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
            time.sleep(self._PROCESS_ALIVE_TIMEOUT)

        self._result_queue.put(STATUS_DONE)
        results = []
        while True:
            item = self._result_queue.get(True)
            if item == STATUS_DONE:
                break
            results.append(item['result'])
        self._results = results

        consumer_error = False
        for consumer in self.processes:
            if consumer.exitcode:
                consumer_error = True
                self.logger.error('%s exited with %d', consumer.name,
                                  consumer.exitcode)

        if consumer_error:
            raise exceptions.ConsumerError

    def __enter__(self):
        """Start the consumers upon entering a runtime context."""
        self.start()
        return self

    def __exit__(self, *args):
        """Cleanup the consumers upon exiting a runtime context."""
        self.stop()

    def _get(self):
        """Get an item from the queue."""
        self._assert_active_state(True)
        return self._queue.get(True)

    def put(self, *args, **kwargs):
        """Enqueue a single item for processing.

        The :py:meth:`consumers.Consumer.process` method will be called with
        any parameters passed to this method.
        """
        self._assert_active_state(True)
        self._queue.put({
            'args': args,
            'kwargs': kwargs})

    @property
    def results(self):
        """Results from the consumers.

        Reset when consumers are started.

        :rtype: list

        :raises consumers.QueueError: Results are not available.
        """
        if self._results is None:
            raise exceptions.QueueError

        return self._results
