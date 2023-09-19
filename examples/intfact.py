import pymzm
model = pymzm.Model()

x = model.add_variable("x", 1, 99999999)
y = model.add_variable("y", 1, 99999999)

model.add_constraint(x * y == 7829 * 6907)
model.add_constraint(y > 1)
model.add_constraint(x > y)

model.set_solve_criteria(pymzm.SOLVE_SATISFY)
model.generate()
model.write("model.mzn")

import minizinc
gecode = minizinc.Solver.lookup("gecode")
result = minizinc.Instance(gecode, model).solve(all_solutions=True)
print(f"x = {result[0].x}")  # x = 7829
print(f"y = {result[0].y}")  # y = 6907