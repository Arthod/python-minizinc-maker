import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "\\..\\..")

import pymzm
import minizinc
from examples.bin_packing import bin_packing
import random

def get_instance(n, seed=5):
    random.seed(seed)
    cap = n
    sizes = [random.randint(1, n) for _ in range(n)]
    random.seed(None)

    return cap, sizes

if __name__ == "__main__":
    gecode = minizinc.Solver.lookup("gecode")

    i = 1
    while True:
        cap, sizes = get_instance(i)
        model = pymzm.Model()
        result = bin_packing(model, gecode, cap, sizes)
        print(result)
        i += 1