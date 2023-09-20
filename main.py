import pymzm
import minizinc

model = pymzm.Model()

xs = model.add_variables("x", range(10), vtype=pymzm.Variable.VTYPE_BOOL)
print(pymzm.Expression.sum([xs[0] * 2, xs[1], xs[2]]) == 0)

model.set_solve_criteria(pymzm.SOLVE_MAXIMIZE, sum(xs))

model.generate(debug=True)

gecode = minizinc.Solver.lookup("gecode")
result = minizinc.Instance(gecode, model).solve(all_solutions=False)
print(result)
