import pymzm
import minizinc

model = pymzm.Model()
n = 5
q = model.add_variables("q", range(n), val_min=0, val_max=5)

model.add_constraint(3 == q[0])
#model.add_constraint(pymzm.Constraint.alldifferent(q))
#model.add_constraint(pymzm.Constraint.alldifferent([q[i] + i for i in range(n)]))
#model.add_constraint(pymzm.Constraint.alldifferent([q[i] - i for i in range(n)]))

model.set_solve_criteria("satisfy")
model.generate()
model.write("_main.mzn")

# Transform Model into a instance
#gecode = minizinc.Solver.lookup("gecode")
#inst = minizinc.Instance(gecode, model)

# Solve the instance
#result = inst.solve(all_solutions=True)
#print(len(result))