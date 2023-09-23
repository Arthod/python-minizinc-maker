import pymzm
import minizinc

# Task 4
# https://imada.sdu.dk/u/march/Teaching/AY2023-2024/DM841/exercises/sheet02

def nqueens(model, solver, n):
    q = model.add_variables("q", range(n), val_min=0, val_max=n-1)

    model.add_constraint(pymzm.Constraint.alldifferent(q))
    model.add_constraint(pymzm.Constraint.alldifferent([q[i] + i for i in range(n)]))
    model.add_constraint(pymzm.Constraint.alldifferent([q[i] - i for i in range(n)]))

    model.set_solve_criteria("satisfy")
    model.generate()

    results = minizinc.Instance(solver, model).solve(all_solutions=True)

    return results


if __name__ == "__main__":
    n = 8
    gecode = minizinc.Solver.lookup("gecode")
    model = pymzm.Model()
    results = nqueens(model, gecode, n)

    for i in range(n):
        for j in range(n):
            if (results[0, f"q_{j}"] == i):
                print("Q", end="")
            else:
                print(".", end="")

            if (j == n - 1):
                print("\n", end="")
            else:
                print("", end="")