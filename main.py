import pymzm
import minizinc

model = pymzm.Model()

xs = model.add_variables("x", range(10), 0, 1, vtype=pymzm.Variable.VTYPE_BOOL)



model.add_constraint(pymzm.Expression.OR(xs[0], xs[1]))

model.set_solve_criteria(pymzm.SOLVE_SATISFY)

model.generate(debug=True)
model.write("_main.mzn")

# Transform Model into a instance
gecode = minizinc.Solver.lookup("gecode")
inst = minizinc.Instance(gecode, model)

# Solve the instance
result = inst.solve(all_solutions=False)
print(result)
