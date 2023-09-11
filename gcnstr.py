import pymzm
import minizinc

model = pymzm.Model()

# Create a MiniZinc model
xs = model.add_variables("xs", range(3), val_min=0, val_max=1)
x = model.add_variable("x", 1, 99999999)
y = model.add_variable("y", 1, 99999999)
z = model.add_variable("z", 1, 99999999)

model.add_constraint(x * y == 7829 * 6907)
model.add_constraint(pymzm.Constraint.among(1, [x, y], {6907}))
model.add_constraint(pymzm.Constraint.all_equal([z, y]))
model.add_constraint(pymzm.Constraint.count([x, y], 6907, 1))
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