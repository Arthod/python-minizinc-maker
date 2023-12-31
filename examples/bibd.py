import pymzm
import minizinc

# Parameters
# BIBD generation is described in most standard textbooks on combinatorics. 
# A BIBD is defined as an arrangement of v  distinct objects into b blocks 
# such that each block contains exactly k distinct objects, each object 
# occurs in exactly r different blocks, and every two distinct objects 
# occur together in exactly λ blocks.

def bibd(model, solver, v, b, r, k, l):
    indicies = [(i, j) for i in range(v) for j in range(b)]
    xs = model.add_variables("x", indices=indicies, vtype=pymzm.Variable.VTYPE_BOOL) # bool if object v is in block b

    for i in range(b):
        model.add_constraint(pymzm.Expression.sum(xs[i, j] for j in range(v)) == r)
    for i in range(v):
        model.add_constraint(pymzm.Expression.sum(xs[j, i] for j in range(b)) == k)

    for i in range(b):
        for j in range(i):
            model.add_constraint(pymzm.Expression.sum(xs[i, k] * xs[j, k] for k in range(v)) == l)

    model.set_solve_criteria(pymzm.SOLVE_SATISFY)
    model.generate()
    
    result = minizinc.Instance(solver, model).solve(all_solutions=False)

    return result

if __name__ == "__main__":
    model = pymzm.Model()
    gecode = minizinc.Solver.lookup("gecode")
    
    v = 7; b = 7; r = 3; k = 3; l = 1
    result = bibd(model, gecode, v, b, r, k, l)


    for i in range(v):
        print(" ".join([str(int(result[f"x_{i}_{j}"])) for j in range(b)]))