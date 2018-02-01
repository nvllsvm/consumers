Changelog
=========

Next
----
- Remove ``Pool.start()`` in favor of starting the pool upon Pool
  instantiation.
- Rename ``Pool.stop()`` to ``Pool.join()``
- Add ``Pool.close()`` to drain the queue and shutdown consumer processes in
  the background.
- Add ``Pool.terminate()`` to kill the consumer processes.
- Refactor a few things.

0.4.0 (2018-01-27)
------------------
- Essentially an API rewrite on what consumers are and how they consume.

0.3.0 (2018-01-25)
------------------
- Added queue results.
- Removed mechanism for queues to manage related queues.

0.2.1 (2018-01-23)
------------------
- Fixed consumers being created in the master process before being forked into
  separate processes.

0.2.0 (2018-01-22)
------------------
- Added mechanism for queues to manage related queues.
- Restructured package.

0.1.0 (2018-01-21)
------------------
- Initial release.
