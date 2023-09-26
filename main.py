import pymzm
import minizinc

model = pymzm.Model()

xs = model.add_variables("x", range(10), vtype=pymzm.Variable.VTYPE_INTEGER, val_min=0, val_max=2)

model.add_constraint(pymzm.Constraint.alldifferent([x - 3 for x in xs]))
model.set_solve_criteria(pymzm.SOLVE_SATISFY)

model.generate(debug=True)
model.write("out.mzn")

gecode = minizinc.Solver.lookup("gecode")
result = minizinc.Instance(gecode, model).solve(all_solutions=False)
print(result)
