# python-minizinc-maker

Create pure Minizinc .mzn files from Python using python-minizinc-maker and [minizinc-python](https://github.com/MiniZinc/minizinc-python).


## Model
Model: `model = pymzm.Model()` \
Variable: `x = model.add_variable(name, vtype, val_min, val_max)` \
Variables: `xs = model.add_variables(name, indicies, vtype, val_min, val_max)` \
Constraint: `model.add_constraint(expr)`\
Solve: `model.set_solve_criteria(solve_criteria, expr)`

### Global constraints
alldifferent, among, all_equal, count, increasing, decreasing, ..(more to be added later)..

### Solve
* model.set_solve_criteria(pymzm.SOLVE_MAXIMIZE, pymzm.Expression.sum(xs))
* model.set_solve_criteria(pymzm.SOLVE_SATISFY)

### 

## Examples
### intfact.py - Integer Factorization example
intfact.py
```python
import pymzm
model = pymzm.Model()

x = model.add_variable("x", val_min=1, val_max=99999999)
y = model.add_variable("y", val_min=1, val_max=99999999)

model.add_constraint(x * y == 7829 * 6907)
model.add_constraint(y > 1)
model.add_constraint(x > y)

model.set_solve_criteria(pymzm.SOLVE_SATISFY)
model.generate()
model.write("model.mzn")
...
```

model.mzn
```mzn
var 1..99999999: x;
var 1..99999999: y;
constraint x * y = 54074903;
constraint y > 1;
constraint x > y;
solve satisfy;
```

Now you can use the minizinc library to solve the model directly.

intfact.py
```python
...
import minizinc
gecode = minizinc.Solver.lookup("gecode")
result = minizinc.Instance(gecode, model).solve(all_solutions=True)
print(f"x = {result[0].x}")  # x = 7829
print(f"y = {result[0].y}")  # y = 6907
```

### bibd.py - Balanced Incomplete Block Design
https://www.csplib.org/Problems/prob028/
```python
v = 7; b = 7; r = 3; k = 3; l = 1

model = pymzm.Model()

indicies = [(i, j) for i in range(v) for j in range(b)]
# bool if object v is in block b
xs = model.add_variables("x", indices=indicies, vtype=pymzm.Variable.VTYPE_BOOL)

for i in range(b):
    model.add_constraint(pymzm.Expression.sum(xs[i, j] for j in range(v)) == r)
for i in range(v):
    model.add_constraint(pymzm.Expression.sum(xs[j, i] for j in range(b)) == k)

for i in range(b):
    for j in range(i):
        model.add_constraint(pymzm.Expression.sum(xs[i, k] * xs[j, k] for k in range(v)) == l)

model.set_solve_criteria(pymzm.SOLVE_SATISFY)
model.generate()

gecode = minizinc.Solver.lookup("gecode")
result = minizinc.Instance(gecode, model).solve(all_solutions=False)

for i in range(v):
    print(" ".join([str(int(result[f"x_{i}_{j}"])) for j in range(b)]))
```
outputs
```
0 0 1 0 0 1 1
0 1 0 0 1 1 0
1 0 0 1 0 1 0
0 0 1 1 1 0 0
0 1 0 1 0 0 1
1 1 1 0 0 0 0
1 0 0 0 1 0 1
```

### sat.py - Satisfiability
```python
model = pymzm.Model()

xs = model.add_variables("x", indices=range(4), vtype=pymzm.Variable.VTYPE_BOOL)
model.add_constraint(pymzm.Expression.AND([
    xs[0] | xs[1] | ~xs[2],
    xs[1] | xs[2] | ~xs[3],
    xs[0] | ~xs[1] | xs[3],
]))
model.set_solve_criteria(pymzm.SOLVE_SATISFY)
model.generate()

gecode = minizinc.Solver.lookup("gecode")
result = minizinc.Instance(gecode, model).solve(all_solutions=False)

for i in range(4):
    print(f"x_{i} = {result[f'x_{i}']}")
```
