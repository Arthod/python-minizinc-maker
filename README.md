# pymzm

Model and solve [MiniZinc](https://www.minizinc.org/) constraint problems in Python - no `.mzn` files required.

```python
import pymzm
import minizinc

model = pymzm.Model()
x = model.add_variable("x", val_min=1, val_max=10000)
y = model.add_variable("y", val_min=1, val_max=10000)

model.add_constraint(x * y == 7829 * 6907)
model.add_constraint(x > y)

model.set_solve_criteria(pymzm.SOLVE_SATISFY)

gecode = minizinc.Solver.lookup("gecode")
result = model.solve(solver=gecode)
print(result["x"], result["y"])  # 7829 6907
```

## Install

```
pip install pymzm
```

Requires [MiniZinc](https://www.minizinc.org/software.html) to be installed and on `PATH`.

## Quickstart

### 1. Build a model

```python
model = pymzm.Model()
```

**Add a single variable:**
```python
x = model.add_variable("x", val_min=0, val_max=10)
# float variable
f = model.add_variable("f", vtype=pymzm.Variable.VTYPE_FLOAT, val_min=0.0, val_max=1.0)
# bool variable
b = model.add_variable("b", vtype=pymzm.Variable.VTYPE_BOOL)
```

**Add indexed variables (returns a `ValueDict`):**
```python
xs = model.add_variables("x", indices=range(5), val_min=0, val_max=10)
grid = model.add_variables("cell", indices=[(i, j) for i in range(3) for j in range(3)], val_min=1, val_max=9)

xs[0]          # Variable "x_0"
grid[1, 2]     # Variable "cell_1_2"
```

### 2. Add constraints

```python
model.add_constraint(x + y == 10)
model.add_constraint(x > y)
model.add_constraint(pymzm.Constraint.alldifferent(xs))
```

**Multiple constraints at once:**
```python
model.add_constraints([
    xs[i] + xs[i + 1] <= 5
    for i in range(len(xs) - 1)
])
```

### 3. Set solve criteria

```python
model.set_solve_criteria(pymzm.SOLVE_SATISFY)
model.set_solve_criteria(pymzm.SOLVE_MAXIMIZE, expr=pymzm.Expression.sum(xs))
model.set_solve_criteria(pymzm.SOLVE_MINIMIZE, expr=x)
```

### 4. Solve

```python
gecode = minizinc.Solver.lookup("gecode")

result = model.solve(solver=gecode)
result = model.solve(solver=gecode, all_solutions=True)
result = model.solve(solver=gecode, timeout=datetime.timedelta(seconds=10))
result = model.solve(solver=gecode, threads=4, free_search=True)
```

**Shortcuts:**
```python
result = model.optimize(solver=gecode)           # requires maximize/minimize criteria
is_sat = model.check_satisfiable(solver=gecode)  # returns bool
```

### 5. Read results

```python
# Single solution
result.x          # by variable name (attribute style)
result["x"]       # dict style
result["x_0"]     # indexed variable

# Multiple solutions (all_solutions=True)
result[0].x
result[0, "x_0"]  # index + variable name
len(result)
```

**Status:**
```python
result.status       # minizinc.Status enum
result.statistics   # solver statistics (minizinc.Result.statistics)
```

## Global constraints

```python
pymzm.Constraint.alldifferent(vars)
pymzm.Constraint.among(vars, value, count)
pymzm.Constraint.all_equal(vars)
pymzm.Constraint.count(vars, value, count)
pymzm.Constraint.increasing(vars)
pymzm.Constraint.decreasing(vars)
```

## Expressions

```python
pymzm.Expression.sum(xs)
pymzm.Expression.AND([e1, e2, e3])
pymzm.Expression.OR([e1, e2, e3])
pymzm.Expression.forall(xs, lambda x: x > 0)
pymzm.Expression.exists(xs, lambda x: x == 5)
```

## Constants and parameters

```python
model.add_constant("N", 9)
p = model.add_parameter("capacity", value=100)
```

## Enum domains

```python
color = model.add_enum("Color", ["red", "green", "blue"])
x = model.add_variable("x", domain=color)
```

## Export to .mzn (optional)

```python
model.generate()           # renders the model internally
model.write("model.mzn")   # writes to file for inspection or external use
```

Generate with debug output:
```python
model.generate(debug=True)
```

## Examples

| File | Problem |
|------|---------|
| [examples/intfact.py](examples/intfact.py) | Integer factorization |
| [examples/nqueens.py](examples/nqueens.py) | N-Queens |
| [examples/sudoku.py](examples/sudoku.py) | Sudoku |
| [examples/magicsquare.py](examples/magicsquare.py) | Magic square |
| [examples/bibd.py](examples/bibd.py) | Balanced Incomplete Block Design |
| [examples/sat.py](examples/sat.py) | Boolean satisfiability |

## Compatibility and migration

- [Compatibility policy](docs/compatibility_policy.md)
- [Migration notes](docs/migration_notes.md)
- [Test matrix](docs/test_matrix.md)

