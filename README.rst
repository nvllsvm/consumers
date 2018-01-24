consumers
=========

|Version| |Status| |License|

Consumers is a simple, flexible way to parallelize processing in Python.

Example
-------

.. code:: python

    from consumers import Consumer, Queue

    class SumConsumer(Consumer):
        def initialize(self):
            self.sum = 0

        def process(self, num):
            self.sum += num

        def shutdown(self):
            return self.sum

    with Queue(SumConsumer) as queue:
        for i in range(5):
            queue.put(i)

    print(queue.results)

A system with two virtual CPUs will have two results.

::

    [4, 6]


Documentation
-------------
https://consumers.readthedocs.io


.. |Version| image:: https://img.shields.io/pypi/v/consumers.svg?
   :target: https://pypi.python.org/pypi/consumers

.. |Status| image:: https://img.shields.io/travis/nvllsvm/consumers.svg?
   :target: https://travis-ci.org/nvllsvm/consumers

.. |License| image:: https://img.shields.io/github/license/nvllsvm/consumers.svg?
   :target: https://github.com/nvllsvm/consumers
