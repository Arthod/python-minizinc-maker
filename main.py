import lib
import minizinc


# Create a MiniZinc model
model = lib.SDUMZModel()

model.add_variable("x", 1, 1000000)
model.add_variable("y", 1, 1000000)

model.add_constraint("x * y = 8633")

model.set_solve_criteria("satisfy")






####
model.generate(debug=True)
#model.write("model.mzn")

# Transform Model into a instance
gecode = minizinc.Solver.lookup("gecode")
inst = minizinc.Instance(gecode, model)

# Solve the instance
result = inst.solve(all_solutions=True)
print(result)
for i in range(len(result)):
    print("x = {}".format(result[i, "x"]))