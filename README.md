# py-minizincmaker

Create pure Minizinc .mzn files from Python using py-minizincmaker library.

main.py
```
model = lib.SDUMZModel()

model.add_variable("x", 1, 99999999)
model.add_variable("y", 1, 99999999)

model.add_constraint(f"x * y = {7829 * 6907}")
model.add_constraint("y > 1")
model.add_constraint("x > y")

model.set_solve_criteria("satisfy")
model.generate()
model.write("model.mzn")
```

model.mzn
```
var 1..99999999: x;
var 1..99999999: y;
constraint x * y = 54074903;
constraint y > 1;
constraint x > y;
solve satisfy;
```
