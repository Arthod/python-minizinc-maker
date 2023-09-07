import lib
import minizinc


# Create a MiniZinc model
# https://www.minizinc.org/doc-2.5.5/en/modelling.html
model = lib.SDUMZModel()

nc = model.add_constant("nc", value=3)

states = ["wa", "nsw", "nt", "v", "sa", "t", "q"]
for state in states:
    model.add_variable(state, 1, nc.value)

model.add_constraint("wa != nt")
model.add_constraint("wa != sa")
model.add_constraint("nt != sa")
model.add_constraint("nt != q")
model.add_constraint("sa != q")
model.add_constraint("sa != nsw")
model.add_constraint("sa != v")
model.add_constraint("q != nsw")
model.add_constraint("nsw != v")

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