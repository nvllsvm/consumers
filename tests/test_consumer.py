from unittest import mock

import pytest

import consumers


class TestConsumer:

    def test_init(self):
        init_args = (1, 2, 3)
        init_kwargs = {'a': 'one',
                       'b': 'two'}
        c = consumers.Consumer(*init_args, **init_kwargs)

        assert c.init_args == init_args
        assert c.init_kwargs == init_kwargs

    def test_init_no_args_nor_kwargs(self):
        c = consumers.Consumer()

        assert c.init_args == ()
        assert c.init_kwargs == {}

    @mock.patch.object(consumers.Consumer, 'initialize')
    def test_process_init(self, mock_initialize):
        init_args = (1, 2, 3)
        init_kwargs = {'a': 'one',
                       'b': 'two'}

        c = consumers.Consumer(*init_args, **init_kwargs)

        name = mock.sentinel.name
        logger = mock.sentinel.logger

        c._process_init(name, logger)

        assert c.name == name
        assert c.logger == logger
        mock_initialize.assert_called_once_with(*init_args, **init_kwargs)

    def test_process(self):
        c = consumers.Consumer()
        with pytest.raises(NotImplementedError):
            c.process()

    def test_initialize(self):
        c = consumers.Consumer()
        c.initialize()

    def test_shutdown(self):
        c = consumers.Consumer()
        c.shutdown()
