import os

from consumers import Pool


def printer(numbers):
    pid = os.getpid()
    for number in numbers:
        print(pid, number)


pool = Pool(printer)
pool.start()

for number in range(5):
    pool.put(number)

pool.stop()
