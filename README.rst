consumers
=========

|Version| |Status| |License|

Consumers is a simple, flexible way to parallelize processing in Python.

Examples
--------

Distributing work accross separate consumer instances.

.. code:: python

    from consumers import Consumer, Queue


    class SumConsumer(Consumer):
        def initialize(self):
            self.sum = 0

        def process(self, num):
            self.sum += num

        def shutdown(self):
            print('Sum', self.sum)


    with Queue(SumConsumer) as queue:
        for i in range(5):
            queue.put(i)


A system with two virtual CPUs will output two results.

::

    Sum 4
    Sum 6


Orchestration
^^^^^^^^^^^^^

Orchestrating multiple types of consumers to achieve a single solution.

.. code:: python

    import logging

    from consumers import Consumer, Queue

    logging.basicConfig(level=logging.INFO)


    class SquareConsumer(Consumer):
        def initialize(self, sum_queue):
            self.sum_queue = sum_queue

        def process(self, num):
            square = num * num
            self.logger.info('Square of %d is %d', num, square)
            self.sum_queue.put(square)


    class SumConsumer(Consumer):
        def initialize(self):
            self.sum = 0

        def process(self, num):
            self.logger.info('Processing %s', num)
            self.sum += num

        def shutdown(self):
            self.logger.info('Sum %d', self.sum)


    sum_queue = Queue(SumConsumer, quantity=1)
    square_queue = Queue(SquareConsumer(sum_queue), queues=[sum_queue])

    with square_queue:
        for i in range(5):
            square_queue.put(i)


A system with two virtual CPUs will output log entries for two instances of
``SquareConsumer`` and one instance of ``SumConsumer``.

::

    INFO:SquareConsumer-2:Square of 1 is 1
    INFO:SumConsumer-1:Processing 0
    INFO:SumConsumer-1:Processing 1
    INFO:SquareConsumer-1:Square of 2 is 4
    INFO:SquareConsumer-2:Square of 3 is 9
    INFO:SumConsumer-1:Processing 4
    INFO:SumConsumer-1:Processing 9
    INFO:SquareConsumer-1:Square of 4 is 16
    INFO:SumConsumer-1:Processing 16
    INFO:SumConsumer-1:Sum 30


.. |Version| image:: https://img.shields.io/pypi/v/consumers.svg?
   :target: https://pypi.python.org/pypi/consumers

.. |Status| image:: https://img.shields.io/travis/nvllsvm/consumers.svg?
   :target: https://travis-ci.org/nvllsvm/consumers

.. |License| image:: https://img.shields.io/github/license/nvllsvm/consumers.svg?
   :target: https://github.com/nvllsvm/consumers
