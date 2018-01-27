import functools
import multiprocessing

import pytest

import consumers


def test_consumer_error():
    def failer(items):
        raise ValueError

    pool = consumers.Pool(failer, 1)
    pool.start()
    with pytest.raises(consumers.ConsumerError):
        pool.stop()


def test_results_before_stop():
    with consumers.Pool(lambda x: x, 1) as pool:
        with pytest.raises(consumers.PoolError):
            print(pool.results)


def test_process_name_function():
    def return_name(_):
        return multiprocessing.current_process().name

    pool = consumers.Pool(return_name, 3)
    pool.start()
    pool.stop()

    assert sorted(pool.results) == ['return_name-1',
                                    'return_name-2',
                                    'return_name-3']


def test_process_name_type():
    class ReturnName:
        def __call__(self, items):
            return multiprocessing.current_process().name

    pool = consumers.Pool(ReturnName, 3)
    pool.start()
    pool.stop()

    assert sorted(pool.results) == ['ReturnName-1',
                                    'ReturnName-2',
                                    'ReturnName-3']


def test_items_generator():
    def return_all(items):
        return tuple(items)

    expected = (
        None,
        1,
        ('a', 'b')
    )

    with consumers.Pool(return_all, 1) as pool:
        pool.put()
        pool.put(1)
        pool.put('a', 'b')

    assert pool.results[0] == expected


def test_pool_function():
    def concatenate(items):
        return ''.join(items)

    with consumers.Pool(concatenate, 1) as pool:
        for letter in 'abcd':
            pool.put(letter)

    assert pool.results[0] == 'abcd'


def test_pool_type():
    class Separator:
        def __init__(self, separator):
            self.separator = separator

        def __call__(self, items):
            return self.separator.join(items)

    partial = functools.partial(Separator, '-')
    with consumers.Pool(partial, 1) as pool:
        for letter in 'abcd':
            pool.put(letter)

    assert pool.results[0] == 'a-b-c-d'
