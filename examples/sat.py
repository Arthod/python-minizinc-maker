
import minizinc
import pymzm

model = pymzm.Model()

xs = model.add_variables("x", indices=range(4), vtype=pymzm.Variable.VTYPE_BOOL)
model.add_constraint(pymzm.Expression.AND([
    xs[0] | xs[1] | ~xs[2],
    xs[1] | xs[2] | ~xs[3],
    xs[0] | ~xs[1] | xs[3],
]))
model.set_solve_criteria(pymzm.SOLVE_SATISFY)

gecode = minizinc.Solver.lookup("gecode")
result = model.solve(solver=gecode, all_solutions=False)

for i in range(4):
    print(f"x_{i} = {result[f'x_{i}']}")