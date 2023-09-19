import pymzm
import minizinc

model = pymzm.Model()

xs = model.add_variables("x", range(10), vtype=pymzm.Variable.VTYPE_BOOL)
ys = model.add_variables("y", range(10), vtype=pymzm.Variable.VTYPE_INTEGER, val_min=0, val_max=10)

model.add_constraint(pymzm.Expression.AND(~xs))
for i in range(10):
    model.add_constraint(ys[i] >= i)
model.add_constraint(xs[0] ^ xs[2] | xs[3] & xs[4] | xs[5] ^ (~xs[0]))

model.set_solve_criteria(pymzm.SOLVE_MAXIMIZE, sum(xs))

model.generate()

gecode = minizinc.Solver.lookup("gecode")
result = minizinc.Instance(gecode, model).solve(all_solutions=False)
print(result)
