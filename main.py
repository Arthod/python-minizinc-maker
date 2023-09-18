import pymzm
import minizinc

model = pymzm.Model()

xs = model.add_variables("x", range(10), 0, 1, vtype=pymzm.Variable.VTYPE_BOOL)


print(~ xs[2])
#model.add_constraint(pymzm.Expression.AND((~xs[a]) for a in xs))
model.add_constraint(xs[0] ^ xs[2] | xs[3] & xs[4] | xs[5] ^ (~xs[0]))

model.set_solve_criteria(pymzm.SOLVE_MAXIMIZE, sum(xs[a] for a in xs))

model.generate(debug=True)
model.write("_main.mzn")

# Transform Model into a instance
gecode = minizinc.Solver.lookup("gecode")
inst = minizinc.Instance(gecode, model)

# Solve the instance
result = inst.solve(all_solutions=False)
print(result)
