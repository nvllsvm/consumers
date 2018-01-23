from unittest import mock
import logging
import multiprocessing
import time

import pytest

from consumers import consumer, exceptions, queue


class TestInit:

    def test_consumer_instance(self):
        init_args = (1, 2, 3)
        init_kwargs = {'a': 'one',
                       'b': 'two'}
        c = consumer.Consumer(*init_args, **init_kwargs)
        q = queue.Queue(c)

        assert q.consumer == consumer.Consumer
        assert q.init_args == init_args
        assert q.init_kwargs == init_kwargs

    def test_consumer_type(self):
        q = queue.Queue(consumer.Consumer)

        assert q.consumer == consumer.Consumer
        assert q.init_args == ()
        assert q.init_kwargs == {}

    def test_init(self):
        q = queue.Queue(consumer.Consumer)

        assert isinstance(q._queue, multiprocessing.queues.Queue)
        assert q.processes == []
        assert q._active is False
        assert isinstance(q.logger, logging.Logger)
        assert q.logger.name == queue.__name__

    @mock.patch('multiprocessing.cpu_count')
    def test_quantity_default(self, mock_cpu_count):
        mock_cpu_count.return_value = mock.sentinel.cpu_count

        q = queue.Queue(consumer.Consumer)

        assert q.quantity == mock_cpu_count()

    def test_quantity_kwarg(self):
        cpu_count = mock.sentinel.cpu_count
        q = queue.Queue(consumer.Consumer, quantity=cpu_count)

        assert q.quantity == cpu_count

    def test_queues_default(self):
        q = queue.Queue(consumer.Consumer)
        assert q._queues == ()

    def test_queues_kwarg(self):
        q = queue.Queue(consumer.Consumer, queues=[1, 2, 3])
        assert q._queues == [1, 2, 3]


class TestContextManager:

    @mock.patch.object(queue.Queue, 'start')
    @mock.patch.object(queue.Queue, 'stop')
    def test_context_manager(self, mock_stop, mock_start):
        q = queue.Queue(consumer.Consumer)

        mock_start.assert_not_called()
        mock_stop.assert_not_called()

        with q as queue_context:
            assert q == queue_context
            mock_start.assert_called_once_with()
            mock_stop.assert_not_called()

        mock_start.assert_called_once_with()
        mock_stop.assert_called_once_with()


class TestStart:

    @mock.patch.object(queue.Queue, '_assert_active_state')
    @mock.patch.object(queue._Process, 'start')
    def test_queue_already_started(self, _, mock_assert_state):
        q = queue.Queue(consumer.Consumer)

        assert q._active is False
        q.start()
        assert q._active is True
        mock_assert_state.assert_called_once_with(False)

    @mock.patch.object(queue._Process, 'start')
    def test_starts_processes(self, mock_process_start):
        quantity = 4
        q = queue.Queue(consumer.Consumer, quantity=4)
        q.start()

        assert len(q.processes) == quantity
        assert mock_process_start.call_count == quantity
        assert mock_process_start.has_calls(
            [() for _ in range(quantity)], any_order=False)

        for num, process in enumerate(q.processes):
            assert process.queue == q
            assert process.process_number == num + 1

    @mock.patch.object(queue._Process, 'start')
    def test_starts_parent_queues(self, mock_process):
        manager = mock.Mock()
        manager.attach_mock(mock_process, 'process_start')

        queues = []
        for i in range(3):
            pq = queue.Queue(consumer.Consumer)
            pq.start = mock.Mock()
            queues.append(pq)
            manager.attach_mock(pq.start, 'parent{}'.format(i))

        q = queue.Queue(consumer.Consumer, queues=queues, quantity=1)
        q.start()
        q.stop()

        assert manager.mock_calls == [
            mock.call.parent0(),
            mock.call.parent1(),
            mock.call.parent2(),
            mock.call.process_start()]

    @mock.patch.object(queue._Process, 'start')
    def test_starts_parent_queueerror(self, mock_process):
        manager = mock.Mock()
        manager.attach_mock(mock_process, 'process_start')

        pq = queue.Queue(consumer.Consumer)
        pq.start = mock.Mock(side_effect=exceptions.QueueError)
        manager.attach_mock(pq.start, 'parent_start')

        q = queue.Queue(consumer.Consumer, queues=[pq], quantity=1)
        q.start()
        q.stop()

        assert manager.mock_calls == [
            mock.call.parent_start(),
            mock.call.process_start()]

    @mock.patch.object(queue._Process, 'start')
    def test_starts_parent_exception(self, mock_process):
        pq = queue.Queue(consumer.Consumer)
        pq.start = mock.Mock(side_effect=ValueError)

        q = queue.Queue(consumer.Consumer, queues=[pq], quantity=1)

        with pytest.raises(ValueError):
            q.start()

        mock_process.assert_not_called()


class TestStop:

    @mock.patch.object(queue.Queue, '_wait_until_done')
    @mock.patch.object(queue.Queue, '_set_done')
    @mock.patch.object(queue.Queue, '_assert_active_state')
    def test_call_order(self, mock_assert_state, mock_set_done,
                        mock_until_done):
        q = queue.Queue(consumer.Consumer)

        manager = mock.Mock()
        manager.attach_mock(mock_assert_state, '_assert_active_state')
        manager.attach_mock(mock_set_done, '_set_done')
        manager.attach_mock(mock_until_done, '_wait_until_done')

        q.stop()

        assert manager.mock_calls == [
            mock.call._assert_active_state(True),
            mock.call._set_done(),
            mock.call._wait_until_done()]


class TestGet:

    @mock.patch.object(queue.Queue, '_assert_active_state')
    def test_call_order(self, mock_assert_state):
        q = queue.Queue(consumer.Consumer)

        expected = mock.sentinel.queue_get

        q._queue.get = mock.Mock(wraps=q._queue.get)
        q._queue.get.return_value = expected

        manager = mock.Mock()
        manager.attach_mock(mock_assert_state, '_assert_active_state')
        manager.attach_mock(q._queue.get, 'get')

        assert expected == q.get()
        assert manager.mock_calls == [
            mock.call._assert_active_state(True),
            mock.call.get(True)]


class TestPut:

    @mock.patch.object(queue.Queue, '_assert_active_state')
    def test_call_order(self, mock_assert_state):
        q = queue.Queue(consumer.Consumer)

        q._queue.put = mock.Mock(wraps=q._queue.put)
        q._queue.put

        args = (1, 2, 3)
        kwargs = {'a': 'one',
                  'b': 'two'}

        expected = {'args': args,
                    'kwargs': kwargs}

        manager = mock.Mock()
        manager.attach_mock(mock_assert_state, '_assert_active_state')
        manager.attach_mock(q._queue.put, 'put')

        q.put(*args, **kwargs)
        assert manager.mock_calls == [
            mock.call._assert_active_state(True),
            mock.call.put(expected)]


class TestAssertActiveState:

    def test_matches(self):
        q = queue.Queue(consumer.Consumer)
        q._assert_active_state(False)
        q._active = True
        q._assert_active_state(True)

    def test_not_matches(self):
        q = queue.Queue(consumer.Consumer)

        with pytest.raises(exceptions.QueueError):
            q._assert_active_state(True)

        with pytest.raises(exceptions.QueueError):
            q._active = True
            q._assert_active_state(False)


class TestSetDone:

    @mock.patch.object(queue._Process, 'start')
    def test_set_done(self, _):
        quantity = 5
        q = queue.Queue(consumer.Consumer, quantity=quantity)
        q.start()

        assert q._active is True
        q._set_done()

        for _ in range(quantity):
            assert q._queue.get() == queue.STATUS_DONE


class TestWaitUntilDone:

    def test_loops_with_timeout(self):
        consumer_sleep = 0.5

        class TestConsumer(consumer.Consumer):
            def process(self):
                time.sleep(consumer_sleep)

        q = queue.Queue(TestConsumer, quantity=2)
        q.start()

        with mock.patch('time.sleep', wraps=time.sleep) as mock_sleep:
            q.put()
            q.put()
            q._set_done()
            q._wait_until_done()
            for p in q.processes:
                assert not p.is_alive()

        num_calls = len(mock_sleep.mock_calls)
        assert num_calls >= 5
        calls = []
        for i in range(num_calls):
            calls.append(mock.call(0.1))
        mock_sleep.assert_has_calls(calls)

    def test_raises_consumer_error(self):

        class TestConsumer(consumer.Consumer):
            def process(self):
                raise KeyError

        q = queue.Queue(TestConsumer, quantity=1)
        with pytest.raises(exceptions.ConsumerError):
            with q:
                q.put()

    @mock.patch.object(queue._Process, 'is_alive')
    @mock.patch.object(queue._Process, 'start')
    def test_stops_queues(self, mock_start, mock_alive):
        mock_alive.return_value = False

        manager = mock.Mock()
        manager.attach_mock(mock_alive, 'is_alive')

        queues = []
        for i in range(3):
            pq = queue.Queue(consumer.Consumer)
            pq.stop = mock.Mock()
            manager.attach_mock(pq.stop, 'parent{}'.format(i))
            queues.append(pq)

        q = queue.Queue(consumer.Consumer, quantity=1, queues=queues)
        q.start()
        q.stop()

        assert manager.mock_calls == [
            mock.call.is_alive(),
            mock.call.parent0(),
            mock.call.parent1(),
            mock.call.parent2()]

    @mock.patch.object(queue._Process, 'start')
    def test_stops_parent_queueerror(self, _):
        pq = queue.Queue(consumer.Consumer)
        pq.stop = mock.Mock(side_effect=exceptions.QueueError)

        q = queue.Queue(consumer.Consumer, quantity=1, queues=[pq])
        q.start()
        q.stop()

    @mock.patch.object(queue._Process, 'start')
    def test_stops_parent_consumererror(self, _):
        pq = queue.Queue(consumer.Consumer)
        pq.stop = mock.Mock(side_effect=exceptions.ConsumerError)

        q = queue.Queue(consumer.Consumer, quantity=1, queues=[pq])
        q.start()
        with pytest.raises(exceptions.ConsumerError):
            q.stop()
