import pymzm
import minizinc

def intfact(model, solver, n1, n2):
    x = model.add_variable("x", val_min=1, val_max=99999999)
    y = model.add_variable("y", val_min=1, val_max=99999999)

    model.add_constraint(x * y == n1 * n2)
    model.add_constraint(y > 1)
    model.add_constraint(x > y)

    model.set_solve_criteria(pymzm.SOLVE_SATISFY)
    model.generate()

    result = minizinc.Instance(solver, model).solve(all_solutions=True)

    return result

if __name__ == "__main__":
    model = pymzm.Model()
    gecode = minizinc.Solver.lookup("gecode")
    result = intfact(model, gecode, 7829, 6907)
    
    print(f"x = {result[0].x}")  # x = 7829
    print(f"y = {result[0].y}")  # y = 6907