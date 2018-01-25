from consumers import Consumer, Queue


class ConcatenateConsumer(Consumer):
    def process(self, index, letter):
        print('{} is at index {}'.format(letter, index))


with Queue(ConcatenateConsumer, quantity=2) as queue:
    for index, letter in enumerate('abcdef'):
        queue.put(index, letter)
