from consumers import Consumer, Queue


class ConcatenateConsumer(Consumer):
    def initialize(self):
        self.string = ''

    def process(self, letter):
        self.string += letter

    def shutdown(self):
        return self.string


with Queue(ConcatenateConsumer, quantity=2) as queue:
    for i in 'abcdef':
        queue.put(i)

print(queue.results)
