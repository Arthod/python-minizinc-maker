
from functools import partial
import pymzm
import minizinc
from model import bin_packing, get_instance

import time

import funcs
import os



# Pymzm time tests:
## Python -> MZN
## MZN -> FZN
## FZN Runtime
## Total

# MZ time tests:
## MZN -> FZN
## FZN Runtime
## Total

def time_diff(funcs):
    time_total = 0
    for func in funcs:
        start_time = time.time()
        func()
        time_total += time.time() - start_time
    return time_total / len(funcs)

if __name__ == "__main__":
    gecode = minizinc.Solver.lookup("gecode")

    p2mzn_list = []
    pmzn2fzn_list = []
    pfzn_list = []
    pfzn_size = []
    pmzn_size = []

    mzn2fzn_list = []
    fzn_list = []
    fzn_size = []
    mzn_size = []

    times = 20

    for n in range(1, 10):
        X = get_instance(n)
        # Py to MZN
        p2mzn_list.append(time_diff([partial(funcs.gen_model, *X) for _ in range(times)]))
        # Py MZN to FZN
        pmzn2fzn_list.append(time_diff([partial(funcs.compile_mzn_to_fzn, "py.mzn") for _ in range(times)]))
        # FZN Runtime
        pfzn_list.append(time_diff([partial(funcs.solve_fzn, "py.fzn") for _ in range(times)]))

        pfzn_size.append(os.path.getsize("py.fzn"))
        pmzn_size.append(os.path.getsize("py.mzn"))

        # MZN -> FZN
        mzn2fzn_list.append(time_diff([partial(funcs.compile_mzn_to_fzn, "M.mzn", X[0], X[0], X[1]) for _ in range(times)]))
        # FZN Runtime
        fzn_list.append(time_diff([partial(funcs.solve_fzn, "M.fzn") for _ in range(times)]))

        fzn_size.append(os.path.getsize("M.fzn"))
        mzn_size.append(os.path.getsize("M.mzn"))


        print(p2mzn_list)
        print(pmzn2fzn_list)
        print(pfzn_list)
        print(pfzn_size)
        print(pmzn_size)

        print(mzn2fzn_list)
        print(fzn_list)
        print(fzn_size)
        print(mzn_size)
        print("--")