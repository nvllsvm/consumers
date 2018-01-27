import functools

from consumers import Pool


class PrintTag:
    def __init__(self, tag):
        self.tag = tag

    def __call__(self, items):
        for number in items:
            print('{} - {}'.format(self.tag, number))


for run in ('first', 'second'):
    partial = functools.partial(PrintTag, run)
    with Pool(partial, 1) as pool:
        for i in range(3):
            pool.put(i)
