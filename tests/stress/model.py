import random

import minizinc
import pymzm


def get_instance(n, seed=5):
    random.seed(seed)
    cap = n
    sizes = [random.randint(1, n) for _ in range(n)]
    random.seed(None)

    return cap, sizes

def bin_packing(model: pymzm.Model, solver, cap, sizes):
    n = len(sizes)

    bins_lb = sum(sizes) // cap + 1
    bins_ub = len(sizes)

    bin_loads = model.add_variables("bin_load", range(bins_ub), val_min=0, val_max=cap)
    model.add_constraint(pymzm.Constraint.decreasing(bin_loads))
    model.add_constraint(bin_loads[0] > 0)

    # Boolean if bin i has item j
    bin_items = model.add_variables("bin_item", [(i, j) for i in range(bins_ub) for j in range(n)], vtype=pymzm.Variable.VTYPE_BOOL)
    for i in range(len(bin_loads)):
        model.add_constraint(bin_loads[i] == pymzm.Expression.sum(bin_items[i, j] * sizes[j] for j in range(n)))
    for j in range(n):
        model.add_constraint(pymzm.Expression.sum(bin_items[i, j] for i in range(len(bin_loads))) == 1)

    # Solve
    model.set_solve_criteria(pymzm.SOLVE_MINIMIZE, pymzm.Expression.sum(bin_loads > 0))
    model.generate(debug=False)
    model.write("out.mzn")
    result = minizinc.Instance(solver, model).solve(all_solutions=False)

    return result