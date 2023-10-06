import pymzm
import minizinc

model = pymzm.Model()

xs = model.add_variables("x", range(10), vtype=pymzm.Variable.VTYPE_INTEGER, val_min=1, val_max=10)

model.add_constraint(pymzm.Constraint.alldifferent(xs))
model.set_solve_criteria(pymzm.SOLVE_SATISFY)
model.set_solve_method(pymzm.IntSearch(xs, pymzm.AnnotationVariableChoice.VARCHOICE_FIRST_FAIL, pymzm.AnnotationValueChoice.VALCHOICE_INDOMAIN_MIN))

model.generate(debug=True)
model.write("out.mzn")

gecode = minizinc.Solver.lookup("gecode")
result = minizinc.Instance(gecode, model).solve(all_solutions=False)
print(result)
