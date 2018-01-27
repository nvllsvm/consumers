from consumers import Pool


def print_letter_index(items):
    for index, letter in items:
        print('{} is at index {}'.format(letter, index))


with Pool(print_letter_index) as pool:
    for i, v in enumerate('abcdef'):
        pool.put(i, v)
