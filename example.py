import logging

import consumers

logging.basicConfig(level=logging.INFO)


class MyConsumer(consumers.Consumer):
    def initialize(self):
        self.sum = 0

    def process(self, num):
        self.logger.info('Processing %s', num)
        self.sum += num

    def shutdown(self):
        self.logger.info('Sum %d', self.sum)


with consumers.Queue(MyConsumer) as queue:
    for i in range(5):
        queue.put(i)
