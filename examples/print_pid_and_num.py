import os

from consumers import Pool


def printer(numbers):
    pid = os.getpid()
    for number in numbers:
        print(pid, number)


pool = Pool(printer)

for number in range(5):
    pool.put(number)

pool.join()
