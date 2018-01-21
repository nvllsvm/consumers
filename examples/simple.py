from consumers import Consumer, Queue


class SumConsumer(Consumer):
    def initialize(self):
        self.sum = 0

    def process(self, num):
        self.sum += num

    def shutdown(self):
        print('Sum', self.sum)


with Queue(SumConsumer, quantity=2) as queue:
    for i in range(5):
        queue.put(i)
