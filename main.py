import pymzm
import minizinc

model = pymzm.Model()

# Create a MiniZinc model
x = model.add_variable("x", 1, 9)
y = model.add_variable("y", 1, 9)
z = model.add_variable("z", 1, 9)
w = model.add_variable("w", 1, 9)
j = model.add_variable("j", 1, 9)
k = model.add_variable("k", 1, 9)
X = model.add_variable("X", 1, 922)

model.add_constraint(x + y - j // k >= z - w)
model.add_constraint(X == x + y)


model.set_solve_criteria("satisfy")

####
model.generate_mzn(debug=False)
model.write_mzn("main.mzn")
model.generate_fzn(debug=True)
model.write_fzn("main.fzn")

# Transform Model into a instance
#gecode = minizinc.Solver.lookup("gecode")
#minizinc.Instance
#inst = minizinc.Instance(gecode, model)

# Solve the instance
#result = inst.solve(all_solutions=False)

#print(result)