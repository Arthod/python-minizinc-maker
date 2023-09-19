import pymzm
import minizinc

model = pymzm.Model()

xs = model.add_variables("x", range(10), vtype=pymzm.Variable.VTYPE_BOOL)
ys = model.add_variables("y", range(10), val_min=0, val_max=10, vtype=pymzm.Variable.VTYPE_INTEGER)

print(xs[0] * (xs[1] + xs[2] + xs[3]))

model.add_constraint(pymzm.Expression.AND(~xs))
for i in range(10):
    model.add_constraint(ys[i] >= i)
model.add_constraint(xs[0] ^ xs[2] | xs[3] & xs[4] | xs[5] ^ (~xs[0]))

model.set_solve_criteria(pymzm.SOLVE_MAXIMIZE, sum(xs) - sum(ys))

model.generate(debug=True)
model.write("_main.mzn")

# Transform Model into a instance
gecode = minizinc.Solver.lookup("gecode")
inst = minizinc.Instance(gecode, model)

# Solve the instance
result = inst.solve(all_solutions=False)
print(result)
