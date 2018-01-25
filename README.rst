consumers
=========

|Version| |Status| |License|

Consumers is a simple, flexible way to parallelize processing in Python.

Documentation
-------------
https://consumers.readthedocs.io


Example
-------

.. code:: python

    from consumers import Consumer, Queue

    class Concatenator(Consumer):
        def initialize(self):
            self.string = ''

        def process(self, letter:
            self.string += letter

        def shutdown(self):
            return self.string

    with Queue(Concatenator, quantity=2) as queue:
        for i in 'abcdef':
            queue.put(i)

    print(queue.results)

**Output**

::

    ['bce', 'adf']


.. |Version| image:: https://img.shields.io/pypi/v/consumers.svg?
   :target: https://pypi.python.org/pypi/consumers

.. |Status| image:: https://img.shields.io/travis/nvllsvm/consumers.svg?
   :target: https://travis-ci.org/nvllsvm/consumers

.. |License| image:: https://img.shields.io/github/license/nvllsvm/consumers.svg?
   :target: https://github.com/nvllsvm/consumers/blob/master/LICENSE
