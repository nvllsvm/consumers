from consumers import Pool


def print_host(numbers, host, port=80):
    connection = '{}:{}'.format(host, port)

    for number in numbers:
        print(connection, number)


with Pool(print_host, 1, args=('remote',)) as pool:
    for i in range(3):
        pool.put(i)

with Pool(print_host, 1, args=('local',), kwargs={'port': 8123}) as pool:
    for i in range(3):
        pool.put(i)
