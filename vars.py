import pymzm
import minizinc

model = pymzm.Model()

# Create a MiniZinc model
xs = model.add_variables("xs", range(3), val_min=0, val_max=1)


model.set_solve_criteria("satisfy")

####
model.generate_mzn(debug=True)
model.write_mzn("model.mzn")

# Transform Model into a instance
gecode = minizinc.Solver.lookup("gecode")
inst = minizinc.Instance(gecode, model)

# Solve the instance
result = inst.solve(all_solutions=False)

print(result)