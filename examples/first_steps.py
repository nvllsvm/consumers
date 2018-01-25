import os
from consumers import Consumer, Queue


class PrintConsumer(Consumer):
    def process(self, num):
        print(os.getpid(), num)


with Queue(PrintConsumer) as queue:
    for i in range(5):
        queue.put(i)
