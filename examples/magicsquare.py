import pymzm
import minizinc

def magicsquare(model, solver, n):
    xs = model.add_variables("x", [(i, j) for i in range(n) for j in range(n)], val_min=1, val_max=n * n)
    y = model.add_variable("y", val_min=0, val_max=50000)

    model.add_constraint(pymzm.Constraint.alldifferent(xs))

    # Two main diagonals
    model.add_constraint(pymzm.Expression.sum([xs[i, i] for i in range(n)]) == y)
    model.add_constraint(pymzm.Expression.sum([xs[i, n - 1 - i] for i in range(n)]) == y)

    # Rows and columns are equal
    for i in range(n):
        model.add_constraint(pymzm.Expression.sum([xs[i, j] for j in range(n)]) == y)
    for j in range(n):
        model.add_constraint(pymzm.Expression.sum([xs[i, j] for i in range(n)]) == y)


    model.set_solve_criteria(pymzm.SOLVE_SATISFY)
    model.generate(debug=False)


    result = minizinc.Instance(solver, model).solve(all_solutions=False)

    return result

if __name__ == "__main__":
    n = 3
    model = pymzm.Model()
    gecode = minizinc.Solver.lookup("gecode")
    result = magicsquare(model, gecode, n)

    for i in range(n):
        print(" ".join([str(result[f"x_{i}_{j}"]) for j in range(n)]))
    print(f"y = {result[f'y']}")