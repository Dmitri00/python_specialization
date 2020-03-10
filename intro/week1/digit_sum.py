import sys
def count_digits(num):
    """
    >>> count_digits("012345")
    15
    >>> count_digits("")
    0
    >>> count_digits("1.1")
    2
    >>> count_digits("1a.2b")
    3
    """
    str_digits = filter(lambda x: x.isdigit(), num)
    return sum(map(int, str_digits))

if __name__ == "__main__":
    num = sys.argv[1]
    digit_sum = count_digits(num)
    print(digit_sum)
        