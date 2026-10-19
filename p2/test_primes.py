# test_primality.py

import random
from sympy import isprime

from p2 import SNPM


def test_randomized_primality():
    tester = SNPM("a", "b")

    false_negatives = []
    false_positives = []

    LIMIT = 1000000
    K = 10

    for n in range(2, LIMIT):

        expected = isprime(n)
        actual = tester.randomized_primality(n, K)

        # prime labeled composite
        if expected and not actual:
            false_negatives.append(n)

        # composite labeled prime
        if not expected and actual:
            false_positives.append(n)

    print("\nFalse negatives:", false_negatives[:20])
    print("False positives:", false_positives[:20])

    assert len(false_negatives) == 0, \
        f"Missed primes: {false_negatives[:10]}"

    assert len(false_positives) == 0, \
        f"Composite labeled prime: {false_positives[:10]}"