import pymzm
import minizinc
model = pymzm.Model()

n = 3
N = n * n
xs = model.add_variables("x", [(i, j) for i in range(N) for j in range(N)], val_min=1, val_max=N)

# Small squares alldifferent
for i in range(n):
    for j in range(n):
        model.add_constraint(pymzm.Constraint.alldifferent([xs[i * 3 + kx, j * 3 + ky] for kx in range(n) for ky in range(n)]))

for i in range(N):
    model.add_constraint(pymzm.Constraint.alldifferent([xs[i, j] for j in range(N)]))
for j in range(N):
    model.add_constraint(pymzm.Constraint.alldifferent([xs[i, j] for i in range(N)]))

_ = 0
sod = [
    [_, 4, 3, _, 8, _, 2, 5, _],
    [6, _, _, _, _, _, _, _, _],
    [_, _, _, _, _, 1, _, 9, 4],
    [9, _, _, _, _, 4, _, 7, _],
    [_, _, _, 6, _, 8, _, _, _],
    [_, 1, _, 2, _, _, _, _, 3],
    [8, 2, _, 5, _, _, _, _, _],
    [_, _, _, _, _, _, _, _, 5],
    [_, 3, 4, _, 9, _, 7, 1, _],
]
for i in range(N):
    for j in range(N):
        if (sod[i][j] == _):
            continue
        model.add_constraint(xs[i, j] == sod[i][j])

model.set_solve_criteria(pymzm.SOLVE_SATISFY)
model.generate(debug=True)


gecode = minizinc.Solver.lookup("gecode")
result = minizinc.Instance(gecode, model).solve(all_solutions=False)

for i in range(N):
    print(" ".join([str(result[f"x_{i}_{j}"]) for j in range(N)]))