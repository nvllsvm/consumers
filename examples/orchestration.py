import logging

from consumers import Consumer, Queue

logging.basicConfig(level=logging.INFO)


class SquareConsumer(Consumer):
    def initialize(self, sum_queue):
        self.sum_queue = sum_queue

    def process(self, num):
        square = num * num
        self.logger.info('Square of %d is %d', num, square)
        self.sum_queue.put(square)


class SumConsumer(Consumer):
    def initialize(self):
        self.sum = 0

    def process(self, num):
        self.logger.info('Processing %s', num)
        self.sum += num

    def shutdown(self):
        self.logger.info('Sum %d', self.sum)


sum_queue = Queue(SumConsumer, quantity=1)
square_queue = Queue(SquareConsumer(sum_queue), queues=[sum_queue])

with square_queue:
    for i in range(5):
        square_queue.put(i)
