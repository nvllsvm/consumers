from consumers import Pool


def concatenate(letters):
    return ''.join(letters)


with Pool(concatenate, quantity=2) as pool:
    for letter in 'abcdef':
        pool.put(letter)

print(pool.results)
