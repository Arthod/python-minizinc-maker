import lib


# Create a MiniZinc model
model = lib.SDULibModel()
#model.add_string("""
#var -100..100: x;
#int: a; int: b; int: c;
#constraint a*(x*x) + b*x = c;
#solve satisfy;
#""")
model.add_variable(lib.Variable("x", -100, 100))

model.add_constant(lib.Constant("a"))
model.add_constant(lib.Constant("b"))
model.add_constant(lib.Constant("c"))

model.add_constraint(lib.Constraint("a*(x*x) + b*x = c"))

model.set_solve_method("satisfy")

# Transform Model into a instance
gecode = lib.SDULibModel.Solver.lookup("gecode")
inst = lib.SDULibModel.Instance(gecode, model)
inst["a"] = 1
inst["b"] = 4
inst["c"] = 0

# Solve the instance
result = inst.solve(all_solutions=True)
for i in range(len(result)):
    print("x = {}".format(result[i, "x"]))