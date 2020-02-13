# python3 gen.py N M
# N nodes
# M links

import sys
from random import sample
from math import sqrt, floor

# https://stackoverflow.com/questions/55244113/python-get-random-unique-n-pairs


def decode(i):
    k = floor((1+sqrt(1+8*i))/2)
    return k + 1, i - k*(k-1) // 2 + 1


def get_input(n, m):
    res = "%d\n%d\n" % (n, m)

    for i in sample(range(n*(n-1)//2), m):
        (x, y) = decode(i)
        res += "%d %d\n" % (x, y)

    return res


if __name__ == "__main__":

    N = int(sys.argv[1])
    M = int(sys.argv[2])

    print(get_input(N, M), end="")
