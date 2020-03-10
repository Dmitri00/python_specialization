import sys
import math
def solve_eq(a, b, c):
    """
    >>> solve_eq(0, 0, 0)
    >>> solve_eq(1, -3, -4)
    (4, -1)
    >>> solve_eq(13, 236, -396)
    (1, -19)
    """
    if a == 0:
        if b != 0:
            return int(-c / b)
    else:
        D = b**2 - 4*a*c
        sqrt_D = math.sqrt(D)
        x1 = (-b + sqrt_D) / (2*a)
        x2 = (-b - sqrt_D) / (2*a)
        x1 = int(x1)
        x2 = int(x2)
        return x1, x2

if __name__ == "__main__":
    coefs = list(map(int, sys.argv[1:]))
    roots = solve_eq(coefs[0], coefs[1], coefs[2])

    for root in roots:
        print(root)