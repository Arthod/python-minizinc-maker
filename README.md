# python-minizinc-maker

Create pure Minizinc .mzn files from Python using python-minizinc-maker and the standard minizinc library.

main.py - integer factorization example
```python
model = pymzm.Model()

x = model.add_variable("x", 1, 99999999)
y = model.add_variable("y", 1, 99999999)

model.add_constraint(x * y == 7829 * 6907)
model.add_constraint(y > 1)
model.add_constraint(x > y)

model.set_solve_criteria("satisfy")
model.generate_mzn()
model.write_mzn("model.mzn")
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

But you can also use the minizinc library to solve the model directly.

main.py - integer factorization example
```python
...
import minizinc
gecode = minizinc.Solver.lookup("gecode")
inst = minizinc.Instance(gecode, model)

result = inst.solve(all_solutions=True)
print(f"x = {result[0].x}")  # x = 7829
print(f"y = {result[0].y}")  # y = 6907
```
