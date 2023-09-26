
from functools import partial
import pymzm
import minizinc
from model import bin_packing, get_instance

import time

# Pymzm time tests:
## Python -> MZN
## MZN -> FZN
## FZN Runtime
## Total

# MZ time tests:
## MZN -> FZN
## FZN Runtime
## Total

def time_diff(func):
    start_time = time.time()
    func()
    return time.time() - start_time

if __name__ == "__main__":
    gecode = minizinc.Solver.lookup("gecode")

    i = 1
    while True:
        model = pymzm.Model()
        result = bin_packing(model, gecode, *get_instance(i))
        print(i, len(model.model_mzn_str), result.objective)
        i += 1