import pymzm
import minizinc

model = pymzm.Model()
n = 2
q = model.add_variables("q", range(n), val_min=0, val_max=5)

model.add_constraint(pymzm.Expression.OR(q[0] == (q[1] + 1), q[0] >= q[1]))
model.add_constraint(pymzm.Constraint.all_equal(q))

#model.add_constraint(pymzm.Constraint.alldifferent(q))
#model.add_constraint(pymzm.Constraint.alldifferent([q[i] + i for i in range(n)]))
#model.add_constraint(pymzm.Constraint.alldifferent([q[i] - i for i in range(n)]))

model.set_solve_criteria("satisfy")
model.generate(debug=True)
model.write("_main.mzn")

# Transform Model into a instance
gecode = minizinc.Solver.lookup("gecode")
inst = minizinc.Instance(gecode, model)

# Solve the instance
result = inst.solve(all_solutions=True)
print(result)