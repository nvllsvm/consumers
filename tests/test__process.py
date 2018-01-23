from unittest import mock
import logging
import multiprocessing

import pytest

from consumers import consumer, queue


class TestInit:

    def test_init(self):
        process_number = 4

        class TestConsumer(consumer.Consumer):
            pass

        q = queue.Queue(TestConsumer)

        p = queue._Process(q, process_number)

        assert isinstance(p, multiprocessing.Process)

        assert p.queue == q
        assert p.process_number == process_number
        assert p.name == 'TestConsumer-4'
        assert type(p.logger) == logging.Logger
        assert p.logger.name == p.name


class TestRun:

    @mock.patch.object(consumer.Consumer, 'shutdown')
    @mock.patch.object(consumer.Consumer, 'process')
    @mock.patch.object(consumer.Consumer, '_process_init')
    @mock.patch.object(queue.Queue, 'get')
    def test_calls(self, mock_get, mock_process_init, mock_process,
                   mock_shutdown):
        manager = mock.Mock()
        manager.attach_mock(mock_get, 'get')
        manager.attach_mock(mock_process_init, 'process_init')
        manager.attach_mock(mock_process, 'process')
        manager.attach_mock(mock_shutdown, 'shutdown')

        args = (1, 2, 3)
        kwargs = {'a': 'one',
                  'b': 'two'}

        q = queue.Queue(consumer.Consumer(*args, **kwargs), quantity=1)

        manager.get.side_effect = [
            {'args': (1, 2), 'kwargs': {'a': 'b', 'c': 'd'}},
            {'args': (3, 4), 'kwargs': {'e': 'f', 'g': 'h'}},
            queue.STATUS_DONE
        ]

        p = queue._Process(q, 1)
        p.run()

        mock_process_init.assert_called_once_with(p.name, p.logger)

        assert manager.mock_calls == [
            mock.call.process_init(p.name, p.logger),
            mock.call.get(),
            mock.call.process(1, 2, a='b', c='d'),
            mock.call.get(),
            mock.call.process(3, 4, e='f', g='h'),
            mock.call.get(),
            mock.call.shutdown()
        ]

    @mock.patch.object(consumer.Consumer, 'shutdown')
    @mock.patch.object(consumer.Consumer, 'process')
    @mock.patch.object(queue.Queue, 'get')
    def test_exception(self, mock_get, mock_process, mock_shutdown):
        q = queue.Queue(consumer.Consumer)
        p = queue._Process(q, 1)
        mock_logger_exception = mock.Mock()
        p.logger.exception = mock_logger_exception

        mock_get.return_value = {'args': (1, 2), 'kwargs': {'a': 'b'}}

        manager = mock.Mock()
        manager.attach_mock(mock_get, 'get')
        manager.attach_mock(mock_process, 'process')
        manager.attach_mock(mock_shutdown, 'shutdown')
        manager.attach_mock(mock_logger_exception, 'logger_exception')

        exception = Exception
        exception_instance = exception()
        mock_process.side_effect = exception_instance
        with pytest.raises(exception):
            p.run()

        assert manager.mock_calls == [
            mock.call.get(),
            mock.call.process(1, 2, a='b'),
            mock.call.logger_exception(exception_instance)]
        mock_shutdown.assert_not_called()
