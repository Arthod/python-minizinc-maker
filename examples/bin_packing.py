
import unittest

import pymzm
import minizinc

# Task 5
# https://imada.sdu.dk/u/march/Teaching/AY2023-2024/DM841/exercises/sheet02


def bin_packing(model: pymzm.Model, solver, cap, sizes):
    n = len(sizes)

    bins_lb = sum(sizes) // cap + 1
    bins_ub = len(sizes)

    bins = model.add_variables("bin", range(bins_ub), val_min=0, val_max=cap)
    items = model.add_variables("item", range(n), val_min=0, val_max=bins_ub - 1) # which bin item items_i goes in to

    for i in range(len(bins)):
        model.add_constraint(bins[i] == pymzm.Expression.sum(pymzm.Expression.ifthenelse(items[j] == i, sizes[j], 0) for j in range(n)))
    model.add_constraint(pymzm.Constraint.decreasing(bins))
    model.add_constraint(bins[0] > 0)

    model.set_solve_criteria(pymzm.SOLVE_MINIMIZE, pymzm.Expression.sum(bins > 0))
    model.generate(debug=False)
    result = minizinc.Instance(gecode, model).solve(all_solutions=False)

    return result

if __name__ == "__main__":
    gecode = minizinc.Solver.lookup("gecode")

    model = pymzm.Model()
    cap = 10
    sizes = [6, 6, 6, 5, 3, 3, 2, 2, 2, 2, 2]
    result = bin_packing(model, gecode, cap, sizes)
    print(result)

    model = pymzm.Model()
    cap = 100
    sizes = [99,98,95,95,95,94,94,91,88,87,86,85,76,74,73,71,68,60,55,54,51,45,42,40,39,39,36,34,33,32,32,31,31,30,29,26,26,23,21,21,21,19,18,18,16,15,5,5,4,1]
    result = bin_packing(model, gecode, cap, sizes)
    print(result)