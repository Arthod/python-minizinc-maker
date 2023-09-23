import minizinc
import pymzm

# Task 3
# https://imada.sdu.dk/u/march/Teaching/AY2023-2024/DM841/exercises/sheet02

guests \
    = [bride, groom, bestman, bridesmaid, bob, carol, ted, alice, ron, rona, ed, clara] \
    = ["bride", "groom", "bestman", "bridesmaid", "bob", "carol", "ted", "alice", "ron", "rona", "ed", "clara"]
hatreds = [(groom, clara), (carol, bestman), (ed, ted), (bride, alice), (ted, ron)]
males = [groom, bestman, bob, ted, ron, ed]
females = [bride, bridesmaid, carol, alice, rona, clara]


model = pymzm.Model()

seats = model.add_variables("seat", guests, vtype=pymzm.Variable.VTYPE_INTEGER, val_min=0, val_max=11)

# Cannot sit on same seat
model.add_constraint(pymzm.Constraint.alldifferent(seats))

# Males sit on odd numbered seats and females sit on even numbered seats
model.add_constraints(seats[male] % 2 == 1 for male in males)
model.add_constraints(seats[female] % 2 == 0 for female in females)

# Ed cannot sit at the end of the table
model.add_constraint(pymzm.Expression.AND([seats[ed] != 0, seats[ed] != 5, seats[ed] != 6, seats[ed] != 11]))

# The bride and groom must sit next to eachother
model.add_constraint((abs(seats[groom] - seats[bride]) == 1) & (pymzm.Expression.iff([seats[groom] <= 5, seats[bride] <= 5])))

model.set_solve_criteria(pymzm.SOLVE_MAXIMIZE, )
model.generate(debug=True)

gecode = minizinc.Solver.lookup("gecode")
result = minizinc.Instance(gecode, model).solve(all_solutions=False)

print(result)