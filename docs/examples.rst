Examples
========

First steps
-----------
The job of these consumers are to output their PID and the number they received
from the queue.

.. literalinclude:: ../examples/first_steps.py

The output might look like the following. 
the queue. Notice how ``2`` appears before ``1``.

::

    3320 0
    3320 2
    3321 1
    3323 3
    3324 4


If we run it again, we would expect the PIDs to change. However, the order of
the numbers changed as well. This is normal and inherent to parallel
processing.

::

    3997 0
    3998 1
    3999 2
    3999 4
    4000 3


Consumer lifecycle
------------------
The goal here is to have each consumer create a string of all the letters it
has processed. Unlike the previous example, we now require the consumers to
maintain a state. We also need the ability to access the final state of the
consumers from the main process.

.. literalinclude:: ../examples/init_shutdown.py

Since we specified a ``quantity`` of two consumers, we will get back two
results.

::

    ['bc', 'adef']


Multiple data
-------------
Multiple parameters of data can be passed to the consumers as easily a passing
them to a function. No need to wrap them in an a container object.

.. literalinclude:: ../examples/multiple_data.py

::

    a is at index 0
    c is at index 2
    b is at index 1
    d is at index 3
    e is at index 4
    f is at index 5


Queue orchestration
-------------------
This demonstrates consumers adding items to another queue.

.. literalinclude:: ../examples/queue_orchestration.py

::

    INFO:SquareConsumer-1:Square of 0 is 0
    INFO:SquareConsumer-2:Square of 1 is 1
    INFO:SumConsumer-1:Processing 1
    INFO:SumConsumer-1:Processing 0
    INFO:SquareConsumer-1:Square of 2 is 4
    INFO:SquareConsumer-2:Square of 3 is 9
    INFO:SumConsumer-1:Processing 4
    INFO:SumConsumer-1:Processing 9
    INFO:SquareConsumer-1:Square of 4 is 16
    INFO:SumConsumer-1:Processing 16
    INFO:SumConsumer-1:Sum 30
