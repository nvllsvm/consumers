Examples
========

Multiple Processes
------------------
Consumers run in separate processes.

.. literalinclude:: ../examples/print_pid_and_num.py

.. code-block:: none

    3320 0
    3320 2
    3321 1
    3323 3
    3324 4


Getting Results
---------------
Consumers can return data the end of execution.

.. literalinclude:: ../examples/concatenate.py

.. code-block:: none

    ('b-c', 'a-d-e-f')


Multiple Data
-------------
Multiple pieces of data can be queued and consumed with ease.

.. literalinclude:: ../examples/print_index_and_letter.py

.. code-block:: none

    a is at index 0
    c is at index 2
    b is at index 1
    d is at index 3
    e is at index 4
    f is at index 5


Consumer Configuration
----------------------
Consumers can be configured with positional and keyword arguments.

.. literalinclude:: ../examples/consumer_config.py

.. code-block:: none

    remote:80 0
    remote:80 1
    remote:80 2
    local:8123 0
    local:8123 1
    local:8123 2


Cross-Pool Communication
------------------------
Consumers can put data into other pools.

.. literalinclude:: ../examples/cross_pool.py

.. code-block:: none

    A consumer has finished with a total of 10292214
    A consumer has finished with a total of 10354035
    A consumer has finished with a total of 10416304
    A consumer has finished with a total of 10479197
