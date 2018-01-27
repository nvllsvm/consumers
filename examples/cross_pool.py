import functools

from consumers import Pool


class SquareSums:
    def __init__(self, logger_pool):
        self.logger_pool = logger_pool

    def __call__(self, numbers):
        total = 0
        for number in numbers:
            total += number * number
        self.logger_pool.put(total)


def logger(totals):
    for total in totals:
        print('A consumer has finished with a total of', total)


logger_pool = Pool(logger, 1)

partial = functools.partial(SquareSums, logger_pool)
square_sums_pool = Pool(partial)

with logger_pool, square_sums_pool:
    for i in range(500):
        square_sums_pool.put(i)
