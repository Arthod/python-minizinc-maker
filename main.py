import pymzm
import minizinc

model = pymzm.Model()

# Create a MiniZinc model
X = model.add_variables(range(0, 5), "X", 1, 5)


model.add_constraint(sum(X) == 5)
model.add_constraint(X[0] > X[1])

model.set_solve_criteria("satisfy")

####
model.generate(debug=True)
model.write("model.mzn")

# Transform Model into a instance
gecode = minizinc.Solver.lookup("gecode")
inst = minizinc.Instance(gecode, model)

# Solve the instance
result = inst.solve(all_solutions=False)
