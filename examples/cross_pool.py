from consumers import Pool


def square_sums(numbers, logger_pool):
    total = 0
    for number in numbers:
        total += number * number
    logger_pool.put(total)


def logger(totals):
    for total in totals:
        print('A consumer has finished with a total of', total)


logger_pool = Pool(logger, 1)
square_sums_pool = Pool(square_sums, args=(logger_pool,))

with logger_pool, square_sums_pool:
    for i in range(500):
        square_sums_pool.put(i)
