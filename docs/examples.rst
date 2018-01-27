Examples
========

Multiple Processes
------------------
Consumers run in separate processes.

.. literalinclude:: ../examples/print_pid_and_num.py

::

    3320 0
    3320 2
    3321 1
    3323 3
    3324 4


Getting Results
---------------
Consumers can return data the end of execution.

.. literalinclude:: ../examples/concatenate.py

::

    ('bc', 'adef')


Multiple Data
-------------
Multiple pieces of data can be queued and consumed with ease.

.. literalinclude:: ../examples/print_index_and_letter.py

::

    a is at index 0
    c is at index 2
    b is at index 1
    d is at index 3
    e is at index 4
    f is at index 5


Consumer Classes
----------------
Callable classes can also be used as consumers.

.. literalinclude:: ../examples/class_tag_and_number.py

::

    first - 0
    first - 1
    first - 2
    second - 0
    second - 1
    second - 2


Cross-Pool Communication
------------------------
Consumers put data into other pools.

.. literalinclude:: ../examples/cross_pool.py

::

    A consumer has finished with a total of 10292214
    A consumer has finished with a total of 10354035
    A consumer has finished with a total of 10416304
    A consumer has finished with a total of 10479197
