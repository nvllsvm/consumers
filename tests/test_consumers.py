import functools
import multiprocessing

import pytest

import consumers


def test_consumer_error():
    def failer(items):
        raise ValueError

    pool = consumers.Pool(failer, 1)
    with pytest.raises(consumers.ConsumerError):
        pool.join()


def test_results_before_join():
    with consumers.Pool(lambda x: x, 1) as pool:
        with pytest.raises(consumers.PoolError):
            print(pool.results)


def test_process_name():
    def return_name(_):
        return multiprocessing.current_process().name

    pool = consumers.Pool(return_name, 3)
    pool.join()

    assert sorted(pool.results) == ['return_name-1',
                                    'return_name-2',
                                    'return_name-3']


def test_process_name_default():
    def return_name(_):
        return multiprocessing.current_process().name

    # partials do not have __name__
    func = functools.partial(return_name)

    pool = consumers.Pool(func, 3)
    pool.join()

    assert sorted(pool.results) == ['Consumer-1',
                                    'Consumer-2',
                                    'Consumer-3']


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


def test_pool():
    def concatenate(items):
        return ''.join(items)

    with consumers.Pool(concatenate, 1) as pool:
        for letter in 'abcd':
            pool.put(letter)

    assert pool.results[0] == 'abcd'


def test_pool_args_kwargs():
    def concatenate(items, a, b, c, d):
        data = [str(v) for v in (a, b, c, d)]
        data.extend(items)
        return ''.join(data)

    args = (1, 2)
    kwargs = {'c': 3, 'd': 4}
    with consumers.Pool(concatenate, 1, args=args, kwargs=kwargs) as pool:
        for letter in 'abcd':
            pool.put(letter)

    assert pool.results[0] == '1234abcd'


def test_pool_close():
    def dummy(items):
        pass

    pool = consumers.Pool(dummy, 1)
    pool.put(1)
    pool.close()

    with pytest.raises(consumers.PoolError):
        pool.put(1)


def test_pool_close_idempotent():
    def dummy(items):
        pass

    pool = consumers.Pool(dummy, 1)
    pool.put(1)

    pool.close()
    pool.close()
    pool.close()


def test_pool_join_idempotent():
    def dummy(items):
        pass

    pool = consumers.Pool(dummy, 1)
    pool.put(1)

    pool.join()
    pool.join()
    pool.join()


def test_pool_terminate_idempotent():
    def dummy(items):
        pass

    pool = consumers.Pool(dummy, 1)
    pool.put(1)

    pool.terminate()
    pool.terminate()
    pool.terminate()
