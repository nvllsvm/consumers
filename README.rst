consumers
=========

.. image:: https://img.shields.io/pypi/v/consumers.svg
    :target: https://pypi.python.org/pypi/consumers

.. image:: https://img.shields.io/pypi/l/consumers.svg
    :target: https://pypi.python.org/pypi/consumers

Consumers is a simple, flexible way to parallelize processing in Python.

Example
-------

.. code:: python

    import logging

    import consumers

    logging.basicConfig(level=logging.INFO)


    class MyConsumer(consumers.Consumer):
        def initialize(self):
            self.sum = 0

        def process_item(self, num):
            self.logger.info('Processing %s', num)
            self.sum += num

        def finish(self):
            self.logger.info('Sum %d', self.sum)


    with consumers.Queue(MyConsumer) as queue:
        for i in range(5):
            queue.put(i)


::

    INFO:MyConsumer-1:Processing 0
    INFO:MyConsumer-2:Processing 1
    INFO:MyConsumer-1:Processing 2
    INFO:MyConsumer-2:Processing 3
    INFO:MyConsumer-1:Processing 4
    INFO:MyConsumer-2:Sum 4
    INFO:MyConsumer-1:Sum 6
