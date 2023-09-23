import pymzm
import minizinc

def pr711(model, solver, n):
    items = model.add_variables("item", range(n), val_min=0, val_max=999)
    model.add_constraint(pymzm.Expression.sum(items) == 711)
    model.add_constraint(pymzm.Expression.product(items) == 711 * 100 * 100 * 100)

    model.set_solve_criteria(pymzm.SOLVE_SATISFY)
    model.generate()
    
    result = minizinc.Instance(solver, model).solve(all_solutions=False)

    return result


if __name__ == "__main__":
    n = 4
    gecode = minizinc.Solver.lookup("gecode")
    model = pymzm.Model()
    
    result = pr711(model, gecode, n)
    print(result)