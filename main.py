import pymzm
import minizinc

model = pymzm.Model()

# Create a MiniZinc model
x = model.add_variable("x", 1, 99999999)
y = model.add_variable("y", 1, 99999999)

model.add_constraint(x * y == 7829 * 6907)
model.add_constraint(pymzm.Constraint.among(1, [x, y], {6907}))
model.add_constraint(y > 1)
model.add_constraint(x > y)
model.set_solve_criteria("satisfy")

####
model.generate(debug=True)
model.write("model.mzn")

# Transform Model into a instance
gecode = minizinc.Solver.lookup("gecode")
inst = minizinc.Instance(gecode, model)

# Solve the instance
result = inst.solve(all_solutions=False)

print(result)