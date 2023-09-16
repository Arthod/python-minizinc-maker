import pymzm
import minizinc

model = pymzm.Model()
n = 5
q = model.add_variables("q", indices=[(i, j, k) for i in range(10) for j in range(1) for k in range(1)], val_min=0, val_max=5)
#x = model.add_variable("x", val_min=0, val_max=5)

model.add_constraint(abs(q[0, 0, 0] == 5) + (q[0, 0, 0] == 3) >= 1)
#model.add_constraint(pymzm.Constraint.alldifferent([q[i] + i for i in range(n)]))
#model.add_constraint(pymzm.Constraint.alldifferent([q[i] - i for i in range(n)]))

model.set_solve_criteria(pymzm.SOLVE_SATISFY)#pymzm.SOLVE_MAXIMIZE, expr=sum(q[a] for a in q))
model.generate(debug=True)
model.write("_main.mzn")

# Transform Model into a instance
gecode = minizinc.Solver.lookup("gecode")
inst = minizinc.Instance(gecode, model)

# Solve the instance
result = inst.solve(all_solutions=True)
print(result)
print(len(result))