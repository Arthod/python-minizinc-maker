import pymzm
import minizinc

model = pymzm.Model()

# Parameters
# BIBD generation is described in most standard textbooks on combinatorics. 
# A BIBD is defined as an arrangement of v  distinct objects into b blocks 
# such that each block contains exactly k distinct objects, each object 
# occurs in exactly r different blocks, and every two distinct objects 
# occur together in exactly λ blocks.
v = 7
b = 7
r = 3
k = 3
l = 1

# Create a MiniZinc model
xs = model.add_variables("x", indices=[(i, j) for i in range(v) for j in range(b)], vtype=pymzm.Variable.VTYPE_BOOL, val_min=0, val_max=1) # bool if object v is in block b

for i in range(b):
    model.add_constraint(sum(xs[i, j] for j in range(v)) == r)
for i in range(v):
    model.add_constraint(sum(xs[j, i] for j in range(b)) == k)

for i in range(b):
    for j in range(i):
        model.add_constraint(sum(xs[i, k] * xs[j, k] for k in range(v)) == l)

model.set_solve_criteria("satisfy")

####
model.generate_mzn(debug=True)
model.write_mzn("model.mzn")

# Transform Model into a instance
gecode = minizinc.Solver.lookup("gecode")
inst = minizinc.Instance(gecode, model)

# Solve the instance
result = inst.solve(all_solutions=False)

for i in range(v):
    print(" ".join([str(result[f"x_{i}_{j}"]) for j in range(b)]))