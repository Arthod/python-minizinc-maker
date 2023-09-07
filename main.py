import lib
import minizinc


# Create a MiniZinc model
model = lib.SDUMZModel()

model.add_variable("x", 1, 99999999)
model.add_variable("y", 1, 99999999)

model.add_constraint(f"x * y = {7829 * 6907}")
model.add_constraint("y > 1")
model.add_constraint("x > y")

model.set_solve_criteria("satisfy")






####
model.generate(debug=True)
model.write("model.mzn")

# Transform Model into a instance
gecode = minizinc.Solver.lookup("gecode")
inst = minizinc.Instance(gecode, model)

# Solve the instance
result = inst.solve(all_solutions=True)
print(result)
for i in range(len(result)):
    print("x = {}".format(result[i, "x"]))