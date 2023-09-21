import pymzm
import minizinc

model = pymzm.Model()

# Create a MiniZinc model
n = 8
q = model.add_variables("q", range(n), val_min=0, val_max=n-1)

model.add_constraint(pymzm.Constraint.alldifferent(q))
model.add_constraint(pymzm.Constraint.alldifferent([q[i] + i for i in range(n)]))
model.add_constraint(pymzm.Constraint.alldifferent([q[i] - i for i in range(n)]))

model.set_solve_criteria("satisfy")

####
model.generate(debug=True)
model.write("model.mzn")

# Transform Model into a instance
gecode = minizinc.Solver.lookup("gecode")
inst = minizinc.Instance(gecode, model)

# Solve the instance
result = inst.solve(all_solutions=False)


for i in range(n):
    for j in range(n):
        if (result[f"q_{j}"] == i):
            print("Q", end="")
        else:
            print(".", end="")

        if (j == n - 1):
            print("\n", end="")
        else:
            print("", end="")