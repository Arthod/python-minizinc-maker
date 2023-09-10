import pymzm
import minizinc

model = pymzm.Model()

# Create a MiniZinc model
x = model.add_variable("x", 1, 9)
y = model.add_variable("y", 1, 9)


model.add_constraint(abs(x)**2 / y == 2)
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

