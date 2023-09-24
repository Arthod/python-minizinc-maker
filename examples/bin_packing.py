
import unittest

import pymzm
import minizinc

# Task 5
# https://imada.sdu.dk/u/march/Teaching/AY2023-2024/DM841/exercises/sheet02


def bin_packing(model: pymzm.Model, solver, cap, sizes):
    n = len(sizes)

    bins_lb = sum(sizes) // cap + 1
    bins_ub = len(sizes)

    bin_loads = model.add_variables("bin_load", range(bins_ub), val_min=0, val_max=cap)
    model.add_constraint(pymzm.Constraint.decreasing(bin_loads))
    model.add_constraint(bin_loads[0] > 0)

    # Formulation 1
    #items = model.add_variables("item", range(n), val_min=0, val_max=bins_ub - 1) # which bin item items_i goes in to

    #for i in range(len(bin_loads)):
    #    model.add_constraint(bin_loads[i] == pymzm.Expression.sum(pymzm.Expression.ifthenelse(items[j] == i, sizes[j], 0) for j in range(n)))
    
    # Formulation 2
    # Boolean if bin i has item j
    bin_items = model.add_variables("bin_item", [(i, j) for i in range(bins_ub) for j in range(n)], vtype=pymzm.Variable.VTYPE_BOOL)
    for i in range(len(bin_loads)):
        model.add_constraint(bin_loads[i] == pymzm.Expression.sum(bin_items[i, j] * sizes[j] for j in range(n)))

    # Solve
    model.set_solve_criteria(pymzm.SOLVE_MINIMIZE, pymzm.Expression.sum(bin_loads > 0))
    model.generate(debug=False)
    model.write("out.mzn")
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