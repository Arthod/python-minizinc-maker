import lib
import minizinc

model = lib.SDUMZModel()

# Create a MiniZinc model
n = 5
q = model.add_variables(range(1, n+1), "q", 1, n)

model.add_constraint(lib.Constraint.alldifferent(q))
model.add_constraint(lib.Constraint.alldifferent([q[i] + i for i in range(1, n+1)]))
model.add_constraint(lib.Constraint.alldifferent([q[i] - i for i in range(1, n+1)]))

model.set_solve_criteria("satisfy")

####
model.generate(debug=True)
model.write("model.mzn")

# Transform Model into a instance
gecode = minizinc.Solver.lookup("gecode")
inst = minizinc.Instance(gecode, model)

# Solve the instance
result = inst.solve(all_solutions=False)

if (len(result)):
    print(result)