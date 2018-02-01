"""
Consumers
=========
"""

__all__ = [
    'ConsumerError',
    'Pool',
    'PoolError'
]

import multiprocessing
import types


STATUS_DONE = 'done'
"""Queue item value which informs a consumer it is done"""


class _Process(multiprocessing.Process):

    def __init__(self, pool, process_number):
        super().__init__()
        self.pool = pool
        self.process_number = process_number

    def get_item(self):
        while True:
            item = self.pool._input_queue.get()
            if item == STATUS_DONE:
                break

            args = item['args']
            num_args = len(args)
            if num_args == 0:
                yield None
            elif num_args == 1:
                yield args[0]
            else:
                yield args

    def run(self):
        if isinstance(self.pool.consumer, types.FunctionType):
            consumer = self.pool.consumer
            name = consumer.__name__
        else:
            consumer = self.pool.consumer()
            name = type(consumer).__name__

        self.name = '{}-{}'.format(name, self.process_number)

        result = consumer(self.get_item())
        self.pool._result_queue.put({'result': result})


class Pool:
    """
    A :py:class:`Pool` is responsible for the lifecycle of separate consumer
    processes and the queue upon which they consume from.

    When used as a context manager, entering the context returns the pool
    object and exiting invokes its :py:meth:`join` method.

    :param type,types.FunctionType consumer:
        The callable which will consume from the pool's queue.

        If *consumer* is a type, it is instantiated in each of the consumer
        processes with no parameters. The resulting instance is used as the
        callable.

        If *consumer* is a function, it is used as-is.

        Both must be callable with a single generator argument. This generator
        can be used to retreive the next item from the queue. It exhausts only
        after the pool is closed.

    :param int quantity:
        The number of consumer processes to create.

        Defaults to the number of CPUs in the system as determined by
        :py:func:`multiprocessing.cpu_count()`.
    """

    def __init__(self, consumer, quantity=None):
        self.consumer = consumer
        self.quantity = quantity or multiprocessing.cpu_count()

        self._processes = []

        self._active = True
        self._closed = False
        self._terminated = False

        self._input_queue = multiprocessing.Queue()
        self._result_queue = multiprocessing.Queue()
        self._results = None

        for process_number in range(1, self.quantity + 1):
            process = _Process(self, process_number)
            process.start()
            self._processes.append(process)

    def join(self):
        """
        Block until the pool's queue has drained and consumers have stopped.

        Sets :py:attr:`results`.

        :raises consumers.ConsumerError: One or more of the consumers did not
        cleanly exit.
        """
        if self._active:
            self._active = False

            self.close()

            for process in self._processes:
                process.join()
                if process.exitcode:
                    raise ConsumerError

            self._result_queue.put(STATUS_DONE)
            results = []
            while True:
                item = self._result_queue.get()
                if item == STATUS_DONE:
                    break
                results.append(item['result'])
            self._results = tuple(results)

    def close(self):
        """
        Prevent any more items from being added into the pool's queue.
        Consumer processes will exit once the remaining items in the queue
        have been processed.
        """
        if not self._closed:
            self._closed = True
            for _ in self._processes:
                self._input_queue.put(STATUS_DONE)
            self._input_queue.close()

    def terminate(self):
        """Terminate the consumer processes."""
        if self._active:
            self._active = False
            for process in self._processes:
                process.terminate()
            self._terminated = True

    @property
    def results(self):
        """Results from the consumers.

        Only available after :py:meth:`join` has completed.
        Reset upon each :py:meth:`start`.

        :returns:
            A :py:class:`tuple` with a size of as many consumers in the pool.

        :raises consumers.PoolError: Results are not available at this time.
        """
        if self._results is None:
            raise PoolError
        return self._results

    def put(self, *args):
        """Enqueue all `\*args` as a single item in the queue."""
        if self._closed or not self._active:
            raise PoolError
        self._input_queue.put({'args': args})

    def __enter__(self):
        """Start the consumers upon entering a runtime context."""
        return self

    def __exit__(self, *args):
        """Cleanup the consumers upon exiting a runtime context."""
        self.join()


class ConsumerError(Exception):
    """An exception in a consumer occurred."""


class PoolError(Exception):
    """An error occurred accessing a pool."""
