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

    from consumers import Pool


    def concatenate(letters):
        return ''.join(letters)


    with Pool(concatenate, 2) as pool:
        for letter in 'abcdef':
            pool.put(letter)

    print(pool.results)

::

    ('bdf', 'ace')

.. |Version| image:: https://img.shields.io/pypi/v/consumers.svg?
   :target: https://pypi.python.org/pypi/consumers

.. |Status| image:: https://img.shields.io/travis/nvllsvm/consumers.svg?
   :target: https://travis-ci.org/nvllsvm/consumers

.. |License| image:: https://img.shields.io/github/license/nvllsvm/consumers.svg?
   :target: https://github.com/nvllsvm/consumers/blob/master/LICENSE
